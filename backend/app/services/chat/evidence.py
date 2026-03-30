from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

from ... import rag_config


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _normalize_score(raw: Any) -> float:
    try:
        score = float(raw)
    except (TypeError, ValueError):
        return 0.0
    if score <= 0.0:
        return 0.0
    if score <= 1.0:
        return score
    if score <= 100.0:
        return score / 100.0
    return 1.0


def _iter_scores(results: Iterable[Dict[str, Any]], sources: Iterable[Dict[str, Any]]) -> List[float]:
    values: List[float] = []
    for item in results or []:
        for key in ("combined_score", "dense_score", "score"):
            if key in item:
                values.append(_normalize_score(item.get(key)))
                break
    for src in sources or []:
        if "score" in src:
            values.append(_normalize_score(src.get("score")))
    return [v for v in values if v > 0.0]


def _count_unique_sources(results: Iterable[Dict[str, Any]], sources: Iterable[Dict[str, Any]]) -> int:
    seen = set()
    for item in results or []:
        payload = item.get("payload", {}) if isinstance(item, dict) else {}
        path = str(payload.get("file_path") or payload.get("source_file") or "").strip().lower()
        if path:
            seen.add(path)
    for src in sources or []:
        path = str(src.get("file_path") or "").strip().lower()
        if path:
            seen.add(path)
    return len(seen)


def compute_evidence_score(results: List[Dict[str, Any]], sources: List[Dict[str, Any]]) -> float:
    scores = sorted(_iter_scores(results, sources), reverse=True)
    score_component = (sum(scores[:3]) / min(3, len(scores))) if scores else 0.0
    result_count_component = _clamp01(len(results or []) / 4.0)
    unique_source_component = _clamp01(_count_unique_sources(results, sources) / 3.0)
    score = (
        0.60 * score_component
        + 0.25 * result_count_component
        + 0.15 * unique_source_component
    )
    return _clamp01(round(score, 4))


def build_evidence_gate(
    results: List[Dict[str, Any]],
    sources: List[Dict[str, Any]],
) -> Dict[str, Any]:
    threshold = _clamp01(rag_config.evidence_threshold())
    policy = rag_config.evidence_policy()
    score = compute_evidence_score(results, sources)
    passed = score >= threshold
    return {
        "score": score,
        "threshold": threshold,
        "policy": policy,
        "passed": passed,
        "action": "direct" if passed else policy,
        "result_count": len(results or []),
        "source_count": len(sources or []),
        "unique_source_count": _count_unique_sources(results, sources),
    }


def apply_evidence_policy(answer: str, evidence_gate: Dict[str, Any]) -> Tuple[str, Dict[str, Any] | None]:
    if bool(evidence_gate.get("passed")):
        return answer, None

    score = float(evidence_gate.get("score") or 0.0)
    threshold = float(evidence_gate.get("threshold") or 0.0)
    policy = str(evidence_gate.get("policy") or "ask").strip().lower()

    if policy == "reject":
        return "", {
            "status_code": 422,
            "code": "INSUFFICIENT_EVIDENCE",
            "message": (
                f"Insufficient evidence to answer confidently "
                f"(score={score:.2f}, threshold={threshold:.2f})."
            ),
        }

    if policy == "constrained" and answer:
        disclaimer = "Limited evidence: this answer may be incomplete or uncertain."
        return f"{disclaimer}\n\n{answer}", None

    clarification = (
        "I don't have enough evidence to answer confidently yet. "
        "Could you clarify the request or share more relevant project context?"
    )
    return clarification, None

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


def _payload_text(payload: Dict[str, Any]) -> str:
    return str(payload.get("text") or payload.get("preview_text") or "").strip()


def _source_key(payload: Dict[str, Any]) -> str:
    return str(
        payload.get("file_path")
        or payload.get("source_file")
        or payload.get("document_id")
        or ""
    ).strip().lower()


def _anchor_key(payload: Dict[str, Any]) -> str:
    source_key = _source_key(payload)
    if not source_key:
        return ""
    line_start = payload.get("line_start")
    line_end = payload.get("line_end")
    if line_start is not None or line_end is not None:
        return f"{source_key}::{line_start or ''}-{line_end or ''}"
    section_path = str(payload.get("section_path") or payload.get("paragraph_range") or "").strip().lower()
    if section_path:
        return f"{source_key}::{section_path}"
    return source_key


def _is_anchorable_payload(payload: Dict[str, Any]) -> bool:
    text = _payload_text(payload)
    if not text:
        return False
    if _source_key(payload):
        return True
    return bool(payload.get("line_start") is not None or payload.get("line_end") is not None)


def _score_from_result(item: Dict[str, Any]) -> float:
    for key in ("combined_score", "dense_score", "score"):
        if key in item:
            return _normalize_score(item.get(key))
    return 0.0


def _score_from_source(item: Dict[str, Any]) -> float:
    return _normalize_score(item.get("score"))


def _collect_result_evidence(results: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen = set()
    for item in results or []:
        payload = dict(item.get("payload", {}) or {})
        anchor_key = _anchor_key(payload)
        if anchor_key and anchor_key in seen:
            continue
        if anchor_key:
            seen.add(anchor_key)
        rows.append(
            {
                "score": _score_from_result(item),
                "anchorable": _is_anchorable_payload(payload),
                "source_key": _source_key(payload),
                "anchor_key": anchor_key,
            }
        )
    return rows


def _collect_source_evidence(sources: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen = set()
    for item in sources or []:
        payload = dict(item or {})
        anchor_key = _anchor_key(payload)
        if anchor_key and anchor_key in seen:
            continue
        if anchor_key:
            seen.add(anchor_key)
        rows.append(
            {
                "score": _score_from_source(payload),
                "anchorable": _is_anchorable_payload(payload),
                "source_key": _source_key(payload),
                "anchor_key": anchor_key,
            }
        )
    return rows


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
    rows = _collect_result_evidence(results) or _collect_source_evidence(sources)
    anchor_rows = [row for row in rows if bool(row.get("anchorable"))]
    anchor_scores = sorted((float(row.get("score") or 0.0) for row in anchor_rows), reverse=True)

    if not anchor_scores:
        fallback = max((float(row.get("score") or 0.0) for row in rows), default=0.0)
        return _clamp01(round(0.20 * fallback, 4))

    anchor_score = anchor_scores[0]
    supporting_anchor_score = anchor_scores[1] if len(anchor_scores) > 1 else (anchor_score * 0.5)
    distinct_anchor_sources = {
        str(row.get("source_key") or "").strip().lower()
        for row in anchor_rows
        if str(row.get("source_key") or "").strip()
    }
    source_support = 1.0 if len(distinct_anchor_sources) >= 2 else 0.5
    score = (
        0.80 * anchor_score
        + 0.15 * supporting_anchor_score
        + 0.05 * source_support
    )
    return _clamp01(round(score, 4))


def build_evidence_gate(
    results: List[Dict[str, Any]],
    sources: List[Dict[str, Any]],
) -> Dict[str, Any]:
    threshold = _clamp01(rag_config.evidence_threshold())
    policy = rag_config.evidence_policy()
    rows = _collect_result_evidence(results) or _collect_source_evidence(sources)
    anchor_rows = [row for row in rows if bool(row.get("anchorable"))]
    anchor_scores = sorted((float(row.get("score") or 0.0) for row in anchor_rows), reverse=True)
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
        "anchor_count": len(anchor_rows),
        "best_anchor_score": round(anchor_scores[0], 4) if anchor_scores else 0.0,
        "supporting_anchor_score": round(anchor_scores[1], 4) if len(anchor_scores) > 1 else 0.0,
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

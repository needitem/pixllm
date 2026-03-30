from dataclasses import dataclass
from typing import Optional

from .... import rag_config


@dataclass
class RoutingProbeScores:
    docs_score: float = 0.0
    code_score: float = 0.0


@dataclass
class RoutingDecision:
    mode: str
    default_mode: str
    docs_primary: bool
    used_probe: bool
    reason: str


@dataclass
class RetrievalQuality:
    low_quality: bool
    reason: str
    total_results: int
    doc_results: int
    code_results: int


def normalize_mode(value: str) -> str:
    mode = str(value or "").strip().lower()
    if mode in {"docs", "code"}:
        return mode
    return ""


def _code_first_types() -> set:
    return set(rag_config.routing_code_first_response_types())


def _doc_first_types() -> set:
    return set(rag_config.routing_doc_first_response_types())


def default_mode_for_response_type(response_type: str) -> str:
    rt = str(response_type or "").strip().lower()
    if rt in _code_first_types():
        return "code"
    if rt in _doc_first_types():
        return "docs"
    return "code"


def _probe_conflict_cutoff(threshold: float) -> float:
    return min(0.92, max(0.0, float(threshold)) + 0.15)


def _should_probe(default_mode: str, confidence: float, threshold: float, target_mode: str) -> bool:
    if not rag_config.routing_probe_enabled():
        return False
    if confidence < threshold:
        return True
    if not target_mode:
        return False
    if default_mode == target_mode:
        return False
    return confidence < _probe_conflict_cutoff(threshold)


def _mode_from_probe(scores: RoutingProbeScores, default_mode: str) -> str:
    docs = max(0.0, float(scores.docs_score or 0.0))
    code = max(0.0, float(scores.code_score or 0.0))
    ratio = max(1.01, float(rag_config.routing_probe_ratio()))

    if docs <= 0 and code <= 0:
        return default_mode

    if docs >= code * ratio:
        return "docs"
    if code >= docs * ratio:
        return "code"
    return default_mode if default_mode in {"docs", "code"} else "code"


def _apply_mode_guards(*, response_type: str, default_mode: str, chosen_mode: str, reason: str) -> tuple[str, str]:
    rt = str(response_type or "").strip().lower()
    chosen = normalize_mode(chosen_mode) or default_mode
    why = reason

    # Keep explicit doc lookup on document retrieval.
    if rt == "doc_lookup" and chosen != "docs":
        return "docs", f"{why}_doc_lookup_guard"

    # For docs-first intents, prevent code-only mode.
    if default_mode == "docs" and chosen == "code":
        return "docs", f"{why}_doc_lookup_guard"

    return chosen, why


def arbitrate_tool_mode(
    *,
    response_type: str,
    confidence: float,
    threshold: float,
    target_mode: str = "",
    probe_scores: Optional[RoutingProbeScores] = None,
) -> RoutingDecision:
    default_mode = default_mode_for_response_type(response_type)
    docs_primary = default_mode == "docs"
    normalized_target = normalize_mode(target_mode)
    chosen = normalized_target or default_mode
    used_probe = False
    reason = "default"

    if _should_probe(default_mode, confidence, threshold, normalized_target):
        if probe_scores is not None:
            chosen = _mode_from_probe(probe_scores, default_mode)
            used_probe = True
            reason = "probe"
        else:
            chosen = default_mode
            reason = "low_confidence_default"
    elif normalized_target:
        chosen = normalized_target
        reason = "classifier_target_mode"

    chosen, reason = _apply_mode_guards(
        response_type=response_type,
        default_mode=default_mode,
        chosen_mode=chosen,
        reason=reason,
    )

    return RoutingDecision(
        mode=chosen,
        default_mode=default_mode,
        docs_primary=docs_primary,
        used_probe=used_probe,
        reason=reason,
    )


def assess_retrieval_quality(*, response_type: str, total_results: int, doc_results: int, current_top_k: int) -> RetrievalQuality:
    total = max(0, int(total_results))
    docs = max(0, int(doc_results))
    code = max(0, total - docs)
    rt = str(response_type or "").strip().lower()

    reason = ""
    _ = current_top_k
    if total == 0:
        reason = "no_results"
    elif rt in {"api_lookup", "doc_lookup"} and docs == 0:
        reason = "doc_evidence_missing"
    elif rt in {"code_explain", "bug_fix", "code_review", "usage_guide"} and code == 0:
        reason = "code_evidence_missing"

    return RetrievalQuality(
        low_quality=bool(reason),
        reason=reason,
        total_results=total,
        doc_results=docs,
        code_results=code,
    )


def next_refinement_mode(*, current_mode: str, response_type: str, reason: str) -> str:
    mode = normalize_mode(current_mode) or default_mode_for_response_type(response_type)
    rt = str(response_type or "").strip().lower()
    why = str(reason or "").strip().lower()

    if rt == "doc_lookup":
        return "docs"
    if why == "doc_evidence_missing":
        return "docs"
    if why == "code_evidence_missing":
        return "code"
    return mode

from dataclasses import dataclass
from typing import Optional

from ... import rag_config


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
def _apply_mode_guards(*, response_type: str, default_mode: str, chosen_mode: str, reason: str) -> tuple[str, str]:
    rt = str(response_type or "").strip().lower()
    chosen = normalize_mode(chosen_mode) or default_mode
    why = reason

    if rt == "doc_lookup" and chosen != "docs":
        return "docs", f"{why}_doc_lookup_guard"

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
    _ = confidence
    _ = threshold
    _ = probe_scores
    reason = "classifier_target_mode" if normalized_target else "default"

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
    elif rt in {"code_explain", "bug_fix", "code_review"} and code == 0:
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

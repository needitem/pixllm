from typing import Any, Dict, List

from .question_contract import normalize_question_contract


def _intent_family(response_type: str, question_contract: Dict[str, Any]) -> str:
    contract_kind = str(dict(question_contract or {}).get("kind") or "").strip().lower()
    contract_mode = str(dict(question_contract or {}).get("retrieval_mode") or "").strip().lower()
    if contract_kind == "doc_reference" or contract_mode == "docs":
        return "document"
    if contract_kind in {"code_change", "code_flow_explanation", "code_read", "code_review", "failure_analysis", "code_compare"} or contract_mode in {"code", "hybrid"}:
        return "code"
    return "general"


def _classification_stability(intent_source: str, intent_confidence: float) -> str:
    source = str(intent_source or "").strip().lower()
    confidence = max(0.0, min(1.0, float(intent_confidence or 0.0)))
    if source == "llm":
        if confidence >= 0.85:
            return "high"
        if confidence >= 0.6:
            return "medium"
        return "low"
    if source == "heuristic":
        return "medium"
    if source == "intent_classification_failed":
        return "low"
    return "unknown"


def _normalize_retrieval_bias(value: str) -> str:
    token = str(value or "").strip().lower()
    return token if token in {"code", "docs", "hybrid"} else ""


def _normalize_answer_style(value: str, question_contract: Dict[str, Any], response_type: str) -> str:
    token = str(value or "").strip().lower()
    if token in {"default", "tutorial", "reference", "explanation", "troubleshooting", "comparison"}:
        return token
    contract_hint = str(dict(question_contract or {}).get("answer_style_hint") or "").strip().lower()
    if contract_hint in {"tutorial", "reference", "explanation", "troubleshooting", "comparison"}:
        return contract_hint
    rt = str(response_type or "").strip().lower()
    if rt == "doc_lookup":
        return "reference"
    if rt == "compare":
        return "comparison"
    if rt in {"bug_fix", "troubleshooting"}:
        return "troubleshooting"
    if rt in {"code_explain", "api_lookup"}:
        return "explanation"
    return "default"


def _docs_enabled(preferred_tool_mode: str, question_contract: Dict[str, Any]) -> bool:
    mode = str(preferred_tool_mode or "").strip().lower()
    if mode in {"docs", "hybrid"}:
        return True
    contract_kind = str(dict(question_contract or {}).get("kind") or "").strip().lower()
    contract_mode = str(dict(question_contract or {}).get("retrieval_mode") or "").strip().lower()
    return contract_kind == "doc_reference" or contract_mode == "docs"


def _tool_priority_for_contract(
    preferred_tool_mode: str,
    *,
    question_contract: Dict[str, Any],
    docs_enabled: bool,
) -> List[str]:
    base = ["find_symbol", "grep", "read", "glob"]
    contract_kind = str(dict(question_contract or {}).get("kind") or "").strip().lower()
    if contract_kind == "doc_reference" and preferred_tool_mode == "docs":
        return ["doc_search", "doc_read", *base]
    if docs_enabled:
        return [*base, "doc_search", "doc_read"]
    return base


def _primary_agent(question_contract: Dict[str, Any], response_type: str) -> str:
    contract_kind = str(dict(question_contract or {}).get("kind") or "").strip().lower()
    rt = str(response_type or "").strip().lower()
    if contract_kind == "doc_reference":
        return "general"
    if contract_kind == "code_change":
        return "build"
    if contract_kind in {"code_review", "failure_analysis", "code_compare"}:
        return "build"
    if rt in {"design_review", "compare", "migration"}:
        return "plan"
    return "build" if contract_kind in {"code_flow_explanation", "code_read"} else "general"


def _subagent(question_contract: Dict[str, Any], response_type: str) -> str:
    contract_kind = str(dict(question_contract or {}).get("kind") or "").strip().lower()
    rt = str(response_type or "").strip().lower()
    if contract_kind == "doc_reference" or rt in {"design_review", "compare"}:
        return "general"
    return "explore"


def _skillset(response_type: str, question_contract: Dict[str, Any]) -> List[str]:
    base = ["korean", "grounded", "no-meta"]
    contract_kind = str(dict(question_contract or {}).get("kind") or "").strip().lower()
    rt = str(response_type or "").strip().lower()
    if contract_kind in {"code_change", "code_flow_explanation", "code_review", "failure_analysis", "code_compare"} or rt in {"bug_fix", "troubleshooting", "code_review", "migration", "compare"}:
        return [*base, "actionable"]
    return base


def resolve_runtime_routing_profile(
    *,
    response_type: str,
    intent_source: str = "",
    intent_confidence: float = 0.0,
    retrieval_bias: str = "",
    answer_style: str = "",
    workspace_overlay_present: bool = False,
    question_contract: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized_contract = normalize_question_contract(
        question_contract,
        response_type=response_type,
        workspace_overlay_present=workspace_overlay_present,
    )
    default_tool_mode = _normalize_retrieval_bias(str(normalized_contract.get("retrieval_mode") or "")) or "code"
    preferred_tool_mode = _normalize_retrieval_bias(retrieval_bias) or default_tool_mode
    docs_enabled = _docs_enabled(preferred_tool_mode, normalized_contract)
    intent_family = _intent_family(response_type, normalized_contract)
    tool_priority = _tool_priority_for_contract(
        preferred_tool_mode,
        question_contract=normalized_contract,
        docs_enabled=docs_enabled,
    )
    normalized_answer_style = _normalize_answer_style(answer_style, normalized_contract, response_type)

    if str(normalized_contract.get("kind") or "").strip().lower() == "doc_reference" and preferred_tool_mode == "docs":
        tool_strategy = "doc_reference_with_code_fallback"
    elif workspace_overlay_present:
        tool_strategy = "frontier_search_loop_with_overlay_bootstrap"
    elif preferred_tool_mode == "hybrid":
        tool_strategy = "frontier_search_loop_hybrid"
    else:
        tool_strategy = "frontier_search_loop"

    return {
        "intent_family": intent_family,
        "agent_lane": (
            "doc_rag_lane"
            if intent_family == "document"
            else ("code_tool_lane" if intent_family == "code" else "general_assistant_lane")
        ),
        "preferred_tool_mode": preferred_tool_mode,
        "tool_strategy": tool_strategy,
        "tool_priority": tool_priority,
        "retrieval_bias": preferred_tool_mode,
        "docs_enabled": docs_enabled,
        "workspace_overlay_policy": (
            "overlay_bootstrap_not_authoritative_ground_with_reads"
            if workspace_overlay_present
            else "server_code_authoritative_with_optional_local_bootstrap"
        ),
        "workspace_overlay_present": bool(workspace_overlay_present),
        "answer_style": normalized_answer_style,
        "classification_stability": _classification_stability(intent_source, intent_confidence),
        "question_contract": normalized_contract,
        "agent_profile": {
            "primary_agent": _primary_agent(normalized_contract, response_type),
            "subagent": _subagent(normalized_contract, response_type),
            "toolset": list(tool_priority),
            "skillset": _skillset(response_type, normalized_contract),
        },
    }


def build_react_routing_payload(react_meta: Dict[str, Any], routing_profile: Dict[str, Any]) -> Dict[str, Any]:
    tool_calls = list(react_meta.get("tool_calls", []) or [])
    profile = dict(routing_profile or {})
    preferred_tool_mode = str(profile.get("preferred_tool_mode") or "code")
    return {
        "selected_mode": "react",
        "final_mode": "react",
        "default_mode": "react",
        "docs_primary": preferred_tool_mode == "docs",
        "confidence": 1.0,
        "target_mode": "react",
        "rationale": "react_loop",
        "reason": "react",
        "used_probe": False,
        "probe_scores": {"docs": 0.0, "code": 0.0},
        "agentic_refinement": {
            "enabled": True,
            "rounds": [{"round": idx + 1, "tool": call.get("tool")} for idx, call in enumerate(tool_calls)],
        },
        "profile": profile,
        "react": {
            "rounds": int(react_meta.get("rounds") or 0),
            "tool_calls": tool_calls,
            "thoughts": list(react_meta.get("thoughts", []) or []),
            "profile": profile,
        },
    }

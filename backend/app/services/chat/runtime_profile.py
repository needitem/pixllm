from typing import Any, Dict, List

from .retrieval.mode_policy import default_mode_for_response_type


def _intent_family_for_response_type(response_type: str) -> str:
    rt = str(response_type or "").strip().lower()
    if rt in {"doc_lookup"}:
        return "document"
    if rt in {
        "usage_guide",
        "api_lookup",
        "code_explain",
        "bug_fix",
        "refactor",
        "code_review",
        "code_generate",
        "troubleshooting",
        "design_review",
        "migration",
        "compare",
    }:
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


def _normalize_answer_style(value: str, response_type: str) -> str:
    token = str(value or "").strip().lower()
    if token in {"default", "tutorial", "reference", "explanation", "troubleshooting", "comparison"}:
        return token
    rt = str(response_type or "").strip().lower()
    if rt == "usage_guide":
        return "tutorial"
    if rt == "doc_lookup":
        return "reference"
    if rt in {"code_explain", "api_lookup"}:
        return "explanation"
    if rt in {"bug_fix", "troubleshooting"}:
        return "troubleshooting"
    if rt == "compare":
        return "comparison"
    return "default"


def _docs_enabled_for_response_type(response_type: str, preferred_tool_mode: str) -> bool:
    rt = str(response_type or "").strip().lower()
    mode = str(preferred_tool_mode or "").strip().lower()
    return mode == "docs" or rt == "doc_lookup"


def _tool_priority_for_mode(preferred_tool_mode: str, response_type: str, *, docs_enabled: bool) -> List[str]:
    rt = str(response_type or "").strip().lower()
    if preferred_tool_mode == "docs":
        base = ["doc_search", "doc_read", "find_symbol", "grep", "read", "glob"]
        return ["usage_bundle", *base] if rt == "usage_guide" else base
    if docs_enabled:
        base = ["find_symbol", "grep", "read", "glob", "doc_search", "doc_read"]
        return ["usage_bundle", *base] if rt == "usage_guide" else base
    base = ["find_symbol", "grep", "read", "glob"]
    return ["usage_bundle", *base] if rt == "usage_guide" else base


def _workspace_overlay_tool_priority(response_type: str, *, docs_enabled: bool) -> List[str]:
    rt = str(response_type or "").strip().lower()
    base = ["find_symbol", "read"]
    if docs_enabled:
        base.extend(["doc_search", "doc_read"])
    return base if rt == "usage_guide" else base


def _primary_agent(response_type: str) -> str:
    rt = str(response_type or "").strip().lower()
    if rt in {"design_review", "compare", "migration"}:
        return "plan"
    if rt in {"general", "doc_lookup"}:
        return "general"
    return "build"


def _subagent(response_type: str) -> str:
    rt = str(response_type or "").strip().lower()
    if rt in {"design_review", "compare"}:
        return "general"
    return "explore"


def _skillset(response_type: str) -> List[str]:
    base = ["korean", "grounded", "no-meta"]
    rt = str(response_type or "").strip().lower()
    if rt in {"bug_fix", "troubleshooting", "code_review", "migration"}:
        return [*base, "actionable"]
    return base


def _toolset(preferred_tool_mode: str, *, docs_enabled: bool) -> List[str]:
    if preferred_tool_mode == "docs":
        return ["doc_search", "doc_read", "find_symbol", "grep", "read", "glob"]
    if docs_enabled:
        return ["find_symbol", "grep", "read", "glob", "doc_search", "doc_read"]
    return ["find_symbol", "grep", "read", "glob"]


def _workspace_overlay_toolset(*, docs_enabled: bool) -> List[str]:
    return ["find_symbol", "read", "doc_search", "doc_read"] if docs_enabled else ["find_symbol", "read"]


def resolve_runtime_routing_profile(
    *,
    response_type: str,
    intent_source: str = "",
    intent_confidence: float = 0.0,
    retrieval_bias: str = "",
    answer_style: str = "",
    workspace_overlay_present: bool = False,
) -> Dict[str, Any]:
    default_tool_mode = default_mode_for_response_type(response_type)
    preferred_tool_mode = _normalize_retrieval_bias(retrieval_bias) or default_tool_mode
    docs_enabled = _docs_enabled_for_response_type(response_type, preferred_tool_mode)
    intent_family = _intent_family_for_response_type(response_type)
    overlay_present = bool(workspace_overlay_present)
    tool_priority = (
        _workspace_overlay_tool_priority(response_type, docs_enabled=docs_enabled)
        if overlay_present
        else _tool_priority_for_mode(preferred_tool_mode, response_type, docs_enabled=docs_enabled)
    )
    normalized_answer_style = _normalize_answer_style(answer_style, response_type)
    return {
        "intent_family": intent_family,
        "agent_lane": (
            "doc_rag_lane"
            if intent_family == "document"
            else ("code_tool_lane" if intent_family == "code" else "general_assistant_lane")
        ),
        "preferred_tool_mode": preferred_tool_mode,
        "tool_strategy": (
            "docs_first_then_code"
            if preferred_tool_mode == "docs"
            else (
                "local_workspace_primary_with_engine_reference"
                if overlay_present
                else ("server_code_first_with_local_overlay" if not docs_enabled else "server_code_first_then_docs")
            )
        ),
        "tool_priority": tool_priority,
        "retrieval_bias": preferred_tool_mode,
        "docs_enabled": docs_enabled,
        "workspace_overlay_policy": (
            "local_workspace_is_authoritative_server_engine_is_reference_only"
            if overlay_present
            else "server_code_is_authoritative_local_overlay_is_supplemental"
        ),
        "workspace_overlay_present": overlay_present,
        "answer_style": normalized_answer_style,
        "classification_stability": _classification_stability(intent_source, intent_confidence),
        "agent_profile": {
            "primary_agent": _primary_agent(response_type),
            "subagent": _subagent(response_type),
            "toolset": _workspace_overlay_toolset(docs_enabled=docs_enabled) if overlay_present else _toolset(preferred_tool_mode, docs_enabled=docs_enabled),
            "skillset": _skillset(response_type),
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

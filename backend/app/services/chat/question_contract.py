from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List


_FLOW_HINT_RE = re.compile(
    r"\b(explain|flow|path|pipeline|workflow|caller|callee|call chain|lifecycle|where|entry|sink)\b",
    re.IGNORECASE,
)
_DOC_HINT_RE = re.compile(
    r"\b(doc|docs|documentation|api|reference|manual|parameter|option)\b",
    re.IGNORECASE,
)
_CODE_HINT_RE = re.compile(r"[/\\]|`[^`]+`|::|->|[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*|\b[A-Z][A-Za-z0-9_]{2,}\b")
_HANGUL_FLOW_HINT_RE = re.compile(
    r"(\uC124\uBA85|\uD750\uB984|\uACFC\uC815|\uD638\uCD9C|\uACBD\uB85C|\uC5B4\uB514|\uC9C4\uC785|\uCD9C\uAD6C|\uC601\uD5A5|\uD6C4\uC18D)"
)
_HANGUL_DOC_HINT_RE = re.compile(r"(\uBB38\uC11C|\uAC00\uC774\uB4DC|\uB808\uD37C\uB7F0\uC2A4|\uC0AC\uC6A9\uBC95|\uD30C\uB77C\uBBF8\uD130|\uC635\uC158)")
_FLOW_METHOD_DECL_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|virtual|override|sealed|partial|async)\s+)+"
    r"[\w<>\[\],\s]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
    re.MULTILINE,
)
_FLOW_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_TYPE_DECL_RE = re.compile(r"^\s*(?:public|private|protected|internal|static|sealed|partial|\s)*(?:enum|class|struct|interface)\b", re.MULTILINE)
_FLOW_CALL_KEYWORDS = {
    "if",
    "for",
    "foreach",
    "while",
    "switch",
    "catch",
    "using",
    "nameof",
    "typeof",
    "return",
    "new",
}


def _normalize_str(value: Any) -> str:
    return str(value or "").strip()


def _normalize_tokens(values: Iterable[Any] | None) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in values or []:
        token = str(item or "").strip().lower()
        if not token or token in seen:
            continue
        seen.add(token)
        ordered.append(token)
    return ordered


def _ordered_unique(values: Iterable[Any]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in values:
        token = str(item or "").strip()
        lowered = token.lower()
        if not token or lowered in seen:
            continue
        seen.add(lowered)
        ordered.append(token)
    return ordered


def _looks_like_flow_question(message: str, *, workspace_overlay_present: bool = False) -> bool:
    text = _normalize_str(message)
    if not text:
        return False
    return bool(_FLOW_HINT_RE.search(text)) or bool(_HANGUL_FLOW_HINT_RE.search(text))


def _looks_like_doc_question(message: str) -> bool:
    text = _normalize_str(message)
    if not text:
        return False
    return bool(_DOC_HINT_RE.search(text)) or bool(_HANGUL_DOC_HINT_RE.search(text))


def _looks_like_code_read_question(message: str) -> bool:
    text = _normalize_str(message)
    if not text:
        return False
    return bool(_CODE_HINT_RE.search(text))


def _base_contract(
    *,
    kind: str,
    retrieval_mode: str,
    answer_style_hint: str,
    require_direct_reads: bool,
    coverage_axes: List[Dict[str, Any]] | None = None,
    continue_while_open_frontier: bool = False,
    budget: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "kind": kind,
        "retrieval_mode": retrieval_mode,
        "answer_style_hint": answer_style_hint,
        "require_direct_reads": bool(require_direct_reads),
        "coverage_axes": list(coverage_axes or []),
        "frontier_policy": {
            "continue_while_open_frontier": bool(continue_while_open_frontier),
            "continue_while_axes_missing": bool(coverage_axes),
        },
        "budget": dict(budget or {}),
    }


def build_question_contract(
    *,
    message: str,
    task_type: str = "",
    tool_scope: List[str] | None = None,
    workspace_overlay_present: bool = False,
    response_type: str = "",
) -> Dict[str, Any]:
    explicit_task_type = _normalize_str(task_type).lower()
    normalized_scope = _normalize_tokens(tool_scope)
    looks_flow = _looks_like_flow_question(
        message,
        workspace_overlay_present=workspace_overlay_present,
    )

    if explicit_task_type in {"docs", "doc", "doc_lookup", "document", "reference"}:
        return _base_contract(
            kind="doc_reference",
            retrieval_mode="docs",
            answer_style_hint="reference",
            require_direct_reads=False,
            budget={"max_rounds": 8, "max_tool_calls": 12},
        )

    if explicit_task_type in {"change", "edit", "write", "code_generate", "bug_fix", "refactor", "migration", "fix"}:
        return _base_contract(
            kind="code_change",
            retrieval_mode="code",
            answer_style_hint="default",
            require_direct_reads=True,
            budget={"max_rounds": 10, "max_tool_calls": 18},
        )

    if looks_flow:
        return _base_contract(
            kind="code_flow_explanation",
            retrieval_mode="code",
            answer_style_hint="explanation",
            require_direct_reads=True,
            coverage_axes=[
                {"id": "entry_or_caller", "label": "entry or caller"},
                {"id": "focal_processing", "label": "focal processing method"},
                {"id": "downstream_effect", "label": "downstream effect or sink"},
            ],
            continue_while_open_frontier=True,
            budget={
                "max_rounds": 14 if workspace_overlay_present else 10,
                "max_tool_calls": 28 if workspace_overlay_present else 18,
                "max_engine_symbol_candidates": 6,
                "max_engine_windows": 6,
            },
        )

    if _looks_like_doc_question(message):
        return _base_contract(
            kind="doc_reference",
            retrieval_mode="docs",
            answer_style_hint="reference",
            require_direct_reads=False,
            budget={"max_rounds": 8, "max_tool_calls": 14},
        )

    if _looks_like_code_read_question(message):
        return _base_contract(
            kind="code_read",
            retrieval_mode="code",
            answer_style_hint="explanation",
            require_direct_reads=True,
            budget={"max_rounds": 8, "max_tool_calls": 14},
        )

    if explicit_task_type in {"usage", "read", "analysis", "compare", "general"} or normalized_scope:
        return _base_contract(
            kind="code_read",
            retrieval_mode="code",
            answer_style_hint="explanation",
            require_direct_reads=True,
            budget={"max_rounds": 8, "max_tool_calls": 14},
        )

    return _base_contract(
        kind="general",
        retrieval_mode="hybrid" if "docs" in normalized_scope else "code",
        answer_style_hint="default",
        require_direct_reads=False,
        budget={"max_rounds": 8, "max_tool_calls": 12},
    )


def normalize_question_contract(
    contract: Dict[str, Any] | None,
    *,
    response_type: str = "",
    message: str = "",
    task_type: str = "",
    tool_scope: List[str] | None = None,
    workspace_overlay_present: bool = False,
) -> Dict[str, Any]:
    fallback = build_question_contract(
        message=message,
        task_type=task_type,
        tool_scope=tool_scope,
        workspace_overlay_present=workspace_overlay_present,
        response_type=response_type,
    )
    payload = dict(contract or {})
    payload_frontier_policy = dict(payload.get("frontier_policy") or {}) if isinstance(payload.get("frontier_policy"), dict) else {}
    fallback_frontier_policy = dict(fallback.get("frontier_policy") or {})
    normalized = {
        "kind": _normalize_str(payload.get("kind") or fallback.get("kind")).lower() or fallback["kind"],
        "retrieval_mode": _normalize_str(payload.get("retrieval_mode") or fallback.get("retrieval_mode")).lower() or fallback["retrieval_mode"],
        "answer_style_hint": _normalize_str(payload.get("answer_style_hint") or fallback.get("answer_style_hint")).lower() or fallback["answer_style_hint"],
        "require_direct_reads": bool(
            payload.get("require_direct_reads")
            if "require_direct_reads" in payload
            else fallback.get("require_direct_reads")
        ),
        "coverage_axes": [],
        "frontier_policy": {
            "continue_while_open_frontier": bool(
                payload_frontier_policy.get(
                    "continue_while_open_frontier",
                    fallback_frontier_policy.get("continue_while_open_frontier"),
                )
            ),
            "continue_while_axes_missing": bool(
                payload_frontier_policy.get(
                    "continue_while_axes_missing",
                    fallback_frontier_policy.get("continue_while_axes_missing"),
                )
            ),
        },
        "budget": dict(fallback.get("budget") or {}),
    }
    for key, value in dict(payload.get("budget") or {}).items():
        normalized["budget"][key] = value

    axes = list(payload.get("coverage_axes") or fallback.get("coverage_axes") or [])
    for axis in axes:
        if isinstance(axis, dict):
            axis_id = _normalize_str(axis.get("id")).lower()
            label = _normalize_str(axis.get("label"))
        else:
            axis_id = _normalize_str(axis).lower()
            label = ""
        if not axis_id:
            continue
        normalized["coverage_axes"].append(
            {
                "id": axis_id,
                "label": label or axis_id.replace("_", " "),
            }
        )

    if normalized["retrieval_mode"] not in {"code", "docs", "hybrid"}:
        normalized["retrieval_mode"] = fallback["retrieval_mode"]
    if normalized["answer_style_hint"] not in {"default", "reference", "explanation", "tutorial", "troubleshooting", "comparison"}:
        normalized["answer_style_hint"] = fallback["answer_style_hint"]
    return normalized


def _collect_candidate_symbols(items: Iterable[Dict[str, Any]], *keys: str) -> List[str]:
    collected: List[str] = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        for key in keys:
            value = str(item.get(key) or "").strip()
            if value:
                collected.append(value)
    return _ordered_unique(collected)


def _read_has_flow_signal(read: Dict[str, Any]) -> bool:
    text = _normalize_str(dict(read or {}).get("content"))
    if not text:
        return False
    if _FLOW_METHOD_DECL_RE.search(text):
        return True
    if _TYPE_DECL_RE.search(text) and not _FLOW_METHOD_DECL_RE.search(text):
        return False
    for token in _FLOW_CALL_RE.findall(text):
        if str(token or "").strip().lower() not in _FLOW_CALL_KEYWORDS:
            return True
    return False


def evaluate_question_contract(
    contract: Dict[str, Any] | None,
    *,
    graph_gate: Dict[str, Any] | None = None,
    direct_read_count: int = 0,
    bootstrap: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized = normalize_question_contract(contract)
    graph_state = dict(graph_gate or {})
    bootstrap_state = dict(bootstrap or {})

    if normalized.get("kind") != "code_flow_explanation":
        return {
            "kind": normalized.get("kind"),
            "passed": True,
            "axes": [],
            "missing_axes": [],
            "issues": [],
            "frontier_open": False,
            "next_search_candidates": list(bootstrap_state.get("next_search_candidates") or []),
        }

    primary_reads = list(bootstrap_state.get("primary_reads") or [])
    support_reads = list(bootstrap_state.get("support_reads") or [])
    flow_observations = list(bootstrap_state.get("flow_observations") or [])
    trace_relations = list(bootstrap_state.get("trace_relations") or [])
    engine_windows = list(bootstrap_state.get("engine_windows") or [])
    open_frontier_symbols = list(bootstrap_state.get("open_frontier_symbols") or [])
    unresolved_edges = list(bootstrap_state.get("unresolved_caller_callee_edges") or [])
    graph_chain = list(graph_state.get("chain") or [])
    graph_frontiers = list(graph_state.get("frontiers") or [])
    flow_reads = [*list(primary_reads or []), *list(support_reads or [])]
    flow_read_signal = any(_read_has_flow_signal(read) for read in flow_reads)

    entry_covered = bool(
        any("caller" in str(item.get("relation") or "").lower() for item in graph_chain)
        or any(str(item.get("tool") or "").lower() == "find_callers" for item in trace_relations)
        or any(str(item.get("caller_symbol") or "").strip() for item in flow_observations)
    )
    focal_covered = bool(
        int(direct_read_count or 0) > 0
        and (
            flow_read_signal
            or _collect_candidate_symbols(flow_observations, "caller_symbol", "callee_symbol")
            or any("call" in str(item.get("relation") or "").lower() for item in graph_chain)
        )
    )
    downstream_covered = bool(
        unresolved_edges
        or engine_windows
        or any(str(item.get("callee_symbol") or "").strip() for item in flow_observations)
        or any("callee" in str(item.get("relation") or "").lower() or "downstream" in str(item.get("relation") or "").lower() for item in graph_chain)
    )

    axis_status = {
        "entry_or_caller": entry_covered,
        "focal_processing": focal_covered,
        "downstream_effect": downstream_covered,
    }
    axes = [
        {
            "id": str(axis.get("id") or "").strip(),
            "label": str(axis.get("label") or "").strip(),
            "covered": bool(axis_status.get(str(axis.get("id") or "").strip(), False)),
        }
        for axis in list(normalized.get("coverage_axes") or [])
    ]
    missing_axes = [axis["id"] for axis in axes if not bool(axis.get("covered"))]
    frontier_open = bool(graph_frontiers or open_frontier_symbols or unresolved_edges)

    issues: List[str] = []
    if normalized.get("require_direct_reads") and int(direct_read_count or 0) <= 0:
        issues.append("missing_direct_reads")
    if missing_axes:
        issues.append("missing_contract_axes")
    if frontier_open and bool(dict(normalized.get("frontier_policy") or {}).get("continue_while_open_frontier")):
        issues.append("open_contract_frontier")

    return {
        "kind": normalized.get("kind"),
        "passed": len(issues) == 0,
        "axes": axes,
        "missing_axes": missing_axes,
        "issues": issues,
        "frontier_open": frontier_open,
        "open_frontier_symbols": _ordered_unique(open_frontier_symbols),
        "unresolved_caller_callee_edges": list(unresolved_edges),
        "next_search_candidates": list(bootstrap_state.get("next_search_candidates") or []),
    }

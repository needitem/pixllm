from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List


_EXPLICIT_DOC_TASK_TYPES = {"docs", "doc", "doc_lookup", "document", "reference"}
_EXPLICIT_CHANGE_TASK_TYPES = {"change", "edit", "write", "code_generate", "bug_fix", "refactor", "migration", "fix"}
_EXPLICIT_REVIEW_TASK_TYPES = {"review", "code_review", "design_review"}
_EXPLICIT_FAILURE_TASK_TYPES = {"repair", "troubleshooting", "debug"}
_EXPLICIT_COMPARE_TASK_TYPES = {"compare"}
_EXPLICIT_READ_TASK_TYPES = {"usage", "read", "analysis", "general", "workspace_overlay", "explain"}

_WRITE_SCOPE = {"write", "execute", "build", "svn"}
_DOC_SCOPE = {"docs", "doc_search", "doc_read"}
_REVIEW_SCOPE = {"review", "code_review"}

_CODE_PATH_RE = re.compile(r"[/\\]|`[^`]+`|\b[A-Za-z0-9_.-]+\.[A-Za-z0-9]{1,8}\b")
_CODE_FENCE_RE = re.compile(r"```|`[^`]+`")
_MEMBER_ACCESS_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\s*(?:\.|::|->)\s*[A-Za-z_][A-Za-z0-9_]*")
_CALL_LIKE_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_SYMBOL_TOKEN_RE = re.compile(r"\b[A-Z][A-Za-z0-9_]{2,}\b")
_ASCII_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
_HANGUL_TOKEN_RE = re.compile(r"[\uAC00-\uD7A3]{2,}")
_FLOW_METHOD_DECL_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|virtual|override|sealed|partial|async)\s+)+"
    r"[\w<>\[\],\s]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
    re.MULTILINE,
)
_TYPE_DECL_RE = re.compile(
    r"^\s*(?:public|private|protected|internal|static|sealed|partial|\s)*(?:enum|class|struct|interface)\b",
    re.MULTILINE,
)
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
    "base",
    "this",
}
_DIRECT_READ_TOOLS = {"read_file", "read_symbol_span", "symbol_neighborhood"}
_RELATION_TOOLS = {"find_callers", "find_references"}


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


def _extract_changed_paths_from_text(*texts: Any) -> List[str]:
    paths: List[str] = []
    seen = set()
    for raw_text in texts:
        for raw_line in str(raw_text or "").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            candidate = ""
            if line.startswith("Index: "):
                candidate = line[7:].strip()
            else:
                status_match = re.match(r"^[?MADRC!~\s]{1,8}\s+(.+)$", line)
                if status_match:
                    candidate = str(status_match.group(1) or "").strip()
            normalized = candidate.replace("\\", "/").strip()
            if not normalized:
                continue
            lowered = normalized.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            paths.append(normalized)
    return paths


def build_message_structure_profile(message: str) -> Dict[str, Any]:
    text = _normalize_str(message)
    path_reference_count = len(_CODE_PATH_RE.findall(text))
    member_access_count = len(_MEMBER_ACCESS_RE.findall(text))
    call_like_tokens = [token for token in _CALL_LIKE_RE.findall(text) if str(token or "").strip().lower() not in _FLOW_CALL_KEYWORDS]
    explicit_symbols = _ordered_unique(
        [
            *(_SYMBOL_TOKEN_RE.findall(text) or []),
            *call_like_tokens,
        ]
    )
    explicit_identifiers = _ordered_unique(
        [
            *explicit_symbols,
            *(_ASCII_IDENTIFIER_RE.findall(text) or []),
        ]
    )
    hangul_terms = _ordered_unique(_HANGUL_TOKEN_RE.findall(text) or [])
    return {
        "text_present": bool(text),
        "path_reference_count": path_reference_count,
        "member_access_count": member_access_count,
        "call_like_count": len(call_like_tokens),
        "code_fence_count": len(_CODE_FENCE_RE.findall(text)),
        "explicit_identifier_count": len(explicit_identifiers),
        "explicit_identifiers": explicit_identifiers,
        "symbol_candidates": explicit_symbols,
        "hangul_terms": hangul_terms,
        "has_explicit_code_target": bool(explicit_symbols or path_reference_count or member_access_count),
        "has_code_context": bool(
            path_reference_count
            or member_access_count
            or call_like_tokens
            or explicit_identifiers
            or _CODE_FENCE_RE.search(text)
        ),
    }


def _graph_state(local_workspace_overlay: Dict[str, Any] | None) -> Dict[str, Any]:
    overlay = dict(local_workspace_overlay or {})
    raw_graph = overlay.get("workspace_graph")
    graph = dict(raw_graph or {}) if isinstance(raw_graph, dict) else {}
    raw_state = graph.get("graph_state")
    return dict(raw_state or {}) if isinstance(raw_state, dict) else {}


def _trace_steps(local_workspace_overlay: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    overlay = dict(local_workspace_overlay or {})
    steps = []
    for item in list(overlay.get("local_trace") or []):
        if isinstance(item, dict):
            steps.append(dict(item))
    return steps


def _read_has_flow_signal(read: Dict[str, Any]) -> bool:
    text = _normalize_str(dict(read or {}).get("content"))
    if not text:
        return False
    if _FLOW_METHOD_DECL_RE.search(text):
        return True
    if _TYPE_DECL_RE.search(text) and not _FLOW_METHOD_DECL_RE.search(text):
        return False
    for token in _CALL_LIKE_RE.findall(text):
        if str(token or "").strip().lower() not in _FLOW_CALL_KEYWORDS:
            return True
    return False


def build_overlay_structure_profile(local_workspace_overlay: Dict[str, Any] | None = None) -> Dict[str, Any]:
    overlay = dict(local_workspace_overlay or {})
    if not overlay:
        return {
            "present": False,
            "selected_file_present": False,
            "selected_file_executable": False,
            "direct_read_count": 0,
            "executable_read_count": 0,
            "trace_relation_count": 0,
            "workspace_graph_chain_count": 0,
            "workspace_graph_frontier_count": 0,
            "workspace_status_present": False,
            "workspace_diff_present": False,
            "changed_path_count": 0,
            "changed_paths": [],
            "target_symbol_present": False,
            "has_flow_graph": False,
            "has_flow_evidence": False,
        }

    selected_file_content = _normalize_str(overlay.get("selected_file_content"))
    selected_file_present = bool(_normalize_str(overlay.get("selected_file_path")) and selected_file_content)
    selected_file_executable = _read_has_flow_signal({"content": selected_file_content}) if selected_file_present else False

    direct_read_count = 1 if selected_file_present else 0
    executable_read_count = 1 if selected_file_executable else 0
    trace_relation_count = 0
    for step in _trace_steps(overlay):
        tool_name = _normalize_str(step.get("tool")).lower()
        observation = step.get("observation")
        observation_dict = dict(observation or {}) if isinstance(observation, dict) else {}
        if tool_name in _DIRECT_READ_TOOLS:
            content = _normalize_str(observation_dict.get("content"))
            if content:
                direct_read_count += 1
                if _read_has_flow_signal({"content": content}):
                    executable_read_count += 1
        if tool_name in _RELATION_TOOLS:
            items = list(observation_dict.get("items") or [])
            trace_relation_count += max(1, len(items)) if observation_dict else 1

    graph_state = _graph_state(overlay)
    graph_chain = list(graph_state.get("chain") or [])
    graph_frontiers = list(graph_state.get("frontiers") or [])
    if not graph_frontiers and isinstance(graph_state.get("frontier"), dict):
        graph_frontiers = [graph_state.get("frontier")]

    workspace_status = _normalize_str(overlay.get("workspace_status"))
    workspace_diff = _normalize_str(overlay.get("workspace_diff"))
    changed_paths = _ordered_unique(
        list(overlay.get("workspace_change_paths") or [])
        or _extract_changed_paths_from_text(workspace_status, workspace_diff)
    )

    target_symbol_present = bool(_normalize_str(dict(overlay.get("workspace_graph") or {}).get("target_symbol")))
    has_flow_graph = bool(graph_chain or graph_frontiers)
    has_flow_evidence = bool(
        has_flow_graph
        or trace_relation_count > 0
        or (executable_read_count > 0 and target_symbol_present)
    )

    return {
        "present": True,
        "selected_file_present": selected_file_present,
        "selected_file_executable": selected_file_executable,
        "direct_read_count": direct_read_count,
        "executable_read_count": executable_read_count,
        "trace_relation_count": trace_relation_count,
        "workspace_graph_chain_count": len(graph_chain),
        "workspace_graph_frontier_count": len(graph_frontiers),
        "workspace_status_present": bool(workspace_status),
        "workspace_diff_present": bool(workspace_diff),
        "changed_path_count": len(changed_paths),
        "changed_paths": changed_paths,
        "target_symbol_present": target_symbol_present,
        "has_flow_graph": has_flow_graph,
        "has_flow_evidence": has_flow_evidence,
    }


def build_question_contract(
    *,
    message: str,
    task_type: str = "",
    tool_scope: List[str] | None = None,
    workspace_overlay_present: bool = False,
    response_type: str = "",
    local_workspace_overlay: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    _ = response_type
    explicit_task_type = _normalize_str(task_type).lower()
    normalized_scope = _normalize_tokens(tool_scope)
    message_profile = build_message_structure_profile(message)
    overlay_profile = build_overlay_structure_profile(local_workspace_overlay)
    has_overlay = bool(workspace_overlay_present or overlay_profile.get("present"))

    if explicit_task_type in _EXPLICIT_DOC_TASK_TYPES:
        return _base_contract(
            kind="doc_reference",
            retrieval_mode="docs",
            answer_style_hint="reference",
            require_direct_reads=False,
            budget={"max_rounds": 8, "max_tool_calls": 12},
        )

    if explicit_task_type in _EXPLICIT_REVIEW_TASK_TYPES or bool(set(normalized_scope) & _REVIEW_SCOPE):
        return _base_contract(
            kind="code_review",
            retrieval_mode="code",
            answer_style_hint="default",
            require_direct_reads=True,
            budget={"max_rounds": 10, "max_tool_calls": 18},
        )

    if explicit_task_type in _EXPLICIT_FAILURE_TASK_TYPES:
        return _base_contract(
            kind="failure_analysis",
            retrieval_mode="code",
            answer_style_hint="troubleshooting",
            require_direct_reads=True,
            budget={"max_rounds": 10, "max_tool_calls": 18},
        )

    if explicit_task_type in _EXPLICIT_CHANGE_TASK_TYPES or bool(set(normalized_scope) & _WRITE_SCOPE):
        return _base_contract(
            kind="code_change",
            retrieval_mode="code",
            answer_style_hint="default",
            require_direct_reads=True,
            budget={"max_rounds": 10, "max_tool_calls": 18},
        )

    if explicit_task_type in _EXPLICIT_COMPARE_TASK_TYPES:
        return _base_contract(
            kind="code_compare",
            retrieval_mode="code",
            answer_style_hint="comparison",
            require_direct_reads=True,
            budget={"max_rounds": 10, "max_tool_calls": 18},
        )

    if bool(set(normalized_scope) & _DOC_SCOPE) and not bool(set(normalized_scope) & _WRITE_SCOPE):
        return _base_contract(
            kind="doc_reference",
            retrieval_mode="docs",
            answer_style_hint="reference",
            require_direct_reads=False,
            budget={"max_rounds": 8, "max_tool_calls": 14},
        )

    if overlay_profile.get("has_flow_evidence"):
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
                "max_rounds": 14 if has_overlay else 10,
                "max_tool_calls": 28 if has_overlay else 18,
                "max_engine_symbol_candidates": 6,
                "max_engine_windows": 6,
            },
        )

    if (
        overlay_profile.get("workspace_diff_present")
        and overlay_profile.get("changed_path_count", 0) > 0
        and not message_profile.get("has_explicit_code_target")
    ):
        return _base_contract(
            kind="code_review",
            retrieval_mode="code",
            answer_style_hint="default",
            require_direct_reads=True,
            budget={"max_rounds": 10, "max_tool_calls": 18},
        )

    if explicit_task_type in _EXPLICIT_READ_TASK_TYPES:
        return _base_contract(
            kind="code_read",
            retrieval_mode="code",
            answer_style_hint="explanation",
            require_direct_reads=True,
            budget={"max_rounds": 8, "max_tool_calls": 14},
        )

    if message_profile.get("has_code_context") or overlay_profile.get("direct_read_count", 0) > 0 or has_overlay or normalized_scope:
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
    local_workspace_overlay: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    fallback = build_question_contract(
        message=message,
        task_type=task_type,
        tool_scope=tool_scope,
        workspace_overlay_present=workspace_overlay_present,
        response_type=response_type,
        local_workspace_overlay=local_workspace_overlay,
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

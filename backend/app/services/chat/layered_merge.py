from __future__ import annotations

from typing import Any, Dict, List


_DIRECT_READ_TOOLS = {"read_file", "read_symbol_span", "symbol_neighborhood"}
_TRACE_EVIDENCE_TOOLS = _DIRECT_READ_TOOLS | {"grep", "find_symbol", "find_references", "find_callers"}
_OVERLAY_TRACE_CHAR_BUDGET = 7200


def _normalize_str(value: Any) -> str:
    return str(value or "").strip()


def _normalize_graph(value: Any) -> Dict[str, Any]:
    return dict(value or {}) if isinstance(value, dict) else {}


def _trace_step_path(step: Dict[str, Any], fallback: str) -> str:
    observation = step.get("observation") if isinstance(step, dict) else {}
    if isinstance(observation, dict):
        path_value = _normalize_str(observation.get("path"))
        if path_value:
            return path_value
        items = list(observation.get("items") or [])
        if items:
            first = items[0] if isinstance(items[0], dict) else {}
            grep_path = _normalize_str(first.get("path"))
            if grep_path:
                return grep_path
    return fallback


def _trace_step_text(step: Dict[str, Any]) -> str:
    tool_name = _normalize_str(step.get("tool") or "tool").lower()
    thought = _normalize_str(step.get("thought"))
    observation = step.get("observation") if isinstance(step, dict) else {}
    if not isinstance(observation, dict):
        return thought
    if tool_name in _DIRECT_READ_TOOLS:
        content = _normalize_str(observation.get("content"))
        return "\n".join(part for part in [thought, content[:1200]] if part).strip()
    if tool_name in _TRACE_EVIDENCE_TOOLS:
        lines = []
        for item in list(observation.get("items") or [])[:3]:
            if not isinstance(item, dict):
                continue
            path = _normalize_str(item.get("path"))
            line = item.get("line")
            text = _normalize_str(item.get("text"))
            if path and text:
                prefix = f"{path}:{line}" if line else path
                lines.append(f"{prefix}: {text}")
        return "\n".join(part for part in [thought, *lines] if part).strip()[:1200]
    return ""


def _select_overlay_trace_steps(trace_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for index, step in enumerate(list(trace_steps or [])):
        tool_name = _normalize_str(step.get("tool") or "tool").lower()
        if tool_name not in _TRACE_EVIDENCE_TOOLS:
            continue
        text_value = _trace_step_text(step)
        if not text_value:
            continue
        candidates.append(
            {
                "index": index,
                "step": step,
                "tool": tool_name,
                "text": text_value,
                "is_direct_read": tool_name in _DIRECT_READ_TOOLS,
            }
        )

    if not candidates:
        return []

    selected: List[Dict[str, Any]] = []
    selected_indexes = set()
    used_chars = 0

    def _maybe_take(rows: List[Dict[str, Any]]) -> bool:
        nonlocal used_chars
        exhausted = False
        for row in rows:
            if row["index"] in selected_indexes:
                continue
            segment_chars = len(str(row.get("text") or ""))
            if selected and used_chars + segment_chars > _OVERLAY_TRACE_CHAR_BUDGET:
                exhausted = True
                continue
            selected.append(row)
            selected_indexes.add(row["index"])
            used_chars += segment_chars
            if used_chars >= _OVERLAY_TRACE_CHAR_BUDGET:
                exhausted = True
                break
        return exhausted

    direct_reads = [row for row in candidates if bool(row.get("is_direct_read"))]
    supporting_reads = [row for row in candidates if not bool(row.get("is_direct_read"))]

    exhausted = _maybe_take(direct_reads)
    if not exhausted:
        _maybe_take(list(reversed(supporting_reads)))

    if not selected:
        selected = [direct_reads[0] if direct_reads else candidates[-1]]

    return [row["step"] for row in sorted(selected, key=lambda item: item["index"])]


def _attachment_field(item: Any, key: str) -> Any:
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def extract_local_workspace_overlay(request: Any) -> Dict[str, Any]:
    attachments = list(getattr(request, "attachments", []) or [])
    for item in attachments:
        kind = _normalize_str(_attachment_field(item, "kind")).lower()
        if kind != "local_workspace_overlay":
            continue
        metadata = _attachment_field(item, "metadata") or {}
        if hasattr(metadata, "model_dump"):
            metadata = metadata.model_dump()
        return {
            "present": True,
            "workspace_path": _normalize_str(metadata.get("workspace_path")),
            "selected_file_path": _normalize_str(metadata.get("selected_file_path")),
            "selected_file_content": _normalize_str(metadata.get("selected_file_content")),
            "workspace_status": _normalize_str(metadata.get("workspace_status")),
            "workspace_diff": _normalize_str(metadata.get("workspace_diff")),
            "local_summary": _normalize_str(metadata.get("local_summary")),
            "local_context_text": _normalize_str(metadata.get("local_context_text")),
            "local_error": _normalize_str(metadata.get("local_error")),
            "local_trace": list(metadata.get("local_trace") or []),
            "workspace_graph": _normalize_graph(metadata.get("workspace_graph")),
            "question": _normalize_str(metadata.get("question")),
        }
    return {
        "present": False,
        "workspace_path": "",
        "selected_file_path": "",
        "selected_file_content": "",
        "workspace_status": "",
        "workspace_diff": "",
        "local_summary": "",
        "local_context_text": "",
        "local_error": "",
        "local_trace": [],
        "workspace_graph": {},
        "question": "",
    }


def build_local_overlay_evidence(local_overlay: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not bool(local_overlay.get("present")):
        return []

    items: List[Dict[str, Any]] = []
    selected_path = _normalize_str(local_overlay.get("selected_file_path"))
    selected_content = _normalize_str(local_overlay.get("selected_file_content"))
    if selected_path and selected_content:
        items.append(
            {
                "layer": "local_workspace_overlay",
                "kind": "selected_file",
                "path": selected_path,
                "text": selected_content[:1200],
            }
        )

    status_text = _normalize_str(local_overlay.get("workspace_status"))
    if status_text:
        items.append(
            {
                "layer": "local_workspace_overlay",
                "kind": "workspace_status",
                "path": local_overlay.get("workspace_path") or selected_path or "workspace",
                "text": status_text[:1200],
            }
        )

    diff_text = _normalize_str(local_overlay.get("workspace_diff"))
    if diff_text:
        items.append(
            {
                "layer": "local_workspace_overlay",
                "kind": "workspace_diff",
                "path": local_overlay.get("workspace_path") or selected_path or "workspace",
                "text": diff_text[:1600],
            }
        )

    summary_text = _normalize_str(local_overlay.get("local_summary"))
    if summary_text:
        items.append(
            {
                "layer": "local_workspace_overlay",
                "kind": "local_summary",
                "path": local_overlay.get("workspace_path") or selected_path or "workspace",
                "text": summary_text[:800],
            }
        )

    context_text = _normalize_str(local_overlay.get("local_context_text"))
    if context_text:
        items.append(
            {
                "layer": "local_workspace_overlay",
                "kind": "local_context",
                "path": local_overlay.get("workspace_path") or selected_path or "workspace",
                "text": context_text[:1600],
            }
        )

    workspace_graph = _normalize_graph(local_overlay.get("workspace_graph"))
    focus_file = _normalize_str(workspace_graph.get("focus_file"))
    core_files = [str(item).strip() for item in list(workspace_graph.get("core_files") or []) if str(item).strip()]
    supporting_files = [str(item).strip() for item in list(workspace_graph.get("supporting_files") or []) if str(item).strip()]
    if focus_file or core_files or supporting_files:
        graph_parts = []
        if focus_file:
            graph_parts.append(f"Focus file: {focus_file}")
        if core_files:
            graph_parts.append(f"Core flow files: {', '.join(core_files[:4])}")
        if supporting_files:
            graph_parts.append(f"Supporting files: {', '.join(supporting_files[:4])}")
        items.append(
            {
                "layer": "local_workspace_overlay",
                "kind": "workspace_graph",
                "path": focus_file or selected_path or local_overlay.get("workspace_path") or "workspace",
                "text": "\n".join(graph_parts)[:1200],
            }
        )

    trace_steps = _select_overlay_trace_steps(list(local_overlay.get("local_trace") or []))
    for offset, step in enumerate(trace_steps):
        tool_name = _normalize_str(step.get("tool") or "tool").lower()
        if tool_name not in _TRACE_EVIDENCE_TOOLS:
            continue
        path_value = _trace_step_path(step, selected_path or local_overlay.get("workspace_path") or "workspace")
        text_value = _trace_step_text(step)
        if not text_value:
            continue
        items.append(
            {
                "layer": "local_workspace_overlay",
                "kind": "local_tool_step",
                "path": path_value,
                "tool": tool_name,
                "text": text_value,
                "round": int(step.get("round") or offset + 1),
            }
        )

    return items


def build_layer_manifest(
    *,
    response_type: str,
    routing_profile: Dict[str, Any],
    results: List[Dict[str, Any]],
    sources: List[Dict[str, Any]],
    local_overlay: Dict[str, Any],
) -> Dict[str, Any]:
    local_items = build_local_overlay_evidence(local_overlay)
    server_code_count = sum(
        1
        for item in list(results or [])
        if str(dict(item.get("payload", {}) or {}).get("source_kind") or "").startswith("code")
    )
    server_doc_count = sum(
        1
        for item in list(results or [])
        if str(dict(item.get("payload", {}) or {}).get("source_kind") or "").startswith("doc")
    )

    merge_order = (
        ["local_workspace_overlay", "server_code_baseline", "server_docs"]
        if bool(local_overlay.get("present"))
        else ["server_code_baseline", "server_docs"]
    )

    return {
        "response_type": response_type,
        "strategy": str(routing_profile.get("tool_strategy") or ""),
        "workspace_overlay_policy": str(routing_profile.get("workspace_overlay_policy") or ""),
        "authoritative_layer": "local_workspace_overlay" if bool(local_overlay.get("present")) else "server_code_baseline",
        "merge_order": merge_order,
        "layers": [
            {
                "layer": "local_workspace_overlay",
                "enabled": bool(local_overlay.get("present")),
                "priority": 1,
                "evidence_count": len(local_items),
            },
            {
                "layer": "server_code_baseline",
                "enabled": True,
                "priority": 2,
                "evidence_count": server_code_count,
            },
            {
                "layer": "server_docs",
                "enabled": bool(routing_profile.get("docs_enabled")),
                "priority": 3,
                "evidence_count": server_doc_count,
            },
        ],
        "source_count": len(list(sources or [])),
        "summary": {
            "server_code_evidence": server_code_count,
            "local_overlay_evidence": len(local_items),
            "server_doc_evidence": server_doc_count,
            "docs_enabled": bool(routing_profile.get("docs_enabled")),
        },
    }

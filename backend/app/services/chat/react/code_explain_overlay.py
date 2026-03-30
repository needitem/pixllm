import asyncio
import json
import re
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .... import rag_config
from ....core.llm_utils import (
    build_chat_template_extra_body,
    extract_completion_finish_reason,
    safe_chat_completion_create,
    stream_chat_completion_text_with_meta,
)
from ....utils.source_guard import find_ungrounded_source_mentions, normalize_source_path
from ..retrieval.routing import build_sources
from ..workspace_graph import (
    build_workspace_grounding_report,
    collect_grounded_overlay_paths,
    extract_workspace_graph,
)
from ...tools.runtime import find_symbol, read_code_lines
from ...tools.query_terms import identifier_structure_score


TokenCallback = Optional[Callable[[str], Awaitable[None] | None]]
ProgressCallback = Optional[Callable[[Dict[str, Any]], Awaitable[None] | None]]
ToolCallback = Optional[Callable[[str, Dict[str, Any], str], Awaitable[None] | None]]

_SYMBOL_TOKEN_RE = re.compile(r"\b[A-Z][A-Za-z0-9_]{4,}\b")
_MEMBER_ACCESS_SYMBOL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:\.|::|->)\s*([A-Za-z_][A-Za-z0-9_]*)")
_CODE_LIKE_SYMBOL_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
_METHOD_DECL_RE = re.compile(
    r"^\s*(?:public|private|protected|internal|static|virtual|override|sealed|partial|async|\s)+"
    r"[\w<>\[\],\s]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("
)
_MEMBER_CALL_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:\.|::|->)\s*([A-Za-z_][A-Za-z0-9_]*)\s*\("
)
_DIRECT_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_CALL_KEYWORDS = {
    "if",
    "for",
    "foreach",
    "while",
    "switch",
    "return",
    "catch",
    "using",
    "nameof",
    "typeof",
    "default",
    "base",
    "this",
    "new",
}
_READ_TOOL_PRIORITY = {
    "read_symbol_span": 0,
    "symbol_neighborhood": 1,
    "selected_file": 2,
    "read_file": 3,
}
_ENGINE_SYMBOL_MATCH_CACHE: Dict[str, List[Dict[str, Any]]] = {}


def _normalize_path(value: Any) -> str:
    return str(value or "").strip().replace("\\", "/")


def _top_level_prefix(path: str) -> str:
    normalized = _normalize_path(path).strip("/")
    if not normalized:
        return ""
    return normalized.split("/", 1)[0].lower()


def _parse_line_range(line_range: str) -> tuple[int, int]:
    raw = str(line_range or "").strip()
    if not raw or "-" not in raw:
        return 1, 120
    try:
        start_s, end_s = raw.split("-", 1)
        start = max(1, int(start_s))
        end = max(start, int(end_s))
        return start, end
    except Exception:
        return 1, 120


def _build_engine_read_window(line_range: str, max_line_span: int) -> tuple[int, int]:
    start, end = _parse_line_range(line_range)
    center = max(start, min(end, start + ((end - start) // 2)))
    radius = max(24, min(80, max_line_span // 4))
    read_start = max(1, center - radius)
    read_end = max(read_start, min(read_start + max(40, radius * 2), center + radius))
    return read_start, read_end


def _collect_local_prefixes(local_overlay: Dict[str, Any]) -> set[str]:
    prefixes = set()
    for path in collect_grounded_overlay_paths(local_overlay):
        prefix = _top_level_prefix(path)
        if prefix:
            prefixes.add(prefix)
    graph = extract_workspace_graph(local_overlay)
    for path in list(graph.get("core_files") or []):
        prefix = _top_level_prefix(path)
        if prefix:
            prefixes.add(prefix)
    focus_path = str(graph.get("focus_file") or "").strip()
    focus_prefix = _top_level_prefix(focus_path)
    if focus_prefix:
        prefixes.add(focus_prefix)
    return prefixes


def _dedupe_tokens(tokens: List[str], *, limit: int = 12) -> List[str]:
    ordered: List[str] = []
    seen = set()
    for token in tokens:
        normalized = str(token or "").strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(normalized)
        if len(ordered) >= limit:
            break
    return ordered


def _is_generic_external_symbol(symbol: str) -> bool:
    token = _maybe_symbol(symbol)
    if not token:
        return True
    lowered = token.lower()
    if lowered in _CALL_KEYWORDS:
        return True
    structure = int(identifier_structure_score(token))
    if structure <= 0 and len(token) <= 4:
        return True
    if structure <= 1 and len(token) <= 8 and token == token.lower():
        return True
    return False


def _maybe_symbol(token: Any) -> str:
    raw = str(token or "").strip()
    if not raw:
        return ""
    if any(marker in raw for marker in (" ", "/", "\\", "|", "\n", "\t")):
        return ""
    match = _CODE_LIKE_SYMBOL_RE.search(raw)
    return str(match.group(0) or "").strip() if match else ""


def _observation_dict(step: Dict[str, Any]) -> Dict[str, Any]:
    observation = step.get("observation")
    return dict(observation or {}) if isinstance(observation, dict) else {}


def _trace_steps(local_overlay: Dict[str, Any], *, tools: Optional[set[str]] = None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for raw_step in list(local_overlay.get("local_trace") or []):
        if not isinstance(raw_step, dict):
            continue
        tool_name = str(raw_step.get("tool") or "").strip().lower()
        if tools is not None and tool_name not in tools:
            continue
        step = dict(raw_step)
        step["tool"] = tool_name
        out.append(step)
    return out


def _trace_step_symbol(step: Dict[str, Any]) -> str:
    observation = _observation_dict(step)
    for candidate in (
        step.get("target_symbol"),
        step.get("symbol"),
        observation.get("symbol"),
        observation.get("target_symbol"),
        observation.get("name"),
        step.get("query"),
    ):
        symbol = _maybe_symbol(candidate)
        if symbol:
            return symbol
    return ""


def _trace_step_path(step: Dict[str, Any], fallback: str = "") -> str:
    observation = _observation_dict(step)
    for candidate in (
        observation.get("path"),
        step.get("path"),
    ):
        path = _normalize_path(candidate)
        if path:
            return path
    for item in list(observation.get("items") or [])[:1]:
        if not isinstance(item, dict):
            continue
        path = _normalize_path(item.get("path"))
        if path:
            return path
    return _normalize_path(fallback)


def _path_segments(path: str) -> List[str]:
    return [segment for segment in _normalize_path(path).strip("/").split("/") if segment]


def _shared_prefix_depth(path: str, other: str) -> int:
    left = _path_segments(path)
    right = _path_segments(other)
    depth = 0
    for left_part, right_part in zip(left, right):
        if left_part.lower() != right_part.lower():
            break
        depth += 1
    return depth


def _path_priority(path: str, *, focus_path: str, selected_path: str) -> tuple[int, int, int, int, str]:
    normalized = _normalize_path(path).lower()
    selected = _normalize_path(selected_path).lower()
    focus = _normalize_path(focus_path).lower()
    shared_depth = max(
        _shared_prefix_depth(normalized, selected),
        _shared_prefix_depth(normalized, focus),
    )
    segment_count = len(_path_segments(normalized))
    return (
        0 if normalized == selected else 1,
        0 if normalized == focus else 1,
        -shared_depth,
        segment_count,
        normalized,
    )


def _sort_local_windows(local_windows: List[Dict[str, Any]], local_overlay: Dict[str, Any]) -> List[Dict[str, Any]]:
    graph = extract_workspace_graph(local_overlay)
    focus_path = str(graph.get("focus_file") or "").strip()
    selected_path = str(local_overlay.get("selected_file_path") or "").strip()
    return sorted(
        list(local_windows or []),
        key=lambda item: _path_priority(
            str(item.get("path") or ""),
            focus_path=focus_path,
            selected_path=selected_path,
        ),
    )


def _collect_local_reads(local_overlay: Dict[str, Any]) -> List[Dict[str, Any]]:
    reads: List[Dict[str, Any]] = []
    seen = set()
    selected_path = _normalize_path(local_overlay.get("selected_file_path"))
    selected_content = str(local_overlay.get("selected_file_content") or "")
    graph = extract_workspace_graph(local_overlay)
    graph_anchor = _maybe_symbol(graph.get("target_symbol"))

    def _append(
        *,
        tool: str,
        path: Any,
        content: Any,
        line_range: Any = "",
        symbol: Any = "",
        round_index: Any = 0,
    ) -> None:
        normalized_path = _normalize_path(path)
        text = str(content or "")
        normalized_range = str(line_range or "").strip() or "1-1"
        normalized_symbol = str(symbol or "").strip()
        if not normalized_path or not text.strip():
            return
        key = (
            normalized_path.lower(),
            normalized_range,
            str(tool or "").strip().lower(),
            normalized_symbol.lower(),
        )
        if key in seen:
            return
        seen.add(key)
        try:
            round_value = int(round_index or 0)
        except Exception:
            round_value = 0
        reads.append(
            {
                "path": normalized_path,
                "content": text,
                "line_range": normalized_range,
                "tool": str(tool or "").strip().lower(),
                "symbol": normalized_symbol,
                "round": round_value,
            }
        )

    if selected_path and selected_content.strip():
        _append(
            tool="selected_file",
            path=selected_path,
            content=selected_content,
            line_range="1-1",
            symbol=graph_anchor,
            round_index=0,
        )

    for step in _trace_steps(local_overlay, tools={"read_file", "read_symbol_span", "symbol_neighborhood"}):
        observation = _observation_dict(step)
        _append(
            tool=step.get("tool") or "",
            path=_trace_step_path(step, fallback=selected_path),
            content=observation.get("content"),
            line_range=observation.get("lineRange") or observation.get("line_range") or "",
            symbol=_trace_step_symbol(step),
            round_index=step.get("round"),
        )

    return reads


def _collect_trace_relations(local_overlay: Dict[str, Any]) -> List[Dict[str, Any]]:
    relations: List[Dict[str, Any]] = []
    seen = set()
    selected_path = _normalize_path(local_overlay.get("selected_file_path"))

    def _append(
        *,
        tool: str,
        anchor_symbol: str = "",
        path: str = "",
        line: Any = 0,
        related_symbol: str = "",
        snippet: str = "",
    ) -> None:
        normalized_path = _normalize_path(path)
        anchor = str(anchor_symbol or "").strip()
        related = str(related_symbol or "").strip()
        text = str(snippet or "").strip()
        try:
            line_value = int(line or 0)
        except Exception:
            line_value = 0
        key = (
            str(tool or "").strip().lower(),
            anchor.lower(),
            normalized_path.lower(),
            line_value,
            related.lower(),
            text[:160].lower(),
        )
        if key in seen:
            return
        seen.add(key)
        relations.append(
            {
                "tool": str(tool or "").strip().lower(),
                "anchor_symbol": anchor,
                "path": normalized_path,
                "line": line_value,
                "related_symbol": related,
                "snippet": text[:240],
            }
        )

    for step in _trace_steps(local_overlay, tools={"find_symbol", "find_references", "find_callers", "symbol_outline", "symbol_neighborhood"}):
        tool_name = str(step.get("tool") or "").strip().lower()
        observation = _observation_dict(step)
        anchor_symbol = _trace_step_symbol(step)
        path = _trace_step_path(step, fallback=selected_path)
        if tool_name == "symbol_neighborhood" and str(observation.get("content") or "").strip():
            start_line, _ = _parse_line_range(str(observation.get("lineRange") or observation.get("line_range") or ""))
            _append(
                tool=tool_name,
                anchor_symbol=anchor_symbol,
                path=path,
                line=start_line,
                related_symbol=anchor_symbol,
                snippet=str(observation.get("content") or "").splitlines()[0][:240],
            )
        items = list(observation.get("items") or [])
        if items:
            for item in items[:16]:
                if not isinstance(item, dict):
                    continue
                _append(
                    tool=tool_name,
                    anchor_symbol=anchor_symbol,
                    path=_normalize_path(item.get("path") or path),
                    line=item.get("line") or 0,
                    related_symbol=_maybe_symbol(item.get("symbol") or item.get("name")),
                    snippet=str(item.get("text") or item.get("content") or "").strip(),
                )
            continue
        if path:
            _append(
                tool=tool_name,
                anchor_symbol=anchor_symbol,
                path=path,
                line=0,
                related_symbol=_maybe_symbol(observation.get("symbol") or observation.get("name")),
                snippet=str(observation.get("content") or "").strip()[:240],
            )

    return relations[:48]


def _extract_flow_observations(local_windows: List[Dict[str, Any]], local_overlay: Dict[str, Any]) -> List[Dict[str, Any]]:
    observations: List[Dict[str, Any]] = []
    seen = set()
    for window in _sort_local_windows(local_windows, local_overlay)[:4]:
        path = str(window.get("path") or "").strip()
        start_line, _ = _parse_line_range(str(window.get("line_range") or ""))
        current_method = str(window.get("symbol") or "").strip()
        for offset, raw_line in enumerate(str(window.get("content") or "").splitlines()):
            line = raw_line.rstrip()
            stripped = line.strip()
            if not stripped:
                continue
            decl_match = _METHOD_DECL_RE.match(line)
            if decl_match:
                current_method = str(decl_match.group(1) or "").strip()
                continue
            for owner, callee in _MEMBER_CALL_RE.findall(line):
                callee_name = str(callee or "").strip()
                if _is_generic_external_symbol(callee_name):
                    continue
                key = (path.lower(), current_method.lower(), callee_name.lower(), start_line + offset)
                if key in seen:
                    continue
                seen.add(key)
                observations.append(
                    {
                        "path": path,
                        "line": start_line + offset,
                        "caller_symbol": current_method,
                        "owner_symbol": str(owner or "").strip(),
                        "callee_symbol": callee_name,
                        "snippet": stripped[:240],
                    }
                )
            if "." in line or "::" in line or "->" in line:
                continue
            for direct in _DIRECT_CALL_RE.findall(line):
                callee_name = str(direct or "").strip()
                if callee_name.lower() in _CALL_KEYWORDS:
                    continue
                if _is_generic_external_symbol(callee_name):
                    continue
                key = (path.lower(), current_method.lower(), callee_name.lower(), start_line + offset)
                if key in seen:
                    continue
                seen.add(key)
                observations.append(
                    {
                        "path": path,
                        "line": start_line + offset,
                        "caller_symbol": current_method,
                        "owner_symbol": "",
                        "callee_symbol": callee_name,
                        "snippet": stripped[:240],
                    }
                )
    return observations[:20]


def _collect_graph_symbols(local_overlay: Dict[str, Any]) -> List[str]:
    graph = extract_workspace_graph(local_overlay)
    graph_state = dict(graph.get("graph_state") or {}) if isinstance(graph.get("graph_state"), dict) else {}
    candidates: List[str] = []
    for token in (
        graph.get("target_symbol"),
        graph_state.get("anchor_symbol"),
        graph_state.get("focus_symbol"),
        graph_state.get("base_symbol"),
    ):
        if _is_generic_external_symbol(str(token or "")):
            continue
        candidates.append(str(token or ""))
    for collection in (
        graph.get("nodes") or [],
        graph_state.get("chain") or [],
        graph_state.get("frontiers") or [],
    ):
        for item in list(collection):
            if not isinstance(item, dict):
                continue
            for token in (item.get("symbol"), item.get("base_symbol"), item.get("via")):
                normalized = str(token or "").strip()
                if _is_generic_external_symbol(normalized):
                    continue
                candidates.append(normalized)
    frontier = graph_state.get("frontier")
    if isinstance(frontier, dict):
        for token in (frontier.get("symbol"), frontier.get("base_symbol"), frontier.get("via")):
            normalized = str(token or "").strip()
            if _is_generic_external_symbol(normalized):
                continue
            candidates.append(normalized)
    return _dedupe_tokens(candidates, limit=10)


def _score_primary_paths(
    local_overlay: Dict[str, Any],
    read_evidence: List[Dict[str, Any]],
    trace_relations: List[Dict[str, Any]],
) -> List[str]:
    graph = extract_workspace_graph(local_overlay)
    selected_path = _normalize_path(local_overlay.get("selected_file_path"))
    focus_path = _normalize_path(graph.get("focus_file"))
    core_files = {_normalize_path(item) for item in list(graph.get("core_files") or []) if _normalize_path(item)}
    supporting_files = {_normalize_path(item) for item in list(graph.get("supporting_files") or []) if _normalize_path(item)}
    candidate_paths = {_normalize_path(item.get("path")) for item in list(read_evidence or []) if _normalize_path(item.get("path"))}
    scores: Dict[str, float] = {path: 0.0 for path in candidate_paths}

    for path in candidate_paths:
        if path == selected_path:
            scores[path] += 120.0
        if path == focus_path:
            scores[path] += 90.0
        if path in core_files:
            scores[path] += 36.0
        if path in supporting_files:
            scores[path] += 12.0
        scores[path] += 2.0 * max(
            _shared_prefix_depth(path, selected_path),
            _shared_prefix_depth(path, focus_path),
        )

    for item in list(read_evidence or []):
        path = _normalize_path(item.get("path"))
        if not path or path not in scores:
            continue
        tool_name = str(item.get("tool") or "").strip().lower()
        scores[path] += {
            "read_symbol_span": 48.0,
            "symbol_neighborhood": 28.0,
            "selected_file": 24.0,
            "read_file": 14.0,
        }.get(tool_name, 10.0)
        if str(item.get("symbol") or "").strip():
            scores[path] += 8.0

    for item in list(trace_relations or []):
        path = _normalize_path(item.get("path"))
        if not path or path not in scores:
            continue
        tool_name = str(item.get("tool") or "").strip().lower()
        scores[path] += 8.0 if tool_name in {"find_callers", "find_references"} else 4.0
        if str(item.get("anchor_symbol") or "").strip():
            scores[path] += 2.0

    ordered = sorted(
        candidate_paths,
        key=lambda path: (
            -scores.get(path, 0.0),
            *_path_priority(path, focus_path=focus_path, selected_path=selected_path),
        ),
    )
    return [path for path in ordered if path][:3]


def _sort_reads(
    reads: List[Dict[str, Any]],
    *,
    local_overlay: Dict[str, Any],
    primary_paths: List[str],
) -> List[Dict[str, Any]]:
    graph = extract_workspace_graph(local_overlay)
    focus_path = _normalize_path(graph.get("focus_file"))
    selected_path = _normalize_path(local_overlay.get("selected_file_path"))
    primary_order = {path.lower(): index for index, path in enumerate(primary_paths)}
    return sorted(
        list(reads or []),
        key=lambda item: (
            0 if _normalize_path(item.get("path")).lower() in primary_order else 1,
            primary_order.get(_normalize_path(item.get("path")).lower(), 99),
            _READ_TOOL_PRIORITY.get(str(item.get("tool") or "").strip().lower(), 9),
            *_path_priority(
                _normalize_path(item.get("path")),
                focus_path=focus_path,
                selected_path=selected_path,
            ),
            int(item.get("round") or 0),
        ),
    )


def _select_trace_relations(
    trace_relations: List[Dict[str, Any]],
    *,
    primary_paths: List[str],
    primary_symbols: List[str],
    support_paths: List[str],
) -> List[Dict[str, Any]]:
    primary_path_set = {path.lower() for path in list(primary_paths or []) if path}
    support_path_set = {path.lower() for path in list(support_paths or []) if path}
    primary_symbol_set = {str(item or "").strip().lower() for item in list(primary_symbols or []) if str(item or "").strip()}
    scored: List[tuple[float, Dict[str, Any]]] = []
    seen = set()

    for relation in list(trace_relations or []):
        path = _normalize_path(relation.get("path"))
        anchor = str(relation.get("anchor_symbol") or "").strip()
        related = str(relation.get("related_symbol") or "").strip()
        score = 0.0
        if path.lower() in primary_path_set:
            score += 10.0
        elif path.lower() in support_path_set:
            score += 6.0
        if anchor.lower() in primary_symbol_set:
            score += 5.0
        if related.lower() in primary_symbol_set:
            score += 3.0
        if str(relation.get("tool") or "").strip().lower() in {"find_callers", "find_references"}:
            score += 2.0
        if score <= 0.0:
            continue
        key = (
            str(relation.get("tool") or "").strip().lower(),
            anchor.lower(),
            path.lower(),
            int(relation.get("line") or 0),
            related.lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        scored.append((score, relation))

    scored.sort(
        key=lambda item: (
            -item[0],
            0 if _normalize_path(item[1].get("path")).lower() in primary_path_set else 1,
            int(item[1].get("line") or 0),
        )
    )
    return [relation for _, relation in scored[:12]]


def _select_support_reads(
    reads: List[Dict[str, Any]],
    *,
    local_overlay: Dict[str, Any],
    primary_paths: List[str],
    primary_symbols: List[str],
    trace_relations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    primary_path_set = {path.lower() for path in list(primary_paths or []) if path}
    primary_symbol_set = {str(item or "").strip().lower() for item in list(primary_symbols or []) if str(item or "").strip()}
    graph = extract_workspace_graph(local_overlay)
    focus_path = _normalize_path(graph.get("focus_file"))
    selected_path = _normalize_path(local_overlay.get("selected_file_path"))
    scored: List[tuple[float, Dict[str, Any]]] = []
    seen = set()

    relation_by_path: Dict[str, float] = {}
    relation_by_anchor: Dict[str, float] = {}
    for relation in list(trace_relations or []):
        path = _normalize_path(relation.get("path"))
        anchor = str(relation.get("anchor_symbol") or "").strip()
        if path:
            relation_by_path[path.lower()] = relation_by_path.get(path.lower(), 0.0) + 1.0
        if anchor:
            relation_by_anchor[anchor.lower()] = relation_by_anchor.get(anchor.lower(), 0.0) + 1.0

    for read in list(reads or []):
        path = _normalize_path(read.get("path"))
        symbol = str(read.get("symbol") or "").strip()
        if not path or path.lower() in primary_path_set:
            continue
        score = 0.0
        score += 4.0 * relation_by_path.get(path.lower(), 0.0)
        score += 3.0 * relation_by_anchor.get(symbol.lower(), 0.0)
        if symbol.lower() in primary_symbol_set:
            score += 5.0
        score += 1.0 * max(
            _shared_prefix_depth(path, selected_path),
            _shared_prefix_depth(path, focus_path),
        )
        score += {
            "read_symbol_span": 4.0,
            "symbol_neighborhood": 2.0,
            "read_file": 1.0,
            "selected_file": 0.0,
        }.get(str(read.get("tool") or "").strip().lower(), 0.0)
        if score <= 0.0:
            continue
        key = (
            path.lower(),
            str(read.get("line_range") or "").strip(),
            str(read.get("tool") or "").strip().lower(),
            symbol.lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        scored.append((score, read))

    scored.sort(
        key=lambda item: (
            -item[0],
            _READ_TOOL_PRIORITY.get(str(item[1].get("tool") or "").strip().lower(), 9),
            *_path_priority(
                _normalize_path(item[1].get("path")),
                focus_path=focus_path,
                selected_path=selected_path,
            ),
        )
    )
    return [item for _, item in scored[:4]]


def _extract_grounded_symbols(
    *,
    local_overlay: Dict[str, Any],
    primary_reads: List[Dict[str, Any]],
    support_reads: List[Dict[str, Any]],
    flow_observations: List[Dict[str, Any]],
    trace_relations: List[Dict[str, Any]],
    engine_windows: List[Dict[str, Any]],
) -> List[str]:
    tokens: List[str] = []
    tokens.extend(_collect_graph_symbols(local_overlay))
    for read in list(primary_reads or []) + list(support_reads or []):
        symbol = str(read.get("symbol") or "").strip()
        if symbol and not _is_generic_external_symbol(symbol):
            tokens.append(symbol)
    for item in list(flow_observations or []):
        for token in (item.get("caller_symbol"), item.get("owner_symbol"), item.get("callee_symbol")):
            normalized = str(token or "").strip()
            if normalized and not _is_generic_external_symbol(normalized):
                tokens.append(normalized)
    for relation in list(trace_relations or []):
        for token in (relation.get("anchor_symbol"), relation.get("related_symbol")):
            normalized = str(token or "").strip()
            if normalized and not _is_generic_external_symbol(normalized):
                tokens.append(normalized)
    for window in list(engine_windows or []):
        symbol = str(window.get("symbol") or "").strip()
        if symbol and not _is_generic_external_symbol(symbol):
            tokens.append(symbol)
    return _dedupe_tokens(tokens, limit=28)


def _extract_external_symbol_candidates(
    *,
    local_overlay: Dict[str, Any],
    primary_symbols: List[str],
    flow_observations: List[Dict[str, Any]],
    trace_relations: List[Dict[str, Any]],
) -> List[str]:
    grounded = {str(item or "").strip().lower() for item in list(primary_symbols or []) if str(item or "").strip()}
    scores: Dict[str, float] = {}
    for item in list(flow_observations or []):
        callee = str(item.get("callee_symbol") or "").strip()
        owner = str(item.get("owner_symbol") or "").strip()
        if callee and callee.lower() not in grounded and not _is_generic_external_symbol(callee):
            scores[callee] = scores.get(callee, 0.0) + 7.0
        if owner and owner not in {"this", "base"} and owner.lower() not in grounded and not _is_generic_external_symbol(owner):
            scores[owner] = scores.get(owner, 0.0) + 2.0
    for relation in list(trace_relations or []):
        for token in (relation.get("anchor_symbol"), relation.get("related_symbol")):
            normalized = str(token or "").strip()
            if not normalized or normalized.lower() in grounded or _is_generic_external_symbol(normalized):
                continue
            scores[normalized] = scores.get(normalized, 0.0) + 2.0
    graph = extract_workspace_graph(local_overlay)
    graph_state = dict(graph.get("graph_state") or {}) if isinstance(graph.get("graph_state"), dict) else {}
    frontier_items: List[Dict[str, Any]] = []
    frontier = graph_state.get("frontier")
    if isinstance(frontier, dict):
        frontier_items.append(frontier)
    for item in list(graph_state.get("frontiers") or []):
        if isinstance(item, dict):
            frontier_items.append(item)
    for item in frontier_items[:6]:
        for token in (item.get("symbol"), item.get("base_symbol"), item.get("via")):
            normalized = _maybe_symbol(token)
            if not normalized or normalized.lower() in grounded or _is_generic_external_symbol(normalized):
                continue
            scores[normalized] = scores.get(normalized, 0.0) + 3.0
    ordered = sorted(scores.items(), key=lambda item: (-item[1], -len(item[0]), item[0].lower()))
    return [token for token, score in ordered if score >= 3.0][:2]


def _build_evidence_pack(
    *,
    question: str,
    local_overlay: Dict[str, Any],
    engine_windows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    read_evidence = _collect_local_reads(local_overlay)
    trace_relations = _collect_trace_relations(local_overlay)
    primary_paths = _score_primary_paths(local_overlay, read_evidence, trace_relations)
    ordered_reads = _sort_reads(read_evidence, local_overlay=local_overlay, primary_paths=primary_paths)
    primary_path_set = {path.lower() for path in list(primary_paths or []) if path}
    primary_reads = [read for read in ordered_reads if _normalize_path(read.get("path")).lower() in primary_path_set][:5]
    flow_observations = _extract_flow_observations(primary_reads, local_overlay)

    primary_symbol_tokens: List[str] = []
    primary_symbol_tokens.extend(_collect_graph_symbols(local_overlay))
    for read in list(primary_reads or []):
        symbol = str(read.get("symbol") or "").strip()
        if symbol and not _is_generic_external_symbol(symbol):
            primary_symbol_tokens.append(symbol)
    for item in list(flow_observations or []):
        for token in (item.get("caller_symbol"), item.get("owner_symbol"), item.get("callee_symbol")):
            normalized = str(token or "").strip()
            if normalized and not _is_generic_external_symbol(normalized):
                primary_symbol_tokens.append(normalized)
    primary_symbols = _dedupe_tokens(primary_symbol_tokens, limit=18)

    support_reads = _select_support_reads(
        ordered_reads,
        local_overlay=local_overlay,
        primary_paths=primary_paths,
        primary_symbols=primary_symbols,
        trace_relations=trace_relations,
    )
    support_paths = _dedupe_tokens([_normalize_path(item.get("path")) for item in list(support_reads or [])], limit=6)
    selected_trace_relations = _select_trace_relations(
        trace_relations,
        primary_paths=primary_paths,
        primary_symbols=primary_symbols,
        support_paths=support_paths,
    )
    grounded_symbols = _extract_grounded_symbols(
        local_overlay=local_overlay,
        primary_reads=primary_reads,
        support_reads=support_reads,
        flow_observations=flow_observations,
        trace_relations=selected_trace_relations,
        engine_windows=engine_windows,
    )
    unresolved_external_symbols = _extract_external_symbol_candidates(
        local_overlay=local_overlay,
        primary_symbols=grounded_symbols,
        flow_observations=flow_observations,
        trace_relations=selected_trace_relations,
    )
    workspace_graph = extract_workspace_graph(local_overlay)
    grounding_report = build_workspace_grounding_report(
        workspace_graph,
        collect_grounded_overlay_paths(local_overlay),
    )
    allowed_paths = _dedupe_tokens(
        [
            *[_normalize_path(item.get("path")) for item in list(primary_reads or [])],
            *[_normalize_path(item.get("path")) for item in list(support_reads or [])],
            *[_normalize_path(item.get("path")) for item in list(engine_windows or [])],
        ],
        limit=12,
    )
    return {
        "question": question,
        "anchor": {
            "selected_path": _normalize_path(local_overlay.get("selected_file_path")),
            "focus_path": _normalize_path(workspace_graph.get("focus_file")),
            "primary_paths": primary_paths,
            "primary_symbols": primary_symbols,
        },
        "grounding_report": {
            "focus_path": grounding_report.get("focus_path"),
            "focus_grounded": grounding_report.get("focus_grounded"),
            "direct_path_count": grounding_report.get("direct_path_count"),
            "open_frontier_count": grounding_report.get("open_frontier_count"),
            "graph_closed": grounding_report.get("graph_closed"),
        },
        "primary_reads": primary_reads,
        "support_reads": support_reads,
        "flow_observations": flow_observations[:12],
        "trace_relations": selected_trace_relations[:12],
        "engine_windows": list(engine_windows or [])[:2],
        "allowed_paths": allowed_paths,
        "grounded_symbols": grounded_symbols,
        "unresolved_external_symbols": unresolved_external_symbols,
    }


async def _maybe_await(callback, *args, **kwargs) -> None:
    if callback is None:
        return
    result = callback(*args, **kwargs)
    if asyncio.iscoroutine(result):
        await result


async def _collect_engine_windows(
    *,
    redis,
    code_tools,
    session_id: str,
    local_overlay: Dict[str, Any],
    evidence_pack: Dict[str, Any],
    max_chars: int,
    max_line_span: int,
    tool_callback: ToolCallback = None,
) -> Dict[str, Any]:
    local_prefixes = _collect_local_prefixes(local_overlay)
    symbol_candidates = list(evidence_pack.get("unresolved_external_symbols") or [])[:2]
    engine_windows: List[Dict[str, Any]] = []
    tool_calls: List[Dict[str, Any]] = []
    seen_paths = set()

    for symbol in symbol_candidates:
        cache_key = symbol.lower()
        cached_matches = _ENGINE_SYMBOL_MATCH_CACHE.get(cache_key)
        if cached_matches is None:
            symbol_result = await find_symbol(
                redis,
                code_tools,
                symbol=symbol,
                limit=8,
                session_id=session_id,
            )
            symbol_matches = [dict(item) for item in list(symbol_result.get("matches") or [])]
            _ENGINE_SYMBOL_MATCH_CACHE[cache_key] = list(symbol_matches)
        else:
            symbol_matches = [dict(item) for item in cached_matches]
        filtered_matches = []
        for row in symbol_matches:
            path = _normalize_path(dict(row or {}).get("path") or "")
            if not path:
                continue
            path_prefix = _top_level_prefix(path)
            if path_prefix and path_prefix in local_prefixes:
                continue
            filtered_matches.append(dict(row))
        preview = json.dumps(
            {
                "symbol": symbol,
                "match_count": len(filtered_matches),
                "matches": filtered_matches[:4],
            },
            ensure_ascii=False,
        )[:500]
        tool_calls.append(
            {
                "round": 0,
                "tool": "find_symbol",
                "input": {"symbol": symbol, "limit": 8},
                "output_preview": preview,
            }
        )
        await _maybe_await(tool_callback, "find_symbol", {"symbol": symbol, "limit": 8}, preview)
        if not filtered_matches:
            continue

        for match in filtered_matches[:2]:
            path = _normalize_path(match.get("path") or "")
            if not path or path.lower() in seen_paths:
                continue
            seen_paths.add(path.lower())
            start_line, end_line = _build_engine_read_window(str(match.get("line_range") or ""), max_line_span)
            read_result = read_code_lines(
                code_tools,
                path=path,
                start_line=start_line,
                end_line=end_line,
                max_line_span=max_line_span,
                max_chars=max_chars,
            )
            read_preview = json.dumps(
                {
                    "path": read_result.get("path"),
                    "found": bool(read_result.get("found")),
                    "line_range": read_result.get("line_range"),
                },
                ensure_ascii=False,
            )[:500]
            tool_calls.append(
                {
                    "round": 0,
                    "tool": "read",
                    "input": {"path": path, "start_line": start_line, "end_line": end_line},
                    "output_preview": read_preview,
                }
            )
            await _maybe_await(
                tool_callback,
                "read",
                {"path": path, "start_line": start_line, "end_line": end_line},
                read_preview,
            )
            if not bool(read_result.get("found")):
                continue
            engine_windows.append(
                {
                    "path": str(read_result.get("path") or path),
                    "line_range": str(read_result.get("line_range") or f"{start_line}-{end_line}"),
                    "content": str(read_result.get("content") or ""),
                    "symbol": symbol,
                    "source_kind": "engine_baseline",
                    "tool": "engine_read",
                }
            )
            if len(engine_windows) >= 2:
                return {"windows": engine_windows, "tool_calls": tool_calls}

    return {"windows": engine_windows, "tool_calls": tool_calls}


def _window_payload(window: Dict[str, Any], *, max_chars: int = 1200) -> Dict[str, Any]:
    return {
        "path": str(window.get("path") or "").strip(),
        "line_range": str(window.get("line_range") or "").strip(),
        "tool": str(window.get("tool") or window.get("source_kind") or "").strip(),
        "content": str(window.get("content") or "")[:max_chars],
        "symbol": str(window.get("symbol") or "").strip(),
        "source_kind": str(window.get("source_kind") or "").strip(),
    }


def _build_prompt_payload(
    *,
    question: str,
    local_overlay: Dict[str, Any],
    engine_windows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    pack = _build_evidence_pack(
        question=question,
        local_overlay=local_overlay,
        engine_windows=engine_windows,
    )
    return {
        "question": question,
        "anchor": dict(pack.get("anchor") or {}),
        "grounding_report": dict(pack.get("grounding_report") or {}),
        "allowed_paths": list(pack.get("allowed_paths") or []),
        "grounded_symbols": list(pack.get("grounded_symbols") or []),
        "primary_reads": [_window_payload(window, max_chars=1600) for window in list(pack.get("primary_reads") or [])],
        "support_reads": [_window_payload(window, max_chars=900) for window in list(pack.get("support_reads") or [])],
        "flow_observations": list(pack.get("flow_observations") or []),
        "trace_relations": list(pack.get("trace_relations") or []),
        "engine_windows": [_window_payload(window, max_chars=800) for window in list(pack.get("engine_windows") or [])],
        "evidence_summary": {
            "primary_read_count": len(list(pack.get("primary_reads") or [])),
            "support_read_count": len(list(pack.get("support_reads") or [])),
            "flow_observation_count": len(list(pack.get("flow_observations") or [])),
            "trace_relation_count": len(list(pack.get("trace_relations") or [])),
            "engine_window_count": len(list(pack.get("engine_windows") or [])),
        },
    }


def _find_ungrounded_symbols(answer: str, allowed_symbols: List[str]) -> List[str]:
    allowed = {str(item or "").strip().lower() for item in list(allowed_symbols or []) if str(item or "").strip()}
    ungrounded: List[str] = []
    seen = set()
    for token in _SYMBOL_TOKEN_RE.findall(str(answer or "")):
        normalized = str(token or "").strip()
        lowered = normalized.lower()
        if not normalized or lowered in allowed or lowered in seen:
            continue
        if _is_generic_external_symbol(normalized):
            continue
        seen.add(lowered)
        ungrounded.append(normalized)
    return ungrounded


async def _generate_answer(
    *,
    vllm_client,
    model_name: str,
    max_tokens: int,
    temperature: float,
    system_prompt_seed: str,
    prompt_payload: Dict[str, Any],
    token_callback: TokenCallback = None,
) -> Dict[str, Any]:
    if vllm_client is None:
        return {"text": "", "truncated": False}

    system_prompt = (
        (str(system_prompt_seed or "").strip() + "\n\n") if str(system_prompt_seed or "").strip() else ""
    ) + (
        "You are writing a grounded Korean code explanation from a structured evidence pack.\n"
        "Narrative priority is: anchor.primary_paths -> primary_reads -> flow_observations -> trace_relations -> support_reads -> engine_windows.\n"
        "Explain only relations that are explicitly supported by those structures.\n"
        "Do not turn support_reads into the main flow unless a flow_observation or trace_relation links them to the anchor.\n"
        "If the evidence only confirms one slice such as registration, persistence, loading, or adapter wiring, describe that slice precisely instead of claiming the whole feature flow.\n"
        "Use engine_windows only when they directly explain an unresolved local symbol.\n"
        "Never mention file paths, symbols, or call chains that are not present in the provided evidence.\n"
        "If the grounded local evidence does not fully close the flow, say that the remaining upstream or downstream relation was not confirmed.\n"
        "Use only paths from allowed_paths and only code-like identifiers from grounded_symbols.\n"
        "Answer in Korean with compact prose and short bullets only when needed.\n"
    )
    user_prompt = (
        "Grounded code explanation payload:\n"
        f"{json.dumps(prompt_payload, ensure_ascii=False)}\n\n"
        "Write the final answer now."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    extra_body = build_chat_template_extra_body(
        False if token_callback is not None else rag_config.model_native_generation_enable_thinking()
    )
    if token_callback is not None:
        return await stream_chat_completion_text_with_meta(
            model=model_name,
            messages=messages,
            max_tokens=max(256, min(int(max_tokens or 1400), 2200)),
            temperature=max(0.0, min(float(temperature), 0.3)),
            client=vllm_client,
            extra_body=extra_body,
            on_token=token_callback,
        )

    completion = await asyncio.to_thread(
        safe_chat_completion_create,
        model=model_name,
        messages=messages,
        max_tokens=max(256, min(int(max_tokens or 1400), 2200)),
        temperature=max(0.0, min(float(temperature), 0.3)),
        client=vllm_client,
        extra_body=extra_body,
    )
    if not completion.choices:
        return {"text": "", "truncated": False}
    return {
        "text": str(completion.choices[0].message.content or "").strip(),
        "truncated": extract_completion_finish_reason(completion) == "length",
    }


async def _repair_answer_scope(
    *,
    vllm_client,
    model_name: str,
    original_answer: str,
    prompt_payload: Dict[str, Any],
    max_tokens: int,
) -> str:
    if vllm_client is None:
        return str(original_answer or "").strip()
    system_prompt = (
        "You are repairing a Korean code explanation so every file path, symbol, and flow step stays grounded.\n"
        "Keep the narrative centered on anchor.primary_paths, primary_reads, and flow_observations.\n"
        "Use trace_relations, support_reads, and engine_windows only when they directly support that main flow.\n"
        "Use only allowed_paths for file mentions and only grounded_symbols for code-like identifiers.\n"
        "Remove or soften unsupported claims instead of inventing details.\n"
    )
    user_prompt = (
        "Grounded payload:\n"
        f"{json.dumps(prompt_payload, ensure_ascii=False)}\n\n"
        "Draft answer:\n"
        f"{original_answer}\n\n"
        "Rewrite the answer now."
    )
    completion = await asyncio.to_thread(
        safe_chat_completion_create,
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max(256, min(int(max_tokens or 1400), 1800)),
        temperature=0.0,
        client=vllm_client,
        extra_body=build_chat_template_extra_body(False),
    )
    if not completion.choices:
        return str(original_answer or "").strip()
    return str(completion.choices[0].message.content or "").strip() or str(original_answer or "").strip()


async def run_local_overlay_code_explain(
    *,
    chat_deps,
    accumulator,
    clean_message: str,
    local_overlay: Dict[str, Any],
    model_name: str,
    max_tokens: int,
    temperature: float,
    system_prompt_seed: str,
    session_id: str,
    routing_profile: Dict[str, Any],
    max_chars: int,
    max_line_span: int,
    progress_callback: ProgressCallback = None,
    token_callback: TokenCallback = None,
    tool_callback: ToolCallback = None,
) -> Optional[Dict[str, Any]]:
    local_reads = _collect_local_reads(local_overlay)
    if not local_reads:
        return None

    await _maybe_await(
        progress_callback,
        {
            "phase": "retrieve",
            "message": "로컬 워크스페이스 근거를 우선 정리하는 중..",
            "tool": "local_overlay",
        },
    )

    initial_pack = _build_evidence_pack(
        question=clean_message,
        local_overlay=local_overlay,
        engine_windows=[],
    )

    engine_result = await _collect_engine_windows(
        redis=getattr(chat_deps, "redis", None),
        code_tools=chat_deps.code_tools,
        session_id=session_id,
        local_overlay=local_overlay,
        evidence_pack=initial_pack,
        max_chars=max_chars,
        max_line_span=max_line_span,
        tool_callback=tool_callback,
    )
    engine_windows = list(engine_result.get("windows") or [])
    for window in engine_windows:
        accumulator.add_code_window(
            {
                "path": window.get("path"),
                "line_range": window.get("line_range"),
                "content": window.get("content", ""),
            }
        )

    await _maybe_await(
        progress_callback,
        {
            "phase": "answer",
            "message": "로컬 근거 중심으로 코드 흐름을 정리하는 중..",
            "source_count": len(local_reads) + len(engine_windows),
        },
    )
    prompt_payload = _build_prompt_payload(
        question=clean_message,
        local_overlay=local_overlay,
        engine_windows=engine_windows,
    )
    answer_result = await _generate_answer(
        vllm_client=getattr(chat_deps, "vllm_client", None),
        model_name=model_name,
        max_tokens=max_tokens,
        temperature=temperature,
        system_prompt_seed=system_prompt_seed,
        prompt_payload=prompt_payload,
        token_callback=token_callback,
    )
    answer = str(answer_result.get("text") or "").strip()
    if not answer:
        return None
    if token_callback is None:
        allowed_paths = [normalize_source_path(item) for item in list(prompt_payload.get("allowed_paths") or []) if str(item or "").strip()]
        grounded_symbols = list(prompt_payload.get("grounded_symbols") or [])
        ungrounded_paths = find_ungrounded_source_mentions(answer, allowed_paths)
        ungrounded_symbols = _find_ungrounded_symbols(answer, grounded_symbols)
        if ungrounded_paths or ungrounded_symbols:
            answer = await _repair_answer_scope(
                vllm_client=getattr(chat_deps, "vllm_client", None),
                model_name=model_name,
                original_answer=answer,
                prompt_payload=prompt_payload,
                max_tokens=max_tokens,
            )

    results = accumulator.to_results()
    return {
        "answer": answer,
        "results": results,
        "sources": build_sources(results),
        "tool_calls": list(engine_result.get("tool_calls") or []),
        "answer_truncated": bool(answer_result.get("truncated")),
        "mode": "local_overlay_code_explain",
        "profile": routing_profile,
    }


__all__ = ["run_local_overlay_code_explain"]

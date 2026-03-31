import asyncio
import json
import re
from typing import Any, Awaitable, Callable, Dict, List, Optional

from ..question_contract import normalize_question_contract
from ..workspace_graph import (
    build_workspace_grounding_report,
    collect_grounded_overlay_paths,
    extract_workspace_graph,
)
from ...tools.query_terms import identifier_structure_score
from ...tools.runtime import find_symbol, read_code_lines


ProgressCallback = Optional[Callable[[Dict[str, Any]], Awaitable[None] | None]]
ToolCallback = Optional[Callable[[str, Dict[str, Any], str], Awaitable[None] | None]]

_CODE_LIKE_SYMBOL_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
_METHOD_DECL_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|static|virtual|override|sealed|partial|async)\s+)+"
    r"[\w<>\[\],\s]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("
)
_MEMBER_CALL_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:\.|::|->)\s*([A-Za-z_][A-Za-z0-9_]*)\s*\("
)
_DIRECT_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_QUESTION_ASCII_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
_QUESTION_HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]{2,}")
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


def _dedupe_tokens(tokens: List[str], *, limit: int | None = None) -> List[str]:
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
        if limit is not None and len(ordered) >= max(1, int(limit)):
            break
    return ordered


def _split_symbol_parts(value: Any) -> List[str]:
    parts = re.split(r"_|(?=[A-Z])", str(value or "").strip())
    return [str(item or "").strip() for item in parts if str(item or "").strip()]


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
            for item in items[:24]:
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

    return relations[:64]


def _extract_flow_observations(
    local_windows: List[Dict[str, Any]],
    local_overlay: Dict[str, Any],
    *,
    limit: int,
) -> List[Dict[str, Any]]:
    observations: List[Dict[str, Any]] = []
    seen = set()
    for window in _sort_local_windows(local_windows, local_overlay):
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
                if len(observations) >= limit:
                    return observations
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
                if len(observations) >= limit:
                    return observations
    return observations


def _collect_graph_symbols(local_overlay: Dict[str, Any], *, limit: int) -> List[str]:
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
    return _dedupe_tokens(candidates, limit=limit)


def _score_primary_paths(
    local_overlay: Dict[str, Any],
    read_evidence: List[Dict[str, Any]],
    trace_relations: List[Dict[str, Any]],
) -> List[str]:
    graph = extract_workspace_graph(local_overlay)
    selected_path = _normalize_path(local_overlay.get("selected_file_path"))
    focus_path = _normalize_path(graph.get("focus_file"))
    selected_matches_focus = bool(selected_path and focus_path and selected_path.lower() == focus_path.lower())
    core_files = {_normalize_path(item) for item in list(graph.get("core_files") or []) if _normalize_path(item)}
    supporting_files = {_normalize_path(item) for item in list(graph.get("supporting_files") or []) if _normalize_path(item)}
    candidate_paths = {_normalize_path(item.get("path")) for item in list(read_evidence or []) if _normalize_path(item.get("path"))}
    scores: Dict[str, float] = {path: 0.0 for path in candidate_paths}

    for path in candidate_paths:
        if path == selected_path:
            scores[path] += 120.0 if selected_matches_focus else 12.0
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
    return [path for path in ordered if path][:4]


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
    limit: int,
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
    return [relation for _, relation in scored[:limit]]


def _select_support_reads(
    reads: List[Dict[str, Any]],
    *,
    local_overlay: Dict[str, Any],
    primary_paths: List[str],
    primary_symbols: List[str],
    trace_relations: List[Dict[str, Any]],
    limit: int,
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
    return [item for _, item in scored[:limit]]


def _extract_grounded_symbols(
    *,
    local_overlay: Dict[str, Any],
    primary_reads: List[Dict[str, Any]],
    support_reads: List[Dict[str, Any]],
    flow_observations: List[Dict[str, Any]],
    trace_relations: List[Dict[str, Any]],
    engine_windows: List[Dict[str, Any]],
    limit: int,
) -> List[str]:
    tokens: List[str] = []
    tokens.extend(_collect_graph_symbols(local_overlay, limit=max(limit, 16)))
    for read in list(primary_reads or []) + list(support_reads or []):
        symbol = str(read.get("symbol") or "").strip()
        if symbol and not _is_generic_external_symbol(symbol):
            tokens.append(symbol)
    for item in list(flow_observations or []):
        caller_symbol = str(item.get("caller_symbol") or "").strip()
        if caller_symbol and not _is_generic_external_symbol(caller_symbol):
            tokens.append(caller_symbol)
    for relation in list(trace_relations or []):
        for token in (relation.get("anchor_symbol"), relation.get("related_symbol")):
            normalized = str(token or "").strip()
            if normalized and not _is_generic_external_symbol(normalized):
                tokens.append(normalized)
    for window in list(engine_windows or []):
        symbol = str(window.get("symbol") or "").strip()
        if symbol and not _is_generic_external_symbol(symbol):
            tokens.append(symbol)
    return _dedupe_tokens(tokens, limit=limit)


def _resolve_frontier_budget(
    *,
    question_contract: Dict[str, Any] | None,
    local_overlay: Dict[str, Any],
    read_evidence: List[Dict[str, Any]],
    trace_relations: List[Dict[str, Any]],
) -> Dict[str, int]:
    normalized_contract = normalize_question_contract(
        question_contract,
        workspace_overlay_present=bool(local_overlay.get("present")),
    )
    configured = dict(normalized_contract.get("budget") or {})
    graph = extract_workspace_graph(local_overlay)
    graph_state = dict(graph.get("graph_state") or {}) if isinstance(graph.get("graph_state"), dict) else {}
    open_frontiers = list(graph_state.get("frontiers") or [])
    if isinstance(graph_state.get("frontier"), dict):
        open_frontiers = [dict(graph_state.get("frontier") or {}), *open_frontiers]
    frontier_count = len(open_frontiers)
    node_count = len(list(graph.get("nodes") or []))
    trace_count = len(list(trace_relations or []))
    read_count = len(list(read_evidence or []))
    frontier_score = max(
        1,
        frontier_count * 4
        + min(node_count, 8) * 2
        + min(trace_count, 18) // 2
        + min(read_count, 12) // 2,
    )

    configured_symbol_cap = max(3, int(configured.get("max_engine_symbol_candidates") or 6))
    configured_window_cap = max(2, int(configured.get("max_engine_windows") or configured_symbol_cap))

    return {
        "frontier_score": frontier_score,
        "primary_read_cap": min(6, max(3, 2 + frontier_score // 6)),
        "support_read_cap": min(8, max(3, 2 + frontier_score // 5)),
        "flow_observation_cap": min(18, max(8, 6 + frontier_score // 4)),
        "trace_relation_cap": min(18, max(8, 6 + frontier_score // 3)),
        "grounded_symbol_cap": min(36, max(18, 12 + frontier_score)),
        "open_frontier_symbol_cap": min(configured_symbol_cap, max(3, 2 + frontier_score // 4)),
        "unresolved_edge_cap": min(12, max(4, 2 + frontier_score // 4)),
        "engine_match_cap": min(6, max(2, 1 + frontier_score // 5)),
        "engine_window_cap": min(configured_window_cap, max(2, 2 + frontier_score // 5)),
        "next_search_candidate_cap": min(12, max(4, 3 + frontier_score // 4)),
    }


def _merge_symbol_candidate(
    candidates: Dict[str, Dict[str, Any]],
    *,
    symbol: Any,
    score: float,
    reason: str,
    source_kind: str,
    path: Any = "",
    caller_symbol: Any = "",
    callee_symbol: Any = "",
    line: Any = 0,
) -> None:
    normalized_symbol = _maybe_symbol(symbol)
    if not normalized_symbol or _is_generic_external_symbol(normalized_symbol):
        return
    key = normalized_symbol.lower()
    entry = candidates.setdefault(
        key,
        {
            "symbol": normalized_symbol,
            "score": 0.0,
            "reasons": [],
            "source_kinds": [],
            "path": "",
            "caller_symbol": "",
            "callee_symbol": "",
            "line": 0,
        },
    )
    entry["score"] = float(entry.get("score") or 0.0) + float(score or 0.0)
    if reason and reason not in entry["reasons"]:
        entry["reasons"].append(reason)
    if source_kind and source_kind not in entry["source_kinds"]:
        entry["source_kinds"].append(source_kind)
    if not str(entry.get("path") or "").strip():
        entry["path"] = _normalize_path(path)
    if not str(entry.get("caller_symbol") or "").strip():
        entry["caller_symbol"] = str(caller_symbol or "").strip()
    if not str(entry.get("callee_symbol") or "").strip():
        entry["callee_symbol"] = str(callee_symbol or "").strip()
    if not int(entry.get("line") or 0):
        try:
            entry["line"] = int(line or 0)
        except Exception:
            entry["line"] = 0


def _extract_open_frontier_symbol_candidates(
    *,
    local_overlay: Dict[str, Any],
    grounded_symbols: List[str],
    flow_observations: List[Dict[str, Any]],
    trace_relations: List[Dict[str, Any]],
    limit: int,
) -> List[Dict[str, Any]]:
    grounded = {str(item or "").strip().lower() for item in list(grounded_symbols or []) if str(item or "").strip()}
    candidates: Dict[str, Dict[str, Any]] = {}

    for item in list(flow_observations or []):
        caller = str(item.get("caller_symbol") or "").strip()
        owner = str(item.get("owner_symbol") or "").strip()
        callee = str(item.get("callee_symbol") or "").strip()
        path = _normalize_path(item.get("path"))
        line = item.get("line") or 0
        if callee and callee.lower() not in grounded:
            _merge_symbol_candidate(
                candidates,
                symbol=callee,
                score=8.0,
                reason="unresolved callee from grounded local read",
                source_kind="flow_observation",
                path=path,
                caller_symbol=caller,
                callee_symbol=callee,
                line=line,
            )
        if owner and owner.lower() not in grounded and owner.lower() not in {"this", "base"}:
            _merge_symbol_candidate(
                candidates,
                symbol=owner,
                score=3.0,
                reason="unresolved owner from grounded local read",
                source_kind="flow_observation",
                path=path,
                caller_symbol=caller,
                callee_symbol=callee,
                line=line,
            )

    for relation in list(trace_relations or []):
        for token in (relation.get("anchor_symbol"), relation.get("related_symbol")):
            normalized = str(token or "").strip()
            if not normalized or normalized.lower() in grounded:
                continue
            _merge_symbol_candidate(
                candidates,
                symbol=normalized,
                score=2.0,
                reason="trace relation exposes unresolved symbol",
                source_kind=str(relation.get("tool") or "trace_relation"),
                path=relation.get("path"),
                line=relation.get("line"),
            )

    graph = extract_workspace_graph(local_overlay)
    graph_state = dict(graph.get("graph_state") or {}) if isinstance(graph.get("graph_state"), dict) else {}
    frontier_items: List[Dict[str, Any]] = []
    if isinstance(graph_state.get("frontier"), dict):
        frontier_items.append(dict(graph_state.get("frontier") or {}))
    for item in list(graph_state.get("frontiers") or []):
        if isinstance(item, dict):
            frontier_items.append(dict(item))
    for item in frontier_items:
        for token in (item.get("symbol"), item.get("base_symbol"), item.get("via")):
            normalized = _maybe_symbol(token)
            if not normalized or normalized.lower() in grounded:
                continue
            _merge_symbol_candidate(
                candidates,
                symbol=normalized,
                score=4.0,
                reason="workspace frontier exposes unresolved symbol",
                source_kind="workspace_graph",
                path=item.get("path"),
                line=item.get("line"),
            )

    ordered = sorted(
        candidates.values(),
        key=lambda item: (
            -float(item.get("score") or 0.0),
            -len(str(item.get("symbol") or "")),
            str(item.get("symbol") or "").lower(),
        ),
    )
    out: List[Dict[str, Any]] = []
    for item in ordered[:limit]:
        out.append(
            {
                "symbol": str(item.get("symbol") or "").strip(),
                "score": float(item.get("score") or 0.0),
                "reason": "; ".join(list(item.get("reasons") or [])[:2]),
                "source_kind": str((list(item.get("source_kinds") or []) or ["frontier"])[0]),
                "path": _normalize_path(item.get("path")),
                "caller_symbol": str(item.get("caller_symbol") or "").strip(),
                "callee_symbol": str(item.get("callee_symbol") or "").strip(),
                "line": int(item.get("line") or 0),
            }
        )
    return out


def _extract_unresolved_caller_callee_edges(
    *,
    flow_observations: List[Dict[str, Any]],
    grounded_symbols: List[str],
    primary_paths: List[str],
    limit: int,
) -> List[Dict[str, Any]]:
    grounded = {str(item or "").strip().lower() for item in list(grounded_symbols or []) if str(item or "").strip()}
    primary_path_set = {str(item or "").strip().lower() for item in list(primary_paths or []) if str(item or "").strip()}
    edges: List[Dict[str, Any]] = []
    seen = set()

    for item in list(flow_observations or []):
        path = _normalize_path(item.get("path"))
        caller = str(item.get("caller_symbol") or "").strip()
        owner = str(item.get("owner_symbol") or "").strip()
        callee = str(item.get("callee_symbol") or "").strip()
        unresolved_symbol = ""
        if callee and callee.lower() not in grounded:
            unresolved_symbol = callee
        elif owner and owner.lower() not in grounded and owner.lower() not in {"this", "base"}:
            unresolved_symbol = owner
        if not unresolved_symbol:
            continue
        key = (
            path.lower(),
            int(item.get("line") or 0),
            caller.lower(),
            owner.lower(),
            callee.lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        score = 8.0
        if path.lower() in primary_path_set:
            score += 3.0
        if caller:
            score += 1.0
        if callee and callee == unresolved_symbol:
            score += 2.0
        edges.append(
            {
                "path": path,
                "line": int(item.get("line") or 0),
                "caller_symbol": caller,
                "owner_symbol": owner,
                "callee_symbol": callee,
                "unresolved_symbol": unresolved_symbol,
                "snippet": str(item.get("snippet") or "").strip()[:240],
                "score": score,
            }
        )

    edges.sort(
        key=lambda item: (
            -float(item.get("score") or 0.0),
            0 if str(item.get("path") or "").strip().lower() in primary_path_set else 1,
            int(item.get("line") or 0),
        )
    )
    return edges[:limit]


def _extract_question_search_terms(question: str, *, limit: int) -> List[str]:
    tokens: List[str] = []
    text = str(question or "").strip()
    for raw in _QUESTION_ASCII_RE.findall(text):
        token = str(raw or "").strip()
        if not token:
            continue
        tokens.append(token)
        for part in _split_symbol_parts(token):
            if len(part) >= 3:
                tokens.append(part.lower())
    for raw in _QUESTION_HANGUL_RE.findall(text):
        token = str(raw or "").strip()
        if len(token) >= 2:
            tokens.append(token)
    return _dedupe_tokens(tokens, limit=limit)


def _build_next_search_candidates(
    *,
    question: str,
    local_overlay: Dict[str, Any],
    open_frontier_symbol_candidates: List[Dict[str, Any]],
    unresolved_edges: List[Dict[str, Any]],
    limit: int,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()
    local_prefixes = _collect_local_prefixes(local_overlay)

    def _append(*, tool: str, query: str = "", symbol: str = "", reason: str = "", path: str = "") -> None:
        probe = str(symbol or query or "").strip()
        if not probe:
            return
        normalized_path = _normalize_path(path)
        path_prefix = _top_level_prefix(normalized_path)
        if path_prefix and path_prefix in local_prefixes:
            return
        key = (str(tool or "").strip().lower(), probe.lower(), normalized_path.lower())
        if key in seen:
            return
        seen.add(key)
        out.append(
            {
                "tool": str(tool or "").strip().lower(),
                "query": str(query or "").strip(),
                "symbol": str(symbol or "").strip(),
                "reason": str(reason or "").strip(),
                "path": normalized_path,
            }
        )

    for item in list(open_frontier_symbol_candidates or []):
        symbol = str(item.get("symbol") or "").strip()
        if symbol:
            _append(
                tool="find_symbol",
                symbol=symbol,
                reason=str(item.get("reason") or "").strip() or "open frontier symbol",
                path=str(item.get("path") or "").strip(),
            )
        if len(out) >= limit:
            return out[:limit]

    for item in list(unresolved_edges or []):
        caller = str(item.get("caller_symbol") or "").strip()
        callee = str(item.get("callee_symbol") or "").strip()
        unresolved_symbol = str(item.get("unresolved_symbol") or "").strip()
        path = str(item.get("path") or "").strip()
        if unresolved_symbol:
            _append(
                tool="find_symbol",
                symbol=unresolved_symbol,
                reason="close unresolved caller/callee edge",
                path=path,
            )
        if caller and callee:
            _append(
                tool="grep",
                query=f"{caller} {callee}",
                reason="probe caller/callee relation in grounded flow",
                path=path,
            )
        elif caller:
            _append(
                tool="grep",
                query=caller,
                reason="probe unresolved caller context",
                path=path,
            )
        if len(out) >= limit:
            return out[:limit]

    return out[:limit]


def _build_bootstrap_summary(pack: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "primary_read_count": len(list(pack.get("primary_reads") or [])),
        "support_read_count": len(list(pack.get("support_reads") or [])),
        "flow_observation_count": len(list(pack.get("flow_observations") or [])),
        "trace_relation_count": len(list(pack.get("trace_relations") or [])),
        "engine_window_count": len(list(pack.get("engine_windows") or [])),
        "open_frontier_symbol_count": len(list(pack.get("open_frontier_symbols") or [])),
        "unresolved_edge_count": len(list(pack.get("unresolved_caller_callee_edges") or [])),
    }


def _build_evidence_pack(
    *,
    question: str,
    local_overlay: Dict[str, Any],
    engine_windows: List[Dict[str, Any]],
    question_contract: Dict[str, Any] | None,
) -> Dict[str, Any]:
    read_evidence = _collect_local_reads(local_overlay)
    trace_relations = _collect_trace_relations(local_overlay)
    frontier_budget = _resolve_frontier_budget(
        question_contract=question_contract,
        local_overlay=local_overlay,
        read_evidence=read_evidence,
        trace_relations=trace_relations,
    )
    primary_paths = _score_primary_paths(local_overlay, read_evidence, trace_relations)
    ordered_reads = _sort_reads(read_evidence, local_overlay=local_overlay, primary_paths=primary_paths)
    primary_path_set = {path.lower() for path in list(primary_paths or []) if path}
    primary_reads = [
        read
        for read in ordered_reads
        if _normalize_path(read.get("path")).lower() in primary_path_set
    ][: int(frontier_budget.get("primary_read_cap") or 4)]
    initial_flow_observations = _extract_flow_observations(
        primary_reads,
        local_overlay,
        limit=int(frontier_budget.get("flow_observation_cap") or 12),
    )

    primary_symbol_tokens: List[str] = []
    primary_symbol_tokens.extend(_collect_graph_symbols(local_overlay, limit=16))
    for read in list(primary_reads or []):
        symbol = str(read.get("symbol") or "").strip()
        if symbol and not _is_generic_external_symbol(symbol):
            primary_symbol_tokens.append(symbol)
    for item in list(initial_flow_observations or []):
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
        limit=int(frontier_budget.get("support_read_cap") or 4),
    )
    flow_observations = _extract_flow_observations(
        [*list(primary_reads or []), *list(support_reads or [])],
        local_overlay,
        limit=int(frontier_budget.get("flow_observation_cap") or 12),
    )
    support_paths = _dedupe_tokens([_normalize_path(item.get("path")) for item in list(support_reads or [])], limit=8)
    selected_trace_relations = _select_trace_relations(
        trace_relations,
        primary_paths=primary_paths,
        primary_symbols=primary_symbols,
        support_paths=support_paths,
        limit=int(frontier_budget.get("trace_relation_cap") or 12),
    )
    grounded_symbols = _extract_grounded_symbols(
        local_overlay=local_overlay,
        primary_reads=primary_reads,
        support_reads=support_reads,
        flow_observations=flow_observations,
        trace_relations=selected_trace_relations,
        engine_windows=engine_windows,
        limit=int(frontier_budget.get("grounded_symbol_cap") or 24),
    )
    open_frontier_symbol_candidates = _extract_open_frontier_symbol_candidates(
        local_overlay=local_overlay,
        grounded_symbols=grounded_symbols,
        flow_observations=flow_observations,
        trace_relations=selected_trace_relations,
        limit=int(frontier_budget.get("open_frontier_symbol_cap") or 4),
    )
    open_frontier_symbols = _dedupe_tokens(
        [str(item.get("symbol") or "").strip() for item in list(open_frontier_symbol_candidates or [])],
        limit=int(frontier_budget.get("open_frontier_symbol_cap") or 4),
    )
    unresolved_edges = _extract_unresolved_caller_callee_edges(
        flow_observations=flow_observations,
        grounded_symbols=grounded_symbols,
        primary_paths=primary_paths,
        limit=int(frontier_budget.get("unresolved_edge_cap") or 4),
    )
    next_search_candidates = _build_next_search_candidates(
        question=question,
        local_overlay=local_overlay,
        open_frontier_symbol_candidates=open_frontier_symbol_candidates,
        unresolved_edges=unresolved_edges,
        limit=int(frontier_budget.get("next_search_candidate_cap") or 6),
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
        limit=18,
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
        "flow_observations": flow_observations,
        "trace_relations": selected_trace_relations,
        "engine_windows": list(engine_windows or [])[: int(frontier_budget.get("engine_window_cap") or 4)],
        "allowed_paths": allowed_paths,
        "grounded_symbols": grounded_symbols,
        "open_frontier_symbol_candidates": open_frontier_symbol_candidates,
        "open_frontier_symbols": open_frontier_symbols,
        "unresolved_caller_callee_edges": unresolved_edges,
        "next_search_candidates": next_search_candidates,
        "frontier_budget": frontier_budget,
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
    frontier_budget = dict(evidence_pack.get("frontier_budget") or {})
    symbol_candidates = list(evidence_pack.get("open_frontier_symbol_candidates") or [])
    engine_window_cap = max(1, int(frontier_budget.get("engine_window_cap") or 4))
    engine_match_cap = max(1, int(frontier_budget.get("engine_match_cap") or 3))
    engine_windows: List[Dict[str, Any]] = []
    tool_calls: List[Dict[str, Any]] = []
    seen_paths = set()

    for candidate in symbol_candidates:
        symbol = str(dict(candidate or {}).get("symbol") or "").strip()
        if not symbol:
            continue
        cache_key = symbol.lower()
        cached_matches = _ENGINE_SYMBOL_MATCH_CACHE.get(cache_key)
        if cached_matches is None:
            symbol_result = await find_symbol(
                redis,
                code_tools,
                symbol=symbol,
                limit=max(8, engine_match_cap * 2),
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
                "matches": filtered_matches[: min(4, engine_match_cap)],
            },
            ensure_ascii=False,
        )[:500]
        tool_calls.append(
            {
                "round": 0,
                "tool": "find_symbol",
                "input": {"symbol": symbol, "limit": max(8, engine_match_cap * 2)},
                "output_preview": preview,
            }
        )
        await _maybe_await(
            tool_callback,
            "find_symbol",
            {"symbol": symbol, "limit": max(8, engine_match_cap * 2)},
            preview,
        )
        if not filtered_matches:
            continue

        for match in filtered_matches[:engine_match_cap]:
            path = _normalize_path(match.get("path") or "")
            if not path or path.lower() in seen_paths:
                continue
            seen_paths.add(path.lower())
            start_line, end_line = _build_engine_read_window(
                str(match.get("line_range") or match.get("lineRange") or ""),
                max_line_span,
            )
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
                    "source_kind": "engine_frontier_read",
                    "tool": "engine_read",
                }
            )
            if len(engine_windows) >= engine_window_cap:
                return {"windows": engine_windows, "tool_calls": tool_calls}

    return {"windows": engine_windows, "tool_calls": tool_calls}


async def collect_local_overlay_code_explain_bootstrap(
    *,
    chat_deps,
    clean_message: str,
    local_overlay: Dict[str, Any],
    session_id: str,
    max_chars: int,
    max_line_span: int,
    progress_callback: ProgressCallback = None,
    tool_callback: ToolCallback = None,
    question_contract: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    local_reads = _collect_local_reads(local_overlay)
    if not local_reads:
        return {}

    normalized_contract = normalize_question_contract(
        question_contract,
        message=clean_message,
        workspace_overlay_present=bool(local_overlay.get("present")),
    )
    await _maybe_await(
        progress_callback,
        {
            "phase": "retrieve",
            "message": "Collecting grounded local reads and open frontier candidates.",
            "tool": "local_overlay",
        },
    )

    initial_pack = _build_evidence_pack(
        question=clean_message,
        local_overlay=local_overlay,
        engine_windows=[],
        question_contract=normalized_contract,
    )
    # The desktop overlay should ground local application flow first.
    # Server-side bootstrap does not prefetch additional engine reads; the main ReAct
    # loop can decide later whether an explicit engine/framework symbol warrants that search.
    engine_result = {"windows": [], "tool_calls": []}
    engine_windows = list(engine_result.get("windows") or [])
    final_pack = _build_evidence_pack(
        question=clean_message,
        local_overlay=local_overlay,
        engine_windows=engine_windows,
        question_contract=normalized_contract,
    )
    final_pack["tool_calls"] = list(engine_result.get("tool_calls") or [])
    final_pack["summary"] = _build_bootstrap_summary(final_pack)

    await _maybe_await(
        progress_callback,
        {
            "phase": "retrieve",
            "message": "Bootstrap frontier collected from local reads and unresolved edges.",
            "source_count": len(local_reads) + len(engine_windows),
            "open_frontier_symbol_count": len(list(final_pack.get("open_frontier_symbols") or [])),
            "unresolved_edge_count": len(list(final_pack.get("unresolved_caller_callee_edges") or [])),
        },
    )
    return final_pack


__all__ = ["collect_local_overlay_code_explain_bootstrap"]

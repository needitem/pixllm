from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List


_FLOW_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
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


def _normalize_path(value: Any) -> str:
    return str(value or "").strip().replace("\\", "/").lower()


def _ordered_unique(items: Iterable[Any]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        value = str(item or "").strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def _graph_state(graph: Dict[str, Any] | None) -> Dict[str, Any]:
    raw_graph = dict(graph or {})
    raw_state = raw_graph.get("graph_state")
    return dict(raw_state or {}) if isinstance(raw_state, dict) else {}


def _graph_chain_nodes(graph: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in list(_graph_state(graph).get("chain") or []):
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "relation": str(item.get("relation") or "").strip(),
                "symbol": str(item.get("symbol") or "").strip(),
                "path": str(item.get("path") or "").strip(),
                "line": int(item.get("line") or 0),
                "covered": bool(item.get("covered")),
                "discovered": bool(item.get("discovered")),
                "search_completed": bool(item.get("search_completed")),
                "base_symbol": str(item.get("base_symbol") or "").strip(),
            }
        )
    return out


def _graph_frontiers(graph: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    raw_state = _graph_state(graph)
    explicit = []
    for item in list(raw_state.get("frontiers") or []):
        if isinstance(item, dict):
            explicit.append(
                {
                    "relation": str(item.get("relation") or "").strip(),
                    "symbol": str(item.get("symbol") or "").strip(),
                    "path": str(item.get("path") or "").strip(),
                    "line": int(item.get("line") or 0),
                    "covered": bool(item.get("covered")),
                    "discovered": bool(item.get("discovered")),
                    "search_completed": bool(item.get("search_completed")),
                    "base_symbol": str(item.get("base_symbol") or "").strip(),
                }
            )
    if explicit:
        return explicit

    single = raw_state.get("frontier")
    if isinstance(single, dict):
        return [
            {
                "relation": str(single.get("relation") or "").strip(),
                "symbol": str(single.get("symbol") or "").strip(),
                "path": str(single.get("path") or "").strip(),
                "line": int(single.get("line") or 0),
                "covered": bool(single.get("covered")),
                "discovered": bool(single.get("discovered")),
                "search_completed": bool(single.get("search_completed")),
                "base_symbol": str(single.get("base_symbol") or "").strip(),
            }
        ]

    frontiers: List[Dict[str, Any]] = []
    for node in _graph_chain_nodes(graph):
        if node["covered"]:
            continue
        if node["search_completed"] and not node["discovered"]:
            continue
        if node["symbol"] or node["path"] or node["base_symbol"]:
            frontiers.append(node)
    return frontiers


def extract_workspace_graph(local_overlay: Dict[str, Any] | None) -> Dict[str, Any]:
    overlay = dict(local_overlay or {})
    raw = overlay.get("workspace_graph")
    return dict(raw or {}) if isinstance(raw, dict) else {}


def collect_grounded_overlay_paths(local_overlay: Dict[str, Any] | None) -> List[str]:
    overlay = dict(local_overlay or {})
    paths: List[str] = []

    selected_path = str(overlay.get("selected_file_path") or "").strip()
    selected_content = str(overlay.get("selected_file_content") or "").strip()
    if selected_path and selected_content:
        paths.append(selected_path)

    for step in list(overlay.get("local_trace") or []):
        if not isinstance(step, dict):
            continue
        if str(step.get("tool") or "").strip().lower() not in {"read_file", "read_symbol_span", "symbol_neighborhood"}:
            continue
        observation = step.get("observation")
        if not isinstance(observation, dict):
            continue
        path = str(observation.get("path") or "").strip()
        content = str(observation.get("content") or "").strip()
        if path and content:
            paths.append(path)

    return _ordered_unique(paths)


def collect_grounded_overlay_windows(local_overlay: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    overlay = dict(local_overlay or {})
    windows: List[Dict[str, Any]] = []
    seen = set()

    def _append(path: Any, content: Any, line_range: Any = "") -> None:
        normalized_path = str(path or "").strip()
        text = str(content or "")
        normalized_range = str(line_range or "").strip() or "1-1"
        if not normalized_path or not text.strip():
            return
        key = f"{_normalize_path(normalized_path)}::{normalized_range}"
        if key in seen:
            return
        seen.add(key)
        windows.append(
            {
                "path": normalized_path,
                "line_range": normalized_range,
                "content": text,
            }
        )

    _append(overlay.get("selected_file_path"), overlay.get("selected_file_content"))

    for step in list(overlay.get("local_trace") or []):
        if not isinstance(step, dict):
            continue
        if str(step.get("tool") or "").strip().lower() not in {"read_file", "read_symbol_span", "symbol_neighborhood"}:
            continue
        observation = step.get("observation")
        if not isinstance(observation, dict):
            continue
        _append(
            observation.get("path"),
            observation.get("content"),
            observation.get("lineRange") or observation.get("line_range") or "",
        )

    return windows


def collect_workspace_graph_paths(graph: Dict[str, Any] | None) -> List[str]:
    raw_graph = dict(graph or {})
    paths: List[str] = []
    paths.extend(
        [
            raw_graph.get("focus_file"),
            _graph_state(raw_graph).get("focus_path"),
        ]
    )
    paths.extend(list(raw_graph.get("core_files") or []))
    paths.extend(list(raw_graph.get("supporting_files") or []))

    for node in list(raw_graph.get("nodes") or []):
        if isinstance(node, dict):
            paths.append(node.get("path"))

    for node in _graph_chain_nodes(raw_graph):
        paths.append(node.get("path"))
    for node in _graph_frontiers(raw_graph):
        paths.append(node.get("path"))

    return _ordered_unique(paths)


def build_workspace_grounding_report(
    graph: Dict[str, Any] | None,
    grounded_paths: List[str] | None = None,
) -> Dict[str, Any]:
    direct_paths = _ordered_unique(grounded_paths or [])
    graph_paths = collect_workspace_graph_paths(graph)
    direct_norm = {_normalize_path(item) for item in direct_paths}
    graph_norm = {_normalize_path(item) for item in graph_paths}
    grounded_graph_paths = [path for path in graph_paths if _normalize_path(path) in direct_norm]
    graph_only_paths = [path for path in graph_paths if _normalize_path(path) not in direct_norm]

    raw_graph = dict(graph or {})
    graph_state = _graph_state(raw_graph)
    focus_path = str(
        raw_graph.get("focus_file")
        or graph_state.get("focus_path")
        or (graph_paths[0] if graph_paths else "")
    ).strip()
    focus_grounded = bool(focus_path) and _normalize_path(focus_path) in direct_norm

    return {
        "focus_path": focus_path,
        "focus_grounded": focus_grounded,
        "direct_paths": direct_paths,
        "graph_paths": graph_paths,
        "grounded_graph_paths": grounded_graph_paths,
        "graph_only_paths": graph_only_paths,
        "direct_path_count": len(direct_paths),
        "graph_path_count": len(graph_norm),
        "grounded_graph_path_count": len({_normalize_path(item) for item in grounded_graph_paths}),
        "graph_grounding_ratio": (
            len({_normalize_path(item) for item in grounded_graph_paths}) / len(graph_norm)
            if graph_norm
            else 1.0
        ),
        "graph_closed": bool(graph_state.get("closed")) if "closed" in graph_state else len(_graph_frontiers(raw_graph)) == 0,
        "open_frontier_count": int(graph_state.get("open_frontier_count") or len(_graph_frontiers(raw_graph))),
        "discovered_count": int(graph_state.get("discovered_count") or len([node for node in _graph_chain_nodes(raw_graph) if node.get("discovered")])),
        "covered_count": int(graph_state.get("covered_count") or len([node for node in _graph_chain_nodes(raw_graph) if node.get("covered")])),
        "coverage_ratio": float(
            graph_state.get("coverage_ratio")
            or (
                len([node for node in _graph_chain_nodes(raw_graph) if node.get("covered")])
                / len([node for node in _graph_chain_nodes(raw_graph) if node.get("discovered")])
                if len([node for node in _graph_chain_nodes(raw_graph) if node.get("discovered")]) > 0
                else 0.0
            )
        ),
    }


def workspace_graph_has_content(graph: Dict[str, Any] | None) -> bool:
    raw_graph = dict(graph or {})
    return bool(
        str(raw_graph.get("focus_file") or "").strip()
        or list(raw_graph.get("core_files") or [])
        or list(raw_graph.get("supporting_files") or [])
        or list(raw_graph.get("nodes") or [])
        or _graph_chain_nodes(raw_graph)
        or str(raw_graph.get("target_symbol") or "").strip()
    )


def _filter_graph_items_by_path(items: Iterable[Any], allowed_paths: set[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or "").strip()
        if not path or _normalize_path(path) not in allowed_paths:
            continue
        out.append(dict(item))
    return out


def _filter_workspace_graph(graph: Dict[str, Any], grounded_paths: List[str] | None = None) -> Dict[str, Any]:
    raw_graph = dict(graph or {})
    allowed_paths = {_normalize_path(path) for path in list(grounded_paths or []) if str(path or "").strip()}
    if not allowed_paths:
        return raw_graph

    filtered = dict(raw_graph)
    filtered["focus_file"] = (
        str(raw_graph.get("focus_file") or "").strip()
        if _normalize_path(raw_graph.get("focus_file")) in allowed_paths
        else ""
    )
    filtered["core_files"] = [
        item
        for item in list(raw_graph.get("core_files") or [])
        if _normalize_path(item) in allowed_paths
    ]
    filtered["supporting_files"] = [
        item
        for item in list(raw_graph.get("supporting_files") or [])
        if _normalize_path(item) in allowed_paths
    ]
    filtered["nodes"] = _filter_graph_items_by_path(raw_graph.get("nodes") or [], allowed_paths)

    raw_state = _graph_state(raw_graph)
    if raw_state:
        filtered_state = dict(raw_state)
        filtered_state["chain"] = _filter_graph_items_by_path(raw_state.get("chain") or [], allowed_paths)
        filtered_state["frontiers"] = _filter_graph_items_by_path(_graph_frontiers(raw_graph), allowed_paths)
        if filtered_state["frontiers"]:
            filtered_state["frontier"] = filtered_state["frontiers"][0]
        else:
            filtered_state["frontier"] = {}
        focus_path = str(raw_state.get("focus_path") or "").strip()
        filtered_state["focus_path"] = focus_path if _normalize_path(focus_path) in allowed_paths else ""
        filtered["graph_state"] = filtered_state
    return filtered


def workspace_graph_has_grounded_focus(graph: Dict[str, Any] | None, grounded_paths: List[str] | None = None) -> bool:
    raw_graph = dict(graph or {})
    focus_path = str(raw_graph.get("focus_file") or _graph_state(raw_graph).get("focus_path") or "").strip()
    if not grounded_paths:
        return bool(focus_path) or workspace_graph_has_content(raw_graph)
    allowed_paths = {_normalize_path(path) for path in list(grounded_paths or []) if str(path or "").strip()}
    if focus_path:
        return _normalize_path(focus_path) in allowed_paths
    return any(_normalize_path(path) in allowed_paths for path in collect_workspace_graph_paths(raw_graph))


def workspace_graph_is_ready_for_answer(
    graph: Dict[str, Any] | None,
    grounded_paths: List[str] | None = None,
) -> Dict[str, Any]:
    raw_graph = dict(graph or {})
    report = build_workspace_grounding_report(raw_graph, grounded_paths)
    issues: List[str] = []
    evidence_dimensions = [
        item
        for item in list(raw_graph.get("evidence_dimensions") or [])
        if isinstance(item, dict)
    ]
    missing_dimensions = [
        {
            "name": str(item.get("name") or "").strip(),
            "why": str(item.get("why") or "").strip(),
        }
        for item in evidence_dimensions
        if str(item.get("status") or "").strip().lower() == "missing"
    ]

    if not workspace_graph_has_content(raw_graph):
        issues.append("missing_graph")

    if grounded_paths is not None and report["graph_path_count"] > 0 and report["grounded_graph_path_count"] == 0:
        issues.append("no_grounded_graph_paths")

    if grounded_paths is not None and report["graph_path_count"] > 0 and not report["focus_grounded"]:
        issues.append("focus_not_grounded")

    if int(report.get("open_frontier_count") or 0) > 0 or not bool(report.get("graph_closed")):
        issues.append("open_frontier")

    discovered_count = int(report.get("discovered_count") or 0)
    covered_count = int(report.get("covered_count") or 0)
    coverage_ratio = float(report.get("coverage_ratio") or 0.0)
    if discovered_count > 0 and covered_count < discovered_count:
        issues.append("uncovered_graph_nodes")
    if discovered_count >= 2 and coverage_ratio < 0.6:
        issues.append("thin_graph_coverage")
    if missing_dimensions:
        issues.append("planner_missing_dimensions")

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "report": report,
        "frontiers": _graph_frontiers(raw_graph),
        "chain": _graph_chain_nodes(raw_graph),
        "missing_dimensions": missing_dimensions,
    }


def _relation_label(node: Dict[str, Any], index: int) -> str:
    relation = str(node.get("relation") or "").strip().replace("_", " ")
    if relation:
        return relation
    return f"step {index + 1}"


def _node_ref(node: Dict[str, Any]) -> str:
    path = str(node.get("path") or "").strip()
    symbol = str(node.get("symbol") or "").strip()
    if path and symbol:
        return f"`{path}` -> `{symbol}`"
    if path:
        return f"`{path}`"
    if symbol:
        return f"`{symbol}`"
    return "`unknown`"


def _edge_sentence(edge: Dict[str, Any]) -> str:
    source = str(edge.get("from") or "").strip()
    target = str(edge.get("to") or "").strip()
    relation = str(edge.get("relation") or "").strip().replace("_", " ")
    via = str(edge.get("via") or "").strip()
    if not source or not target:
        return ""
    if via:
        return f"`{source}` -> `{target}` via `{via}`"
    if relation:
        return f"`{source}` -> `{target}` ({relation})"
    return f"`{source}` -> `{target}`"


def _uses_korean(text: str) -> bool:
    return bool(re.search(r"[\uac00-\ud7a3]", str(text or "")))


def _find_anchor_window(
    local_overlay: Dict[str, Any] | None,
    *,
    focus_path: str,
    target_symbol: str,
) -> Dict[str, Any]:
    windows = collect_grounded_overlay_windows(local_overlay)
    normalized_focus = _normalize_path(focus_path)
    normalized_target = str(target_symbol or "").strip()
    candidates: List[Dict[str, Any]] = []
    for window in windows:
        if _normalize_path(window.get("path")) != normalized_focus:
            continue
        content = str(window.get("content") or "")
        if normalized_target and re.search(rf"\b{re.escape(normalized_target)}\s*\(", content):
            candidates.append(window)
    if candidates:
        return sorted(
            candidates,
            key=lambda item: (
                0 if str(item.get("line_range") or "").strip() not in {"", "1-1"} else 1,
                len(str(item.get("content") or "")),
                len(str(item.get("line_range") or "")),
            ),
        )[0]
    for window in windows:
        if _normalize_path(window.get("path")) == normalized_focus:
            return window
    return {}


def _extract_anchor_calls(content: str, *, anchor_symbol: str = "") -> List[str]:
    out: List[str] = []
    seen = set()
    anchor_lower = str(anchor_symbol or "").strip().lower()
    normalized_content = re.sub(r"/\*.*?\*/", " ", str(content or ""), flags=re.S)
    normalized_content = re.sub(r"//.*?$", " ", normalized_content, flags=re.M)
    for token in _FLOW_CALL_RE.findall(normalized_content):
        symbol = str(token or "").strip()
        lowered = symbol.lower()
        if not symbol or not symbol[:1].isupper():
            continue
        if lowered in _FLOW_CALL_KEYWORDS or lowered == anchor_lower:
            continue
        if lowered in seen:
            continue
        seen.add(lowered)
        out.append(symbol)
    return out


def _chain_nodes_for_base_symbols(
    chain: List[Dict[str, Any]],
    *,
    relation: str,
    base_symbols: Iterable[str],
) -> List[Dict[str, Any]]:
    normalized_bases = {str(item or "").strip().lower() for item in list(base_symbols or []) if str(item or "").strip()}
    out: List[Dict[str, Any]] = []
    seen = set()
    for node in chain:
        if str(node.get("relation") or "").strip().lower() != relation:
            continue
        if str(node.get("base_symbol") or "").strip().lower() not in normalized_bases:
            continue
        symbol = str(node.get("symbol") or "").strip()
        path = str(node.get("path") or "").strip()
        key = f"{path.lower()}::{symbol.lower()}"
        if not symbol or key in seen:
            continue
        seen.add(key)
        out.append(node)
    return out


def _frontier_nodes_for_base_symbols(
    frontiers: List[Dict[str, Any]],
    *,
    base_symbols: Iterable[str],
) -> List[Dict[str, Any]]:
    normalized_bases = {str(item or "").strip().lower() for item in list(base_symbols or []) if str(item or "").strip()}
    out: List[Dict[str, Any]] = []
    seen = set()
    for node in frontiers:
        if str(node.get("base_symbol") or "").strip().lower() not in normalized_bases:
            continue
        symbol = str(node.get("symbol") or "").strip()
        path = str(node.get("path") or "").strip()
        key = f"{path.lower()}::{symbol.lower()}"
        if not symbol or key in seen:
            continue
        seen.add(key)
        out.append(node)
    return out


def _symbol_ref(symbol: str, path: str = "") -> str:
    label = f"`{symbol}()`" if symbol else "`unknown`"
    if path:
        return f"{label} in `{path}`"
    return label


def render_workspace_graph_answer(
    question: str,
    graph: Dict[str, Any],
    *,
    grounded_paths: List[str] | None = None,
    local_overlay: Dict[str, Any] | None = None,
) -> str:
    filtered_graph = _filter_workspace_graph(graph, grounded_paths)
    if grounded_paths is not None and not workspace_graph_has_grounded_focus(graph, grounded_paths):
        return ""
    if not workspace_graph_has_content(filtered_graph):
        return ""

    graph_state = _graph_state(filtered_graph)
    chain = _graph_chain_nodes(filtered_graph)
    frontiers = _graph_frontiers(filtered_graph)
    focus_path = str(filtered_graph.get("focus_file") or graph_state.get("focus_path") or "").strip()
    core_files = _ordered_unique(filtered_graph.get("core_files") or [])
    supporting_files = _ordered_unique(filtered_graph.get("supporting_files") or [])
    target_symbol = str(filtered_graph.get("target_symbol") or graph_state.get("anchor_symbol") or "").strip()
    is_korean = _uses_korean(question)
    caller_nodes = [
        node
        for node in chain
        if str(node.get("relation") or "").strip().lower() in {"caller_owner", "related_owner"}
        and str(node.get("base_symbol") or "").strip().lower() == target_symbol.lower()
    ]
    anchor_window = _find_anchor_window(local_overlay, focus_path=focus_path, target_symbol=target_symbol)
    direct_call_names = _extract_anchor_calls(str(anchor_window.get("content") or ""), anchor_symbol=target_symbol)
    direct_callees = _chain_nodes_for_base_symbols(chain, relation="callee_definition", base_symbols=[target_symbol])
    direct_frontiers = _frontier_nodes_for_base_symbols(frontiers, base_symbols=[target_symbol])
    direct_callee_map = {str(node.get("symbol") or "").strip().lower(): node for node in direct_callees}
    direct_frontier_map = {str(node.get("symbol") or "").strip().lower(): node for node in direct_frontiers}

    title = str(question or "").strip() or "Workspace Graph"
    lines: List[str] = [f"## {title}", ""]

    if focus_path or target_symbol:
        lines.append("### 확인된 진입점" if is_korean else "### Confirmed Entry Point")
        if focus_path and target_symbol:
            lines.append(
                f"- `{focus_path}`의 `{target_symbol}()`가 현재 grounded anchor입니다."
                if is_korean else
                f"- The current grounded anchor is `{target_symbol}()` in `{focus_path}`."
            )
        elif focus_path:
            lines.append(f"- Primary grounded focus: `{focus_path}`")
        elif target_symbol:
            lines.append(f"- Current anchor symbol: `{target_symbol}`")
        if caller_nodes:
            caller_refs = ", ".join(
                _symbol_ref(str(node.get("symbol") or "").strip(), str(node.get("path") or "").strip())
                for node in caller_nodes[:4]
            )
            lines.append(
                f"- 호출 측에서는 {caller_refs} 에서 이 흐름으로 들어옵니다."
                if is_korean else
                f"- Confirmed callers into this flow include {caller_refs}."
            )
        lines.append("")

    direct_flow_lines: List[str] = []
    seen_symbols = set()
    for symbol in direct_call_names:
        lowered = symbol.lower()
        if lowered in seen_symbols:
            continue
        seen_symbols.add(lowered)
        downstream_nodes = _chain_nodes_for_base_symbols(chain, relation="callee_definition", base_symbols=[symbol])
        if lowered in direct_callee_map:
            callee_node = direct_callee_map[lowered]
            if downstream_nodes:
                downstream_refs = ", ".join(
                    _symbol_ref(str(node.get("symbol") or "").strip(), str(node.get("path") or "").strip())
                    for node in downstream_nodes[:3]
                )
                direct_flow_lines.append(
                    f"- `{target_symbol}()` -> {_symbol_ref(symbol, str(callee_node.get('path') or '').strip())}; 내부에서 {downstream_refs} 까지 확인됨"
                    if is_korean else
                    f"- `{target_symbol}()` -> {_symbol_ref(symbol, str(callee_node.get('path') or '').strip())}; downstream grounded calls include {downstream_refs}"
                )
            else:
                direct_flow_lines.append(
                    f"- `{target_symbol}()` -> {_symbol_ref(symbol, str(callee_node.get('path') or '').strip())}"
                )
        elif lowered in direct_frontier_map:
            direct_flow_lines.append(
                f"- `{target_symbol}()` -> `{symbol}()`; 정의 추적은 아직 열려 있음"
                if is_korean else
                f"- `{target_symbol}()` -> `{symbol}()`; definition tracking is still open"
            )
        else:
            direct_flow_lines.append(
                f"- `{target_symbol}()` -> `{symbol}()`; anchor span에서 호출만 직접 확인됨"
                if is_korean else
                f"- `{target_symbol}()` -> `{symbol}()`; directly observed in the anchor span"
            )
    if not direct_flow_lines:
        for node in direct_callees[:6]:
            symbol = str(node.get("symbol") or "").strip()
            if not symbol:
                continue
            downstream_nodes = _chain_nodes_for_base_symbols(chain, relation="callee_definition", base_symbols=[symbol])
            if downstream_nodes:
                downstream_refs = ", ".join(
                    _symbol_ref(str(item.get("symbol") or "").strip(), str(item.get("path") or "").strip())
                    for item in downstream_nodes[:3]
                )
                direct_flow_lines.append(
                    f"- `{target_symbol}()` -> {_symbol_ref(symbol, str(node.get('path') or '').strip())}; 내부에서 {downstream_refs} 까지 확인됨"
                    if is_korean else
                    f"- `{target_symbol}()` -> {_symbol_ref(symbol, str(node.get('path') or '').strip())}; downstream grounded calls include {downstream_refs}"
                )
            else:
                direct_flow_lines.append(
                    f"- `{target_symbol}()` -> {_symbol_ref(symbol, str(node.get('path') or '').strip())}"
                )
    if direct_flow_lines:
        lines.append("### 직접 확인된 호출 흐름" if is_korean else "### Directly Grounded Flow")
        lines.extend(direct_flow_lines[:8])
        lines.append("")

    downstream_roots = [str(node.get("symbol") or "").strip() for node in direct_callees[:6] if str(node.get("symbol") or "").strip()]
    downstream_nodes = _chain_nodes_for_base_symbols(chain, relation="callee_definition", base_symbols=downstream_roots)
    if downstream_nodes:
        lines.append("### 확인된 downstream 효과" if is_korean else "### Confirmed Downstream Effects")
        for node in downstream_nodes[:6]:
            base_symbol = str(node.get("base_symbol") or "").strip()
            lines.append(
                f"- `{base_symbol}()` 내부에서 {_symbol_ref(str(node.get('symbol') or '').strip(), str(node.get('path') or '').strip())} 까지 이어집니다."
                if is_korean else
                f"- Inside `{base_symbol}()`, the flow continues to {_symbol_ref(str(node.get('symbol') or '').strip(), str(node.get('path') or '').strip())}."
            )
        lines.append("")

    if frontiers:
        lines.append("### 아직 열린 frontier" if is_korean else "### Remaining Open Frontier")
        for node in frontiers[:5]:
            base_symbol = str(node.get("base_symbol") or "").strip()
            reason = str(node.get("reason") or "").strip()
            summary = _symbol_ref(str(node.get("symbol") or "").strip(), str(node.get("path") or "").strip())
            if base_symbol and reason:
                lines.append(
                    f"- `{base_symbol}()` 기준으로 {summary} 추적이 남아 있습니다. 사유: `{reason}`"
                    if is_korean else
                    f"- From `{base_symbol}()`, tracking to {summary} is still open. Reason: `{reason}`"
                )
            elif base_symbol:
                lines.append(
                    f"- `{base_symbol}()` 기준으로 {summary} 추적이 남아 있습니다."
                    if is_korean else
                    f"- From `{base_symbol}()`, tracking to {summary} is still open."
                )
            else:
                lines.append(f"- {summary}")
        lines.append("")

    related_paths = _ordered_unique(([focus_path] if focus_path else []) + core_files + supporting_files)
    if related_paths:
        lines.append("### 근거 파일" if is_korean else "### Grounded Files")
        for path in related_paths[:6]:
            lines.append(f"- `{path}`")

    return "\n".join(lines).strip()

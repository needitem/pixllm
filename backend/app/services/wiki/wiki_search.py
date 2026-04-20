from .wiki_core import *  # noqa: F401,F403
from .wiki_manifest import _load_runtime_manifest_for_root
from .wiki_pages import _page_payload

_EXPLICIT_FAMILY_HINT_PATTERNS: Sequence[Tuple[str, Sequence[str]]] = (
    ("api_videoview", ("videoview", "nxvideoview", "비디오 레이어", "동영상 채널", "klv")),
    ("api_imageview", ("imageview", "nximageview")),
    ("api_milmapview", ("milmapview", "milmap")),
    ("api_planetview", ("planetview", "planet 엔진")),
    ("api_scene_editor", ("scene 파일", "scene 객체", "scene 선택", "scene object", "scene editor", "scene")),
    ("api_editor", ("편집 화면", "canvas editor", "canvas")),
    ("api_dfs", ("dfs", "pbi", "pbe", "provider export")),
    ("api_vector", ("벡터", "vector", "shp")),
    ("api_raster", ("xrasterio", "xdm", "래스터", "raster")),
    ("api_coordinate", ("좌표계", "epsg", "utm", "mgrs", "georef", "wkt", "proj4")),
    ("api_sensor_model", ("sensor model", "영상 좌표", "image to ground", "ground to image")),
    ("api_uspaceview", ("uspaceview", "uspace view")),
    ("api_core", ("license", "라이선스", "config path", "설정 경로")),
)
_QUERY_ROUTER_TOKEN_CACHE: Dict[str, Dict[str, Any]] = {}
_QUERY_ROUTER_TOKEN_CACHE_LIMIT = 128
_EXPLICIT_FAMILY_HINT_CACHE: Dict[str, List[str]] = {}
_PRIORITY_FAMILY_HINT_CACHE: Dict[str, List[str]] = {}
_QUERY_HINT_CACHE_LIMIT = 128


def _store_hint_cache(cache: Dict[str, List[str]], key: str, value: List[str]) -> List[str]:
    cache[key] = list(value)
    while len(cache) > _QUERY_HINT_CACHE_LIMIT:
        oldest_key = next(iter(cache))
        cache.pop(oldest_key, None)
    return list(value)

def _build_excerpt(content: str, query: str, limit: int = 420) -> str:
    source = str(content or "")
    lowered = source.lower()
    needle = str(query or "").strip().lower()
    if not needle:
        return source[:limit]
    index = lowered.find(needle)
    if index < 0:
        return source[:limit]
    start = max(0, index - 120)
    end = min(len(source), index + max(120, len(needle) + 120))
    return source[start:end][:limit]


def _compact_values(values: Iterable[str]) -> List[str]:
    output: List[str] = []
    seen = set()
    for item in values or []:
        compact = compact_token(item)
        if not compact or compact in seen:
            continue
        seen.add(compact)
        output.append(compact)
    return output


def _expand_manifest_match_tokens(values: Iterable[str]) -> List[str]:
    expanded: List[str] = []
    for item in values or []:
        raw_value = str(item or "").strip()
        if not raw_value:
            continue
        expanded.append(raw_value)
        expanded.extend(extract_query_terms(raw_value, limit=24))
        expanded.extend(extract_query_compacts(raw_value, limit=24))
    return _compact_values(expanded)


def _query_router_tokens(query: str) -> Dict[str, Any]:
    raw_query = str(query or "").strip()
    cached = _QUERY_ROUTER_TOKEN_CACHE.get(raw_query)
    if cached is not None:
        return cached
    query_compacts = _compact_values(extract_query_compacts(raw_query, limit=24))
    query_terms = _compact_values(extract_query_terms(raw_query, limit=24))
    query_symbols = _compact_values(extract_symbol_query_candidates(raw_query, max_candidates=8))
    query_blob = compact_token(raw_query)
    semantic_tokens = _compact_values([*query_compacts, *query_terms])
    payload = {
        "raw": raw_query,
        "blob": query_blob,
        "compacts": query_compacts,
        "terms": query_terms,
        "symbols": query_symbols,
        "semantic_tokens": semantic_tokens,
    }
    _QUERY_ROUTER_TOKEN_CACHE[raw_query] = payload
    while len(_QUERY_ROUTER_TOKEN_CACHE) > _QUERY_ROUTER_TOKEN_CACHE_LIMIT:
        oldest_key = next(iter(_QUERY_ROUTER_TOKEN_CACHE))
        _QUERY_ROUTER_TOKEN_CACHE.pop(oldest_key, None)
    return payload


def _query_explicit_family_hints(query: str) -> List[str]:
    lowered = str(query or "").strip().lower()
    if not lowered:
        return []
    cached = _EXPLICIT_FAMILY_HINT_CACHE.get(lowered)
    if cached is not None:
        return list(cached)
    hints: List[str] = []
    for family, patterns in _EXPLICIT_FAMILY_HINT_PATTERNS:
        if any(pattern in lowered for pattern in patterns):
            hints.append(family)
    return _store_hint_cache(_EXPLICIT_FAMILY_HINT_CACHE, lowered, hints)


def _query_priority_family_hints(query: str) -> List[str]:
    lowered = str(query or "").strip().lower()
    if not lowered:
        return []
    cached = _PRIORITY_FAMILY_HINT_CACHE.get(lowered)
    if cached is not None:
        return list(cached)

    def has_any(*parts: str) -> bool:
        return any(part in lowered for part in parts)

    if (
        has_any("imageview", "milmapview", "planetview")
        and has_any("비디오 레이어", "video layer", "동영상 채널", "채널 연결", "채널 해제", "초기 프레임", "동영상 프레임", "klv")
    ):
        families = ["api_videoview"]
        if has_any("imageview"):
            families.append("api_imageview")
        if has_any("milmapview"):
            families.append("api_milmapview")
        if has_any("planetview"):
            families.append("api_planetview")
        return _store_hint_cache(_PRIORITY_FAMILY_HINT_CACHE, lowered, families)

    if has_any("scene") and has_any("선택", "편집을 종료", "select none", "select all", "hit test", "scene object"):
        return _store_hint_cache(_PRIORITY_FAMILY_HINT_CACHE, lowered, ["api_scene_editor"])

    if has_any("dfs") and has_any("export", "진행률", "cancel"):
        return _store_hint_cache(_PRIORITY_FAMILY_HINT_CACHE, lowered, ["api_dfs"])

    if has_any("dfs", "provider group") and has_any("xdmcompmanager", "xdm comp manager", "xdmcompmanager를"):
        return _store_hint_cache(_PRIORITY_FAMILY_HINT_CACHE, lowered, ["api_dfs"])

    if has_any("합성 관리자", "comp manager", "compmanager", "합성 1 front", "합성 2 front"):
        return _store_hint_cache(_PRIORITY_FAMILY_HINT_CACHE, lowered, ["api_imageview", "api_raster"])

    if has_any("planetview", "planet 엔진") and has_any("shader", "cartoon", "sun follow"):
        return _store_hint_cache(_PRIORITY_FAMILY_HINT_CACHE, lowered, ["api_planetview"])

    if has_any("milmapview") and has_any("shader", "cartoon"):
        return _store_hint_cache(_PRIORITY_FAMILY_HINT_CACHE, lowered, ["api_milmapview"])

    if has_any("공간 좌표") and has_any("world 좌표", "화면 좌표", "screen 좌표"):
        return _store_hint_cache(_PRIORITY_FAMILY_HINT_CACHE, lowered, ["api_uspaceview", "api_coordinate"])

    if has_any("영상 중심점") and has_any("지도 좌표", "map coord"):
        return _store_hint_cache(_PRIORITY_FAMILY_HINT_CACHE, lowered, ["api_sensor_model", "api_coordinate"])

    return _store_hint_cache(_PRIORITY_FAMILY_HINT_CACHE, lowered, [])


def _compact_query_matches(query_blob: str, query_compacts: Sequence[str], candidate: str) -> bool:
    normalized_candidate = compact_token(candidate)
    if not normalized_candidate:
        return False
    if normalized_candidate in query_compacts:
        return True
    if len(normalized_candidate) >= 2 and normalized_candidate in str(query_blob or ""):
        return True
    return False


def _routing_hint_match_count(entry: Dict[str, Any], query_info: Dict[str, Any]) -> int:
    hints = entry.get("routing_hints") if isinstance(entry.get("routing_hints"), list) else []
    if not hints:
        return 0
    query_blob = str(query_info.get("blob") or "")
    query_terms = query_info.get("semantic_tokens") if isinstance(query_info.get("semantic_tokens"), list) else []
    matched = 0
    for item in hints:
        if not isinstance(item, dict):
            continue
        all_of = [str(value or "").strip() for value in (item.get("all_of") if isinstance(item.get("all_of"), list) else []) if str(value or "").strip()]
        any_of = [str(value or "").strip() for value in (item.get("any_of") if isinstance(item.get("any_of"), list) else []) if str(value or "").strip()]
        all_match = all(_compact_query_matches(query_blob, query_terms, value) for value in all_of) if all_of else True
        any_match = any(_compact_query_matches(query_blob, query_terms, value) for value in any_of) if any_of else True
        if all_match and any_match:
            matched += 1
    return matched


def _workflow_router_match_flags(entry: Dict[str, Any], query_info: Dict[str, Any]) -> Dict[str, bool]:
    path_value = str(entry.get("path") or "").strip()
    title = str(entry.get("title") or "").strip()
    aliases = [str(item or "").strip() for item in (entry.get("aliases") if isinstance(entry.get("aliases"), list) else []) if str(item or "").strip()]
    route_terms = [str(item or "").strip() for item in (entry.get("route_terms") if isinstance(entry.get("route_terms"), list) else []) if str(item or "").strip()]
    symbols = [str(item or "").strip() for item in (entry.get("symbols") if isinstance(entry.get("symbols"), list) else []) if str(item or "").strip()]
    linked_method_symbols = [str(item or "").strip() for item in (entry.get("linked_method_symbols") if isinstance(entry.get("linked_method_symbols"), list) else []) if str(item or "").strip()]
    semantic_terms = [str(item or "").strip() for item in (entry.get("semantic_terms") if isinstance(entry.get("semantic_terms"), list) else []) if str(item or "").strip()]
    bundle_page_titles = [str(item or "").strip() for item in (entry.get("bundle_page_titles") if isinstance(entry.get("bundle_page_titles"), list) else []) if str(item or "").strip()]
    bundle_page_summaries = [str(item or "").strip() for item in (entry.get("bundle_page_summaries") if isinstance(entry.get("bundle_page_summaries"), list) else []) if str(item or "").strip()]
    family = str(entry.get("workflow_family") or "").strip()

    path_stem = PurePosixPath(path_value).stem
    exact_candidates = _compact_values([title, path_stem, *aliases])
    route_compacts = _expand_manifest_match_tokens([title, path_stem, family, *aliases, *route_terms, *symbols, *linked_method_symbols])
    symbol_compacts = _expand_manifest_match_tokens([*symbols, *linked_method_symbols])
    semantic_compacts = _expand_manifest_match_tokens([title, str(entry.get("summary") or ""), *semantic_terms, *bundle_page_titles, *bundle_page_summaries])
    bundle_compacts = _expand_manifest_match_tokens([*bundle_page_titles, *bundle_page_summaries])

    query_blob = str(query_info.get("blob") or "")
    query_compacts = query_info.get("compacts") if isinstance(query_info.get("compacts"), list) else []
    query_symbols = query_info.get("symbols") if isinstance(query_info.get("symbols"), list) else []
    query_semantic = query_info.get("semantic_tokens") if isinstance(query_info.get("semantic_tokens"), list) else []
    exact_route_matches = [candidate for candidate in query_compacts if candidate in route_compacts]
    exact_name_matches = [candidate for candidate in query_compacts if candidate in exact_candidates]
    semantic_hits = [candidate for candidate in query_semantic if len(candidate) >= 4 and candidate in semantic_compacts]
    bundle_hits = [candidate for candidate in query_semantic if len(candidate) >= 4 and candidate in bundle_compacts]

    exact_name_match = any(_compact_query_matches(query_blob, query_compacts, candidate) for candidate in exact_candidates)
    route_term_match = any(_compact_query_matches(query_blob, query_compacts, candidate) for candidate in route_compacts)
    symbol_match = any(compact_token(candidate) in query_symbols for candidate in symbol_compacts)
    family_literal_match = _compact_query_matches(query_blob, query_compacts, family)
    bundle_match = any(_compact_query_matches(query_blob, query_semantic, candidate) for candidate in [*bundle_page_titles, *bundle_page_summaries])
    semantic_match = bundle_match or len(semantic_hits) >= 2 or any(_compact_query_matches(query_blob, query_semantic, candidate) for candidate in semantic_terms)
    routing_hint_match_count = _routing_hint_match_count(entry, query_info)

    return {
        "exact_name_match": exact_name_match,
        "route_term_match": route_term_match,
        "symbol_match": symbol_match,
        "family_literal_match": family_literal_match,
        "bundle_match": bundle_match,
        "semantic_match": semantic_match,
        "routing_hint_match_count": routing_hint_match_count,
        "longest_exact_route_match": max((len(item) for item in exact_route_matches), default=0),
        "exact_route_match_count": len(exact_route_matches),
        "exact_name_match_count": len(exact_name_matches),
        "semantic_overlap_count": len(semantic_hits),
        "bundle_overlap_count": len(bundle_hits),
        "longest_semantic_match": max((len(item) for item in semantic_hits), default=0),
    }


def _workflow_result_payload(
    entry: Dict[str, Any],
    root: Path,
    *,
    include_content: bool,
    rank: int,
    query: str,
) -> Dict[str, Any]:
    path_value = str(entry.get("path") or "").strip()
    target = root / PurePosixPath(path_value).as_posix()
    page_payload = _page_payload(root, target) if target.exists() else {}
    content = target.read_text(encoding="utf-8") if include_content and target.exists() else str(entry.get("content") or "")
    return {
        "path": path_value,
        "title": str(entry.get("title") or "").strip(),
        "kind": "workflow",
        "summary": str(entry.get("summary") or "").strip(),
        "updated_at": str(page_payload.get("updated_at") or ""),
        **({"content": content} if include_content else {"excerpt": _build_excerpt(content or str(entry.get("content") or ""), query)}),
        "rank": rank,
    }


def _workflow_results_for_families(
    root: Path,
    *,
    families: Sequence[str],
    include_content: bool,
    query: str,
    limit: int,
    workflow_index: Optional[Sequence[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    if not isinstance(workflow_index, Sequence):
        manifest = _load_runtime_manifest_for_root(root)
        workflow_index = manifest.get("workflow_index") if isinstance(manifest.get("workflow_index"), list) else []
    if not workflow_index:
        return []
    family_order = [str(item or "").strip() for item in families if str(item or "").strip()]
    ordered: List[Dict[str, Any]] = []
    seen = set()
    for family in family_order:
        matches = [
            entry for entry in workflow_index
            if isinstance(entry, dict) and str(entry.get("workflow_family") or "").strip() == family
        ]
        for entry in matches:
            key = str(entry.get("path") or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            ordered.append(_workflow_result_payload(entry, root, include_content=include_content, rank=0, query=query))
            if len(ordered) >= max(1, min(int(limit or 12), 50)):
                return ordered
    return ordered


def _preferred_workflow_paths(
    root: Path,
    *,
    families: Sequence[str],
    workflow_index: Optional[Sequence[Dict[str, Any]]] = None,
) -> List[str]:
    items = _workflow_results_for_families(
        root,
        families=families,
        include_content=False,
        query="",
        limit=50,
        workflow_index=workflow_index,
    )
    return [str(item.get("path") or "").strip().lower() for item in items if str(item.get("path") or "").strip()]


def _route_workflow_results(
    root: Path,
    *,
    query: str,
    limit: int = 12,
    include_content: bool = False,
    preferred_families: Optional[Sequence[str]] = None,
    priority_families: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    manifest = _load_runtime_manifest_for_root(root)
    workflow_index = manifest.get("workflow_index") if isinstance(manifest.get("workflow_index"), list) else []
    if not workflow_index:
        return []

    preferred = _workflow_results_for_families(
        root,
        families=preferred_families or [],
        include_content=include_content,
        query=query,
        limit=limit,
        workflow_index=workflow_index,
    )
    preferred_paths = _preferred_workflow_paths(root, families=preferred_families or [], workflow_index=workflow_index)
    preferred_priority = {path_value: index for index, path_value in enumerate(preferred_paths)}
    priority_paths = _preferred_workflow_paths(root, families=priority_families or [], workflow_index=workflow_index)
    priority_path_set = set(priority_paths)
    priority_rank = {path_value: index for index, path_value in enumerate(priority_paths)}

    query_info = _query_router_tokens(query)
    candidates: List[Tuple[Dict[str, Any], Dict[str, bool]]] = []
    for entry in workflow_index:
        if not isinstance(entry, dict):
            continue
        flags = _workflow_router_match_flags(entry, query_info)
        if any(flags.values()):
            candidates.append((entry, flags))

    if not candidates:
        candidates = [(entry, _workflow_router_match_flags(entry, query_info)) for entry in workflow_index if isinstance(entry, dict)]
        candidates = [
            (entry, flags)
            for entry, flags in candidates
            if int(flags.get("semantic_overlap_count") or 0) > 0 or bool(flags.get("semantic_match"))
        ]
        if not candidates:
            return preferred[: max(1, min(int(limit or 12), 50))]

    priority_candidates = [
        (entry, flags)
        for entry, flags in candidates
        if str(entry.get("path") or "").strip().lower() in priority_path_set
        and (
            bool(flags.get("exact_name_match"))
            or bool(flags.get("route_term_match"))
            or bool(flags.get("bundle_match"))
            or bool(flags.get("semantic_match"))
            or bool(flags.get("symbol_match"))
            or int(flags.get("routing_hint_match_count") or 0) > 0
        )
    ]
    if priority_candidates:
        ordered_priority: List[Dict[str, Any]] = []
        seen_priority = set()
        for entry, _flags in sorted(
            priority_candidates,
            key=lambda item: (
                priority_rank.get(str(item[0].get("path") or "").strip().lower(), 999),
                str(item[0].get("path") or ""),
            ),
        ):
            path_value = str(entry.get("path") or "").strip().lower()
            if not path_value or path_value in seen_priority:
                continue
            seen_priority.add(path_value)
            ordered_priority.append(_workflow_result_payload(entry, root, include_content=include_content, rank=0, query=query))
            if len(ordered_priority) >= max(1, min(int(limit or 12), 50)):
                return ordered_priority
        if ordered_priority:
            remaining = [item for item in preferred if str(item.get("path") or "").strip().lower() not in seen_priority]
            return [*ordered_priority, *remaining][: max(1, min(int(limit or 12), 50))]

    buckets = [
        lambda flags: bool(flags.get("exact_name_match")),
        lambda flags: bool(flags.get("symbol_match") and flags.get("route_term_match")),
        lambda flags: bool(flags.get("route_term_match")),
        lambda flags: bool(flags.get("bundle_match")),
        lambda flags: bool(flags.get("semantic_match") and int(flags.get("semantic_overlap_count") or 0) >= 3),
        lambda flags: bool(flags.get("symbol_match")),
        lambda flags: bool(flags.get("semantic_match")),
        lambda flags: bool(flags.get("family_literal_match")),
    ]

    ordered: List[Dict[str, Any]] = []
    seen = set()
    for bucket_index, predicate in enumerate(buckets, start=1):
        bucket_entries = [
            (entry, flags)
            for entry, flags in candidates
            if predicate(flags)
        ]
        for entry, flags in sorted(
            bucket_entries,
            key=lambda item: (
                -int(item[1].get("routing_hint_match_count") or 0),
                -int(item[1].get("exact_name_match_count") or 0),
                preferred_priority.get(str(item[0].get("path") or "").strip().lower(), 999),
                -int(item[1].get("longest_exact_route_match") or 0),
                -int(item[1].get("bundle_overlap_count") or 0),
                -int(item[1].get("semantic_overlap_count") or 0),
                -int(item[1].get("longest_semantic_match") or 0),
                -int(item[1].get("exact_route_match_count") or 0),
                str(item[0].get("workflow_family") or ""),
                str(item[0].get("path") or ""),
            ),
        ):
            path_value = str(entry.get("path") or "").strip().lower()
            if not path_value or path_value in seen:
                continue
            seen.add(path_value)
            ordered.append(_workflow_result_payload(entry, root, include_content=include_content, rank=bucket_index, query=query))
            if len(ordered) >= max(1, min(int(limit or 12), 50)):
                return ordered
    if ordered:
        return ordered[: max(1, min(int(limit or 12), 50))]
    return preferred[: max(1, min(int(limit or 12), 50))]


def _page_match_tuple(page: Dict[str, Any], query: str) -> Optional[Tuple[int, int, int, int, str]]:
    raw_query = str(query or "").strip()
    if not raw_query:
        priority = {
            "schema": 100,
            "home": 96,
            "index": 92,
            "workflow": 88,
            "howto": 86,
            "topic": 84,
            "concept": 83,
            "analysis": 82,
            "source": 80,
            "entity": 78,
            "decision": 76,
            "log": 58,
            "readme": 56,
            "method": 28,
        }
        return (0, -priority.get(str(page.get("kind") or ""), 10), 0, 0, str(page.get("path") or ""))

    query_info = _query_router_tokens(raw_query)
    query_blob = str(query_info.get("blob") or "")
    query_compacts = query_info.get("compacts") if isinstance(query_info.get("compacts"), list) else []

    title = str(page.get("title") or "").strip()
    path_value = str(page.get("path") or "").strip()
    summary = str(page.get("summary") or "").strip()
    content = str(page.get("content") or "")
    title_compact = compact_token(title)
    path_compact = compact_token(path_value)
    summary_compact = compact_token(summary)
    content_compact = compact_token(content)

    exact_title = bool(title_compact and title_compact in query_blob)
    exact_path = bool(path_compact and path_compact in query_blob)
    summary_match = any(compact and compact in summary_compact for compact in query_compacts)
    content_match = any(compact and compact in content_compact for compact in query_compacts)
    title_or_path_match = any(compact and (compact in title_compact or compact in path_compact) for compact in query_compacts)

    if not any([exact_title, exact_path, title_or_path_match, summary_match, content_match]):
        return None

    kind_priority = {
        "workflow": 0,
        "topic": 1,
        "analysis": 2,
        "source": 3,
        "entity": 4,
        "decision": 5,
        "page": 6,
        "schema": 7,
        "home": 8,
        "index": 9,
        "readme": 10,
        "log": 11,
    }
    return (
        0 if exact_title or exact_path else 1,
        0 if title_or_path_match else 1,
        0 if summary_match else 1,
        kind_priority.get(str(page.get("kind") or ""), 20),
        path_value,
    )



__all__ = [name for name in globals() if not name.startswith("__")]

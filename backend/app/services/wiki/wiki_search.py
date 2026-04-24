from ... import config
from .wiki_core import *  # noqa: F401,F403
from .wiki_manifest import _load_runtime_manifest_for_root
from .wiki_pages import _page_payload

_QUERY_ROUTER_TOKEN_CACHE: Dict[str, Dict[str, Any]] = {}
_QUERY_ROUTER_TOKEN_CACHE_LIMIT = 128
_WORKFLOW_ENTRY_PROFILE_CACHE: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
_WORKFLOW_ENTRY_PROFILE_CACHE_LIMIT = 4096
_WORKFLOW_FAMILY_RANK_MARGIN = max(0, int(getattr(config, "WORKFLOW_FAMILY_RANK_MARGIN", 18) or 18))
_WORKFLOW_FAMILY_COUNT_SCORE_WEIGHTS: Tuple[Tuple[str, int], ...] = (
    ("routing_hint_match_count", 40),
    ("exact_name_match_count", 24),
    ("exact_route_match_count", 18),
    ("bundle_overlap_count", 14),
    ("semantic_overlap_count", 8),
)
_WORKFLOW_FAMILY_BOOL_SCORE_WEIGHTS: Tuple[Tuple[str, int], ...] = (
    ("symbol_match", 20),
    ("bundle_match", 14),
    ("semantic_match", 10),
    ("family_literal_match", 8),
    ("route_term_match", 6),
)
_WORKFLOW_FAMILY_PRIORITY_FIELDS = (
    "routing_hint_match_count",
    "exact_name_match_count",
    "exact_route_match_count",
    "bundle_overlap_count",
    "symbol_match",
)

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


def _manifest_string_list(value: Any) -> Tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item or "").strip() for item in value if str(item or "").strip())


def _manifest_routing_hints(value: Any) -> Tuple[Tuple[Tuple[str, ...], Tuple[str, ...]], ...]:
    if not isinstance(value, list):
        return ()
    hints: List[Tuple[Tuple[str, ...], Tuple[str, ...]]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        all_of = _manifest_string_list(item.get("all_of"))
        any_of = _manifest_string_list(item.get("any_of"))
        if all_of or any_of:
            hints.append((all_of, any_of))
    return tuple(hints)


def _store_workflow_entry_profile_cache(key: Tuple[Any, ...], payload: Dict[str, Any]) -> Dict[str, Any]:
    _WORKFLOW_ENTRY_PROFILE_CACHE[key] = payload
    while len(_WORKFLOW_ENTRY_PROFILE_CACHE) > _WORKFLOW_ENTRY_PROFILE_CACHE_LIMIT:
        oldest_key = next(iter(_WORKFLOW_ENTRY_PROFILE_CACHE))
        _WORKFLOW_ENTRY_PROFILE_CACHE.pop(oldest_key, None)
    return payload


def _workflow_entry_match_profile(entry: Dict[str, Any]) -> Dict[str, Any]:
    path_value = str(entry.get("path") or "").strip()
    title = str(entry.get("title") or "").strip()
    summary = str(entry.get("summary") or "").strip()
    family = str(entry.get("workflow_family") or "").strip()
    aliases = _manifest_string_list(entry.get("aliases"))
    route_terms = _manifest_string_list(entry.get("route_terms"))
    symbols = _manifest_string_list(entry.get("symbols"))
    linked_method_symbols = _manifest_string_list(entry.get("linked_method_symbols"))
    semantic_terms = _manifest_string_list(entry.get("semantic_terms"))
    bundle_page_titles = _manifest_string_list(entry.get("bundle_page_titles"))
    bundle_page_summaries = _manifest_string_list(entry.get("bundle_page_summaries"))
    routing_hints = _manifest_routing_hints(entry.get("routing_hints"))
    cache_key = (
        path_value,
        title,
        summary,
        family,
        aliases,
        route_terms,
        symbols,
        linked_method_symbols,
        semantic_terms,
        bundle_page_titles,
        bundle_page_summaries,
        routing_hints,
    )
    cached = _WORKFLOW_ENTRY_PROFILE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    path_stem = PurePosixPath(path_value).stem
    payload = {
        "family": family,
        "exact_candidates": tuple(_compact_values([title, path_stem, *aliases])),
        "route_compacts": tuple(_expand_manifest_match_tokens([title, path_stem, family, *aliases, *route_terms, *symbols, *linked_method_symbols])),
        "symbol_compacts": tuple(_expand_manifest_match_tokens([*symbols, *linked_method_symbols])),
        "semantic_compacts": tuple(_expand_manifest_match_tokens([title, summary, *semantic_terms, *bundle_page_titles, *bundle_page_summaries])),
        "bundle_compacts": tuple(_expand_manifest_match_tokens([*bundle_page_titles, *bundle_page_summaries])),
        "semantic_terms": semantic_terms,
        "bundle_page_titles": bundle_page_titles,
        "bundle_page_summaries": bundle_page_summaries,
        "routing_hints": routing_hints,
    }
    return _store_workflow_entry_profile_cache(cache_key, payload)


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


def _workflow_family_entry_score(flags: Dict[str, Any]) -> int:
    return sum(
        int(flags.get(name) or 0) * weight
        for name, weight in _WORKFLOW_FAMILY_COUNT_SCORE_WEIGHTS
    ) + sum(
        weight if bool(flags.get(name)) else 0
        for name, weight in _WORKFLOW_FAMILY_BOOL_SCORE_WEIGHTS
    )


def _manifest_family_score_table(
    workflow_index: Sequence[Dict[str, Any]],
    *,
    query_info: Dict[str, Any],
) -> Dict[str, Dict[str, int]]:
    family_scores: Dict[str, Dict[str, int]] = {}
    for entry in workflow_index:
        if not isinstance(entry, dict):
            continue
        family = str(entry.get("workflow_family") or "").strip()
        if not family:
            continue
        flags = _workflow_router_match_flags(entry, query_info)
        if not (
            bool(flags.get("exact_name_match"))
            or bool(flags.get("route_term_match"))
            or bool(flags.get("symbol_match"))
            or bool(flags.get("bundle_match"))
            or bool(flags.get("semantic_match"))
            or bool(flags.get("family_literal_match"))
            or int(flags.get("routing_hint_match_count") or 0) > 0
        ):
            continue
        current = family_scores.setdefault(
            family,
            {
                "score": 0,
                "routing_hint_match_count": 0,
                "exact_name_match_count": 0,
                "exact_route_match_count": 0,
                "bundle_overlap_count": 0,
                "semantic_overlap_count": 0,
                "symbol_match": 0,
                "bundle_match": 0,
                "semantic_match": 0,
                "family_literal_match": 0,
            },
        )
        current["score"] = max(current["score"], _workflow_family_entry_score(flags))
        current["routing_hint_match_count"] = max(current["routing_hint_match_count"], int(flags.get("routing_hint_match_count") or 0))
        current["exact_name_match_count"] = max(current["exact_name_match_count"], int(flags.get("exact_name_match_count") or 0))
        current["exact_route_match_count"] = max(current["exact_route_match_count"], int(flags.get("exact_route_match_count") or 0))
        current["bundle_overlap_count"] = max(current["bundle_overlap_count"], int(flags.get("bundle_overlap_count") or 0))
        current["semantic_overlap_count"] = max(current["semantic_overlap_count"], int(flags.get("semantic_overlap_count") or 0))
        current["symbol_match"] = max(current["symbol_match"], 1 if bool(flags.get("symbol_match")) else 0)
        current["bundle_match"] = max(current["bundle_match"], 1 if bool(flags.get("bundle_match")) else 0)
        current["semantic_match"] = max(current["semantic_match"], 1 if bool(flags.get("semantic_match")) else 0)
        current["family_literal_match"] = max(current["family_literal_match"], 1 if bool(flags.get("family_literal_match")) else 0)
    return family_scores


def _ordered_manifest_family_scores(
    family_scores: Dict[str, Dict[str, int]],
) -> List[Tuple[str, Dict[str, int]]]:
    return sorted(
        family_scores.items(),
        key=lambda item: (
            -int(item[1]["score"]),
            -int(item[1]["routing_hint_match_count"]),
            -int(item[1]["exact_name_match_count"]),
            -int(item[1]["exact_route_match_count"]),
            -int(item[1]["bundle_overlap_count"]),
            -int(item[1]["semantic_overlap_count"]),
            item[0],
        ),
    )


def _manifest_family_preferences(
    root: Path,
    *,
    query: str,
    workflow_index: Optional[Sequence[Dict[str, Any]]] = None,
    rankings: Optional[Sequence[Dict[str, Any]]] = None,
    limit: int = 6,
) -> Dict[str, List[str]]:
    preferred: List[str] = []
    priority: List[str] = []
    safe_limit = max(1, int(limit or 6))
    if not isinstance(rankings, Sequence):
        rankings = _manifest_family_rankings(
            root,
            query=query,
            workflow_index=workflow_index,
            limit=safe_limit,
        )
    for item in rankings:
        if not isinstance(item, dict):
            continue
        family = str(item.get("family") or "").strip()
        if not family:
            continue
        if len(preferred) < safe_limit:
            preferred.append(family)
        if (
            any(int(item.get(field) or 0) > 0 for field in _WORKFLOW_FAMILY_PRIORITY_FIELDS)
        ):
            priority.append(family)
        if len(preferred) >= safe_limit and len(priority) >= min(3, safe_limit):
            break

    return {
        "preferred_families": preferred,
        "priority_families": priority[: min(3, safe_limit)],
    }


def _manifest_family_rankings(
    root: Path,
    *,
    query: str,
    workflow_index: Optional[Sequence[Dict[str, Any]]] = None,
    limit: int = 6,
) -> List[Dict[str, Any]]:
    if not isinstance(workflow_index, Sequence):
        manifest = _load_runtime_manifest_for_root(root)
        workflow_index = manifest.get("workflow_index") if isinstance(manifest.get("workflow_index"), list) else []
    if not workflow_index:
        return []

    query_info = _query_router_tokens(query)
    family_scores = _manifest_family_score_table(workflow_index, query_info=query_info)
    ordered = _ordered_manifest_family_scores(family_scores)

    results: List[Dict[str, Any]] = []
    for family, stats in ordered[: max(1, int(limit or 6))]:
        results.append(
            {
                "family": family,
                "score": int(stats["score"]),
                "routing_hint_match_count": int(stats["routing_hint_match_count"]),
                "exact_name_match_count": int(stats["exact_name_match_count"]),
                "exact_route_match_count": int(stats["exact_route_match_count"]),
                "bundle_overlap_count": int(stats["bundle_overlap_count"]),
                "semantic_overlap_count": int(stats["semantic_overlap_count"]),
                "symbol_match": int(stats["symbol_match"]),
            }
        )
    return results


def _compact_query_matches(query_blob: str, query_compacts: Sequence[str], candidate: str) -> bool:
    normalized_candidate = compact_token(candidate)
    if not normalized_candidate:
        return False
    if normalized_candidate in query_compacts:
        return True
    if len(normalized_candidate) >= 2 and normalized_candidate in str(query_blob or ""):
        return True
    return False


def _routing_hint_match_count_from_hints(
    hints: Sequence[Tuple[Sequence[str], Sequence[str]]],
    query_info: Dict[str, Any],
) -> int:
    if not hints:
        return 0
    query_blob = str(query_info.get("blob") or "")
    query_terms = query_info.get("semantic_tokens") if isinstance(query_info.get("semantic_tokens"), list) else []
    matched = 0
    for all_of, any_of in hints:
        all_match = all(_compact_query_matches(query_blob, query_terms, value) for value in all_of) if all_of else True
        any_match = any(_compact_query_matches(query_blob, query_terms, value) for value in any_of) if any_of else True
        if all_match and any_match:
            matched += 1
    return matched


def _workflow_router_match_flags(entry: Dict[str, Any], query_info: Dict[str, Any]) -> Dict[str, Any]:
    profile = _workflow_entry_match_profile(entry)
    family = str(profile.get("family") or "")
    exact_candidates = profile.get("exact_candidates") if isinstance(profile.get("exact_candidates"), tuple) else ()
    route_compacts = profile.get("route_compacts") if isinstance(profile.get("route_compacts"), tuple) else ()
    symbol_compacts = profile.get("symbol_compacts") if isinstance(profile.get("symbol_compacts"), tuple) else ()
    semantic_compacts = profile.get("semantic_compacts") if isinstance(profile.get("semantic_compacts"), tuple) else ()
    bundle_compacts = profile.get("bundle_compacts") if isinstance(profile.get("bundle_compacts"), tuple) else ()
    semantic_terms = profile.get("semantic_terms") if isinstance(profile.get("semantic_terms"), tuple) else ()
    bundle_page_titles = profile.get("bundle_page_titles") if isinstance(profile.get("bundle_page_titles"), tuple) else ()
    bundle_page_summaries = profile.get("bundle_page_summaries") if isinstance(profile.get("bundle_page_summaries"), tuple) else ()
    routing_hints = profile.get("routing_hints") if isinstance(profile.get("routing_hints"), tuple) else ()

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
    routing_hint_match_count = _routing_hint_match_count_from_hints(routing_hints, query_info)

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
    if not isinstance(workflow_index, Sequence):
        manifest = _load_runtime_manifest_for_root(root)
        workflow_index = manifest.get("workflow_index") if isinstance(manifest.get("workflow_index"), list) else []
    family_order = [str(item or "").strip() for item in families if str(item or "").strip()]
    ordered: List[str] = []
    seen = set()
    for family in family_order:
        for entry in workflow_index:
            if not isinstance(entry, dict) or str(entry.get("workflow_family") or "").strip() != family:
                continue
            path_value = str(entry.get("path") or "").strip().lower()
            if not path_value or path_value in seen:
                continue
            seen.add(path_value)
            ordered.append(path_value)
            if len(ordered) >= 50:
                return ordered
    return ordered


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

    safe_limit = max(1, min(int(limit or 12), 50))
    preferred_payloads: Optional[List[Dict[str, Any]]] = None

    def preferred_results() -> List[Dict[str, Any]]:
        nonlocal preferred_payloads
        if preferred_payloads is None:
            preferred_payloads = _workflow_results_for_families(
                root,
                families=preferred_families or [],
                include_content=include_content,
                query=query,
                limit=safe_limit,
                workflow_index=workflow_index,
            )
        return preferred_payloads

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
            return preferred_results()[:safe_limit]

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
            if len(ordered_priority) >= safe_limit:
                return ordered_priority
        if ordered_priority:
            remaining = [item for item in preferred_results() if str(item.get("path") or "").strip().lower() not in seen_priority]
            return [*ordered_priority, *remaining][:safe_limit]

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
            if len(ordered) >= safe_limit:
                return ordered
    if ordered:
        return ordered[:safe_limit]
    return preferred_results()[:safe_limit]


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

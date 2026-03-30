import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ... import rag_config
from ...utils.encoding import TEXT_ENCODING_FALLBACKS, decode_bytes
from .code_runtime import iter_code_roots
from .query_terms import compact_token as _compact_symbol
from .query_terms import extract_query_compacts
from .query_terms import extract_symbol_query_candidates as extract_symbol_candidates
from .query_terms import identifier_structure_score as _structure_signal_score
from .query_terms import split_identifier_parts as _split_symbol_parts
from .query_strategy import (
    expand_line_window,
    is_usage_entrypoint_file,
    is_usage_example_path,
    merge_code_matches,
    normalize_usage_path,
    parse_line_range,
    prioritize_usage_matches,
    strip_usage_companion_suffixes,
    usage_match_score,
)
from .runtime import read_code_lines, search_code

_COMMON_TYPE_TOKENS = {
    "string",
    "bool",
    "boolean",
    "int",
    "float",
    "double",
    "void",
    "return",
    "public",
    "private",
    "protected",
    "internal",
    "static",
    "class",
    "namespace",
    "using",
    "object",
    "event",
    "sender",
    "args",
}
_USAGE_SECTION_ORDER = [
    "definition",
    "usage",
    "calls",
    "updates",
    "support",
]
_IMPLEMENTATION_STEP_SPECS = [
    ("definition", "definition", "definition or anchor location"),
    ("usage", "usage", "observed usage sites"),
    ("calls", "calls", "direct or member calls"),
    ("updates", "updates", "assignments or state transitions"),
    ("support", "support", "supporting context"),
]
_SYMBOL_FILE_PATTERNS = (
    "**/src/**/*.*",
    "**/source/**/*.*",
    "**/app/**/*.*",
    "**/apps/**/*.*",
    "**/lib/**/*.*",
    "**/modules/**/*.*",
    "**/packages/**/*.*",
    "**/examples/**/*.*",
    "**/example/**/*.*",
    "**/samples/**/*.*",
    "**/sample/**/*.*",
    "**/demo/**/*.*",
    "**/*.*",
)
_SEARCH_EXPANSION_STOP_TOKENS = {
    "class",
    "false",
    "generated",
    "gen",
    "namespace",
    "private",
    "protected",
    "public",
    "return",
    "source",
    "src",
    "static",
    "string",
    "system",
    "test",
    "tests",
    "this",
    "true",
    "using",
    "void",
}
_CONTENT_SYMBOL_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b")
_CALL_LIKE_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\(")
_MEMBER_CALL_RE = re.compile(r"(?:\.|->)[A-Za-z_][A-Za-z0-9_]*\s*\(")
_MEMBER_ASSIGN_RE = re.compile(r"(?:\.|->)[A-Za-z_][A-Za-z0-9_]*\s*=")
_DEFINITION_HINT_RE = re.compile(r"\b(?:class|struct|interface|enum|record|namespace|module|typedef|def|function)\b")
_REPO_SYMBOL_CANDIDATE_SCORE_DEFAULTS = {
    "query_exact": 14.0,
    "query_suffix": 10.0,
    "query_contains": 6.0,
    "path_stem_hit": 0.0,
    "path_hit": 0.0,
    "match_hit": 0.0,
    "definition_hit": 0.0,
    "example_hit": 0.0,
    "content_hit": 0.0,
    "structure_multiplier": 1.0,
}
_SEARCH_EXPANSION_TERM_SCORE_DEFAULTS = {
    "query_exact": 18.0,
    "query_suffix": 12.0,
    "query_contains": 7.0,
    "path_stem_hit": 0.0,
    "path_hit": 0.0,
    "match_hit": 0.0,
    "definition_hit": 0.0,
    "example_hit": 0.0,
    "content_hit": 0.0,
    "structure_multiplier": 1.0,
}
_FILE_PROFILE_SCORE_DEFAULTS = {
    "category_unit": 10,
    "usage_bonus": 6,
    "calls_bonus": 5,
    "updates_bonus": 4,
    "definition_bonus": 3,
}
_PATH_RELEVANCE_SCORE_DEFAULTS = {
    "min_token_bonus": 2,
}
_TERM_SUPPORT_SCORE_DEFAULTS = {
    "query_exact": 10.0,
    "query_suffix": 6.0,
    "query_contains": 3.0,
    "path_stem_hit": 5.0,
    "path_hit": 2.0,
    "match_hit": 2.0,
    "definition_hit": 2.5,
    "example_hit": 1.5,
    "content_hit": 1.5,
    "structure_multiplier": 0.75,
}
_MATCH_RERANK_SCORE_DEFAULTS = {
    "cluster_bonus": 6.0,
    "dir_bonus": 3.5,
    "entrypoint_bonus": 1.5,
}


def _unique_preserving_order(values: Sequence[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for value in values:
        token = str(value or "").strip()
        if not token or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def _strip_companion_suffixes(stem: str) -> str:
    return strip_usage_companion_suffixes(stem)


def _read_text_prefix(path: Path, max_bytes: int = 16000) -> str:
    try:
        raw = path.read_bytes()[:max_bytes]
    except Exception:
        return ""
    return decode_bytes(raw, TEXT_ENCODING_FALLBACKS)


def _score_repo_symbol_candidate(symbol: str, query_compacts: Sequence[str]) -> int:
    compact = _compact_symbol(symbol)
    if not compact:
        return 0
    support = _empty_term_support(symbol, compact, query_compacts)
    return int(_score_term_support(support, weight_name="repo_symbol_candidate_score"))


def _compact_overlap_flags(compact: str, query_compacts: Sequence[str]) -> Dict[str, int]:
    flags = {"query_exact": 0, "query_suffix": 0, "query_contains": 0}
    for query_compact in query_compacts:
        if not query_compact:
            continue
        if compact == query_compact:
            flags["query_exact"] = 1
        elif compact.endswith(query_compact) or query_compact.endswith(compact):
            flags["query_suffix"] = 1
        elif query_compact in compact or compact in query_compact:
            flags["query_contains"] = 1
    return flags


def _empty_term_support(term: str, compact: str, query_compacts: Sequence[str]) -> Dict[str, Any]:
    flags = _compact_overlap_flags(compact, query_compacts)
    return {
        "term": term,
        "compact": compact,
        "query_exact": flags["query_exact"],
        "query_suffix": flags["query_suffix"],
        "query_contains": flags["query_contains"],
        "path_stem_hits": 0,
        "path_hits": 0,
        "match_hits": 0,
        "definition_hits": 0,
        "example_hits": 0,
        "content_hits": 0,
        "structure_score": _structure_signal_score(term),
    }


def _score_term_support(support: Dict[str, Any], weight_name: str = "term_support_score") -> float:
    weights = rag_config.heuristics_weights(weight_name, _TERM_SUPPORT_SCORE_DEFAULTS)
    return (
        int(support.get("query_exact") or 0) * float(weights["query_exact"])
        + int(support.get("query_suffix") or 0) * float(weights["query_suffix"])
        + int(support.get("query_contains") or 0) * float(weights["query_contains"])
        + int(support.get("path_stem_hits") or 0) * float(weights["path_stem_hit"])
        + int(support.get("path_hits") or 0) * float(weights["path_hit"])
        + int(support.get("match_hits") or 0) * float(weights["match_hit"])
        + int(support.get("definition_hits") or 0) * float(weights["definition_hit"])
        + int(support.get("example_hits") or 0) * float(weights["example_hit"])
        + int(support.get("content_hits") or 0) * float(weights["content_hit"])
        + float(support.get("structure_score") or 0.0) * float(weights["structure_multiplier"])
    )


def _collect_match_term_support(
    matches: Sequence[Dict[str, Any]],
    query: str,
    *,
    seed_terms: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    query_candidates = extract_symbol_candidates(query)
    query_compacts = list(extract_query_compacts(query, limit=12))
    for term in [*(seed_terms or []), *query_candidates]:
        compact = _compact_symbol(term)
        if not compact or compact in query_compacts:
            continue
        query_compacts.append(compact)
        if len(query_compacts) >= 12:
            break

    candidate_terms: List[str] = [*(seed_terms or []), *query_candidates]
    for row in matches or []:
        candidate_terms.extend(_iter_match_path_terms(str(row.get("path") or "")))
        candidate_terms.extend(_CONTENT_SYMBOL_RE.findall(str(row.get("match") or "")))

    supports: Dict[str, Dict[str, Any]] = {}
    for term in _unique_preserving_order(candidate_terms):
        compact = _compact_symbol(term)
        if not compact or _is_search_noise_token(term):
            continue
        support = supports.get(compact)
        if support is None:
            support = _empty_term_support(term, compact, query_compacts)
            supports[compact] = support
        elif _structure_signal_score(term) > int(support.get("structure_score") or 0):
            support["term"] = term
            support["structure_score"] = _structure_signal_score(term)

    for row in matches or []:
        path = str(row.get("path") or "")
        normalized_path = _normalize_path(path)
        path_compact = _compact_symbol(normalized_path)
        path_stem_compact = _compact_symbol(_strip_companion_suffixes(Path(normalized_path).stem))
        match_text = str(row.get("match") or "")
        match_compact = _compact_symbol(match_text)
        is_example = _is_example_path(path)
        has_definition_hint = bool(_DEFINITION_HINT_RE.search(match_text.lower()))
        for compact, support in supports.items():
            path_hit = compact in path_compact if path_compact else False
            match_hit = compact in match_compact if match_compact else False
            if compact == path_stem_compact:
                support["path_stem_hits"] = int(support["path_stem_hits"]) + 1
            elif path_hit:
                support["path_hits"] = int(support["path_hits"]) + 1
            if match_hit:
                support["match_hits"] = int(support["match_hits"]) + 1
                support["content_hits"] = int(support["content_hits"]) + 1
                if has_definition_hint:
                    support["definition_hits"] = int(support["definition_hits"]) + 1
            if is_example and (path_hit or match_hit or compact == path_stem_compact):
                support["example_hits"] = int(support["example_hits"]) + 1

    ranked = list(supports.values())
    ranked.sort(
        key=lambda item: (
            _score_term_support(item),
            int(item.get("path_stem_hits") or 0),
            int(item.get("match_hits") or 0),
            len(str(item.get("term") or "")),
        ),
        reverse=True,
    )
    return ranked


def _is_search_noise_token(token: str) -> bool:
    lowered = str(token or "").strip().lower()
    compact = _compact_symbol(lowered)
    if not compact or len(compact) < 3:
        return True
    return (
        lowered in _SEARCH_EXPANSION_STOP_TOKENS
        or lowered in _COMMON_TYPE_TOKENS
    )


def _iter_match_path_terms(path: str) -> List[str]:
    normalized = _normalize_path(path)
    if not normalized:
        return []
    parsed = Path(normalized)
    tokens: List[str] = []
    stem = parsed.stem
    if stem and stem.lower() not in _SEARCH_EXPANSION_STOP_TOKENS:
        tokens.append(stem)
    for part in parsed.parts:
        if part.lower() in {"source", "src"}:
            continue
        stem = Path(part).stem
        if stem and stem.lower() not in _SEARCH_EXPANSION_STOP_TOKENS:
            tokens.append(stem)
    return _unique_preserving_order(tokens)


def _has_example_matches(rows: Sequence[Dict[str, Any]]) -> bool:
    return any(str(row.get("path") or "").strip() for row in rows or [])


def _extract_search_expansion_terms(
    matches: Sequence[Dict[str, Any]],
    primary_symbol: str,
    query: str,
    limit: int = 6,
) -> List[str]:
    seed_terms: List[str] = [*extract_symbol_candidates(query)]
    if primary_symbol:
        seed_terms.extend([primary_symbol, *_split_symbol_parts(primary_symbol)])
    supports = _collect_match_term_support(matches, query, seed_terms=seed_terms)
    primary_compact = _compact_symbol(primary_symbol)
    query_compacts = {_compact_symbol(term) for term in extract_symbol_candidates(query)}
    terms: List[str] = []
    for support in supports:
        compact = str(support.get("compact") or "")
        if not compact or compact == primary_compact or compact in query_compacts:
            continue
        if int(support.get("path_hits") or 0) <= 0 and int(support.get("match_hits") or 0) <= 0 and int(support.get("path_stem_hits") or 0) <= 0:
            continue
        terms.append(str(support.get("term") or ""))
        if len(terms) >= max(1, int(limit or 1)):
            break
    return terms


def _is_example_path(path: str) -> bool:
    return is_usage_example_path(path)


def _normalize_path(path: str) -> str:
    return normalize_usage_path(path)


def _example_dir(path: str) -> str:
    normalized = _normalize_path(path)
    if not normalized:
        return ""
    return str(Path(normalized).parent).replace("\\", "/")


def _normalized_example_stem(path: str) -> str:
    normalized = _normalize_path(path)
    return _strip_companion_suffixes(Path(normalized).stem)


def _example_cluster(path: str) -> str:
    directory = _example_dir(path)
    if not directory:
        return ""
    stem = _normalized_example_stem(path)
    if not stem:
        return ""
    return f"{directory}::{stem}"


def _path_in_dir(path: str, directory: str) -> bool:
    normalized = _normalize_path(path).lower().rstrip("/")
    target = _normalize_path(directory).lower().rstrip("/")
    return bool(normalized and target) and (normalized == target or normalized.startswith(f"{target}/"))


def _path_in_cluster(path: str, cluster: str) -> bool:
    normalized_cluster = str(cluster or "").strip().lower()
    if not normalized_cluster:
        return False
    return _example_cluster(path).lower() == normalized_cluster


def _focus_dir_row_score(row: Dict[str, Any], symbol: str) -> float:
    return usage_match_score(row, query_text=symbol, preferred_symbol=symbol)


def _select_focus_example_dir(matches: Sequence[Dict[str, Any]], symbol: str) -> str:
    dir_scores: Dict[str, List[float]] = {}
    for row in matches or []:
        directory = _example_dir(str(row.get("path") or ""))
        if not directory:
            continue
        dir_scores.setdefault(directory, []).append(_focus_dir_row_score(row, symbol))
    if not dir_scores:
        return ""
    ranked = sorted(
        (
            (directory, sum(sorted(scores, reverse=True)[:4]))
            for directory, scores in dir_scores.items()
        ),
        key=lambda item: (-item[1], len(item[0]), item[0].lower()),
    )
    return ranked[0][0]


def _select_focus_example_cluster(matches: Sequence[Dict[str, Any]], symbol: str) -> str:
    cluster_scores: Dict[str, List[float]] = {}
    for row in matches or []:
        cluster = _example_cluster(str(row.get("path") or ""))
        if not cluster:
            continue
        cluster_scores.setdefault(cluster, []).append(_focus_dir_row_score(row, symbol))
    if not cluster_scores:
        return ""
    ranked = sorted(
        (
            (cluster, sum(sorted(scores, reverse=True)[:4]))
            for cluster, scores in cluster_scores.items()
        ),
        key=lambda item: (-item[1], len(item[0]), item[0].lower()),
    )
    return ranked[0][0]


def _symbol_path_tokens(symbol: str) -> List[str]:
    raw = str(symbol or "").strip()
    if not raw:
        return []
    lowered = [part.lower() for part in _split_symbol_parts(raw) if part]
    compact = "".join(lowered)
    return _unique_preserving_order([compact, *lowered])


def _path_relevance_score(path: str, symbol: str) -> int:
    weights = rag_config.heuristics_weights("path_relevance_score", _PATH_RELEVANCE_SCORE_DEFAULTS)
    normalized = str(path or "").replace("\\", "/").lower()
    tokens = _symbol_path_tokens(symbol)
    score = 0
    for token in tokens:
        if not token:
            continue
        if token in normalized:
            score += max(int(weights["min_token_bonus"]), len(token))
    return score


def _is_symbol_family_path(path: str, symbol: str) -> bool:
    normalized = str(path or "").replace("\\", "/").lower()
    tokens = _symbol_path_tokens(symbol)
    if not tokens:
        return False
    strong_tokens = [token for token in tokens if len(token) >= 5]
    if any(token and token in normalized for token in strong_tokens):
        return True
    file_name = Path(normalized).name
    stem = Path(normalized).stem
    compact = "".join(ch for ch in str(symbol or "").lower() if ch.isalnum())
    file_name_compact = _compact_symbol(file_name)
    stem_compact = _compact_symbol(stem)
    return bool(compact) and (compact in file_name_compact or compact in stem_compact)


def _usage_match_sort_key(row: Dict[str, Any], symbol: str, query_text: str) -> Tuple[float, int, int]:
    path = str(row.get("path") or "")
    score = usage_match_score(row, query_text=query_text, preferred_symbol=symbol)
    return (
        score,
        _path_relevance_score(path, symbol),
        1 if _is_symbol_family_path(path, symbol) else 0,
    )


def _match_rerank_score(
    row: Dict[str, Any],
    *,
    symbol: str,
    query_text: str,
    focus_example_dir: str = "",
    focus_example_cluster: str = "",
) -> float:
    weights = rag_config.heuristics_weights("match_rerank_score", _MATCH_RERANK_SCORE_DEFAULTS)
    score = usage_match_score(row, query_text=query_text, preferred_symbol=symbol)
    path = str(row.get("path") or "")
    if focus_example_cluster and _path_in_cluster(path, focus_example_cluster):
        score += float(weights["cluster_bonus"])
    elif focus_example_dir and _path_in_dir(path, focus_example_dir):
        score += float(weights["dir_bonus"])
    return score


def _extract_handler_candidates(rows: Sequence[Dict[str, Any]]) -> List[str]:
    return []


def _extract_symbol_mentions(rows: Sequence[Dict[str, Any]]) -> List[str]:
    tokens: List[str] = []
    for row in rows or []:
        path = str(row.get("path") or "")
        match = str(row.get("match") or "")
        stem = Path(path).stem
        if stem:
            tokens.append(stem)
        for text in (match, path):
            for token in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b", text):
                tokens.append(token)
    return _unique_preserving_order(tokens)


def _extract_path_stems(rows: Sequence[Dict[str, Any]]) -> List[str]:
    stems: List[str] = []
    for row in rows or []:
        path = str(row.get("path") or "")
        stem = _strip_companion_suffixes(Path(path).stem)
        if stem:
            stems.append(stem)
    return _unique_preserving_order(stems)


def _resolve_symbol_from_matches(matches: Sequence[Dict[str, Any]], fallback_query: str) -> str:
    seed_terms = [*extract_symbol_candidates(fallback_query), *_extract_path_stems(matches)]
    supports = _collect_match_term_support(matches, fallback_query, seed_terms=seed_terms)
    if not supports:
        return ""
    top = supports[0]
    return str(top.get("term") or "")


def _resolve_symbol_from_code_index(code_tools, fallback_query: str) -> str:
    query_tokens = extract_symbol_candidates(fallback_query)
    seed_terms = [*query_tokens]
    supports: Dict[str, Dict[str, Any]] = {}
    scanned = 0
    for root in iter_code_roots(code_tools):
        for pattern in _SYMBOL_FILE_PATTERNS:
            for file_path in root.glob(pattern):
                if not file_path.is_file():
                    continue
                scanned += 1
                if scanned > 4000:
                    break
                stem = _strip_companion_suffixes(file_path.stem)

                symbol_candidates = []
                if stem:
                    symbol_candidates.append(stem)
                text_prefix = _read_text_prefix(file_path)
                if text_prefix:
                    symbol_candidates.extend(_unique_preserving_order(_CONTENT_SYMBOL_RE.findall(text_prefix))[:40])

                for symbol in _unique_preserving_order(symbol_candidates):
                    compact = _compact_symbol(symbol)
                    if not compact or _is_search_noise_token(symbol):
                        continue
                    support = supports.get(compact)
                    if support is None:
                        support = _empty_term_support(symbol, compact, [_compact_symbol(term) for term in seed_terms if _compact_symbol(term)])
                        supports[compact] = support
                    elif _structure_signal_score(symbol) > int(support.get("structure_score") or 0):
                        support["term"] = symbol
                        support["structure_score"] = _structure_signal_score(symbol)
                    if symbol == stem:
                        support["path_stem_hits"] = int(support["path_stem_hits"]) + 1
                    else:
                        support["content_hits"] = int(support["content_hits"]) + 1
                    if _is_example_path(str(file_path)):
                        support["example_hits"] = int(support["example_hits"]) + 1
            if scanned > 4000:
                break
        if scanned > 4000:
            break

    ranked = sorted(
        supports.values(),
        key=lambda item: (
            _score_term_support(item),
            int(item.get("path_stem_hits") or 0),
            int(item.get("content_hits") or 0),
            len(str(item.get("term") or "")),
        ),
        reverse=True,
    )
    if not ranked:
        return ""
    return str(ranked[0].get("term") or "")


def _symbol_quality_score(symbol: str) -> Tuple[int, int, int]:
    raw = str(symbol or "")
    return (
        len(_split_symbol_parts(raw)),
        len(_compact_symbol(raw)),
        1 if any(ch.isdigit() for ch in raw) else 0,
    )


def _choose_canonical_symbol(indexed_symbol: str, matched_symbol: str) -> str:
    indexed = str(indexed_symbol or "").strip()
    matched = str(matched_symbol or "").strip()
    if indexed and not matched:
        return indexed
    if matched and not indexed:
        return matched
    if not indexed and not matched:
        return ""

    indexed_compact = _compact_symbol(indexed)
    matched_compact = _compact_symbol(matched)
    if indexed_compact and matched_compact and indexed_compact == matched_compact:
        return indexed if _symbol_quality_score(indexed) >= _symbol_quality_score(matched) else matched

    if indexed_compact and matched_compact:
        if indexed_compact.endswith(matched_compact):
            return indexed
        if matched_compact.endswith(indexed_compact):
            return matched

    return indexed if _symbol_quality_score(indexed) >= _symbol_quality_score(matched) else matched


def _infer_primary_symbol(matches: Sequence[Dict[str, Any]], fallback_query: str) -> str:
    resolved = _resolve_symbol_from_matches(matches, fallback_query)
    if resolved:
        return resolved

    candidates = extract_symbol_candidates(fallback_query)
    if candidates:
        return candidates[0]

    for row in matches or []:
        path = Path(str(row.get("path") or ""))
        stem = path.stem
        if stem and len(_compact_symbol(stem)) >= 4:
            return stem
    return ""


def _build_generic_follow_up_queries(seed: str) -> List[str]:
    return []


def _build_usage_search_queries(symbol: str, query_text: str) -> List[Tuple[str, Optional[str]]]:
    cleaned_symbol = str(symbol or "").strip()
    queries: List[Tuple[str, Optional[str]]] = []
    primary_query = cleaned_symbol or str(query_text or "").strip()
    if primary_query:
        queries.append((primary_query, None))
    if cleaned_symbol and str(query_text or "").strip() and cleaned_symbol != str(query_text or "").strip():
        queries.append((str(query_text or "").strip(), None))
    deduped: List[Tuple[str, Optional[str]]] = []
    seen = set()
    for query_value, path_filter in queries:
        key = f"{str(query_value or '').strip().lower()}::{str(path_filter or '').strip().lower()}"
        if not str(query_value or "").strip() or key in seen:
            continue
        seen.add(key)
        deduped.append((query_value, path_filter))
    return deduped


def _exact_symbol_query(symbol: str) -> str:
    return rf"re:\b{re.escape(str(symbol or '').strip())}\b"


def _select_candidate_paths(matches: Sequence[Dict[str, Any]], max_paths: int = 4) -> List[str]:
    return _unique_preserving_order([str(row.get("path") or "") for row in matches])[:max_paths]


def _serialize_match(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "path": str(row.get("path") or ""),
        "line_range": str(row.get("line_range") or ""),
        "match": str(row.get("match") or "")[:240],
    }


def _serialize_window(window: Dict[str, Any], max_excerpt_chars: int = 1400) -> Dict[str, Any]:
    excerpt = str(window.get("content") or "")
    if len(excerpt) > max_excerpt_chars:
        excerpt = excerpt[:max_excerpt_chars]
    return {
        "path": str(window.get("path") or ""),
        "line_range": str(window.get("line_range") or ""),
        "excerpt": excerpt,
    }


def _line_range_start(line_range: str) -> int:
    start, _ = parse_line_range(line_range)
    return start


def _max_windows_for_path(path: str) -> int:
    normalized = str(path or "").replace("\\", "/").lower()
    if any(token in normalized for token in ("/generated/", "/gen/", "/dist/", "/build/")):
        return 1
    if normalized.endswith((".h", ".hh", ".hpp", ".hxx")):
        return 1
    return 2


def _categorize_usage_window(window: Dict[str, Any], symbol: str) -> List[str]:
    path = str(window.get("path") or "").replace("\\", "/").lower()
    content = str(window.get("content") or "")
    lowered = content.lower()
    symbol_lower = str(symbol or "").lower()
    categories: List[str] = []
    call_count = len(_CALL_LIKE_RE.findall(content))
    member_call_count = len(_MEMBER_CALL_RE.findall(content))
    assignment_count = len(_MEMBER_ASSIGN_RE.findall(content))
    query_compact = _compact_symbol(symbol_lower)
    path_compact = _compact_symbol(path)
    content_compact = _compact_symbol(content)

    if _DEFINITION_HINT_RE.search(lowered) or Path(path).stem.lower() == symbol_lower.lower():
        categories.append("definition")
    if call_count > 0 or member_call_count > 0:
        categories.append("usage")
    if member_call_count > 0 or call_count >= 2:
        categories.append("calls")
    if assignment_count > 0:
        categories.append("updates")
    if query_compact and (query_compact in path_compact or query_compact in content_compact):
        categories.append("support")
    if not categories:
        categories.append("support")
    return _unique_preserving_order(categories)


def _extract_related_types(windows: Sequence[Dict[str, Any]], primary_symbol: str) -> List[str]:
    counts: Dict[str, int] = {}
    primary_lower = str(primary_symbol or "").lower()
    for window in windows or []:
        text = str(window.get("content") or "")
        for token in re.findall(r"\b[A-Z][A-Za-z0-9_]{2,}\b", text):
            lowered = token.lower()
            if lowered == primary_lower or lowered in _COMMON_TYPE_TOKENS:
                continue
            counts[token] = counts.get(token, 0) + 1
    ranked = sorted(
        counts.items(),
        key=lambda item: (-item[1], -_structure_signal_score(item[0]), -len(item[0]), item[0].lower()),
    )
    return [token for token, _ in ranked[:8]]


def _build_file_profiles(
    windows: Sequence[Dict[str, Any]],
    primary_symbol: str,
) -> List[Dict[str, Any]]:
    weights = rag_config.heuristics_weights("file_profile_score", _FILE_PROFILE_SCORE_DEFAULTS)
    profiles: Dict[str, Dict[str, Any]] = {}
    for window in windows or []:
        path = str(window.get("path") or "").strip()
        if not path:
            continue
        serialized = _serialize_window(window)
        categories = _categorize_usage_window(window, primary_symbol)
        profile = profiles.setdefault(
            path,
            {
                "path": path,
                "is_example": _is_example_path(path),
                "categories": [],
                "windows": [],
            },
        )
        profile["categories"] = _unique_preserving_order([*profile["categories"], *categories])
        profile["windows"].append(serialized)

    ranked_profiles: List[Dict[str, Any]] = []
    for profile in profiles.values():
        profile["windows"] = sorted(
            list(profile.get("windows", []) or []),
            key=lambda item: _line_range_start(str(item.get("line_range") or "")),
        )
        categories = list(profile.get("categories", []) or [])
        coverage_score = len(categories) * int(weights["category_unit"])
        if "usage" in categories:
            coverage_score += int(weights["usage_bonus"])
        if "calls" in categories:
            coverage_score += int(weights["calls_bonus"])
        if "updates" in categories:
            coverage_score += int(weights["updates_bonus"])
        if "definition" in categories:
            coverage_score += int(weights["definition_bonus"])
        coverage_score += _path_relevance_score(str(profile.get("path") or ""), primary_symbol)
        profile["score"] = coverage_score
        ranked_profiles.append(profile)

    ranked_profiles.sort(
        key=lambda item: (
            int(item.get("score") or 0),
            len(list(item.get("categories", []) or [])),
            1 if item.get("is_example") else 0,
            -len(str(item.get("path") or "")),
        ),
        reverse=True,
    )
    return ranked_profiles


def _build_implementation_steps(
    sections: Dict[str, List[Dict[str, Any]]],
    file_profiles: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    profile_by_path = {str(item.get("path") or ""): item for item in file_profiles or []}
    steps: List[Dict[str, Any]] = []
    for title, category, focus in _IMPLEMENTATION_STEP_SPECS:
        rows = list(sections.get(category, []) or [])
        if not rows:
            continue
        primary_path = str(file_profiles[0].get("path") or "") if file_profiles else ""
        if primary_path:
            primary_rows = [row for row in rows if str(row.get("path") or "") == primary_path]
            secondary_rows = [row for row in rows if str(row.get("path") or "") != primary_path]
            rows = primary_rows + secondary_rows
        files = _unique_preserving_order(str(row.get("path") or "") for row in rows if str(row.get("path") or "").strip())
        supporting = []
        for path in files[:3]:
            profile = profile_by_path.get(path, {})
            supporting.append(
                {
                    "path": path,
                    "categories": list(profile.get("categories", []) or []),
                    "line_ranges": [str(window.get("line_range") or "") for window in list(profile.get("windows", []) or [])[:3]],
                }
            )
        steps.append(
            {
                "title": title,
                "category": category,
                "focus": focus,
                "files": files[:3],
                "evidence": rows[:3],
                "supporting_files": supporting,
            }
        )
    return steps


async def collect_usage_guide_bundle(
    *,
    redis,
    code_tools,
    session_id: Optional[str],
    query: str,
    limit: int,
    max_chars: int,
    max_line_span: int,
) -> Dict[str, Any]:
    capped_limit = max(6, min(int(limit or 12), 24))
    trace: List[Dict[str, Any]] = []
    symbol_candidates = extract_symbol_candidates(query)
    indexed_symbol = _resolve_symbol_from_code_index(code_tools, query)
    primary_symbol = indexed_symbol or (symbol_candidates[0] if symbol_candidates else "")

    search_groups: List[List[Dict[str, Any]]] = []

    exact_symbol_matches: List[Dict[str, Any]] = []
    if primary_symbol:
        exact_result = await search_code(
            redis,
            code_tools,
            query_or_regex=_exact_symbol_query(primary_symbol),
            path_filter=None,
            limit=capped_limit,
            session_id=session_id,
        )
        exact_symbol_matches = prioritize_usage_matches(
            list(exact_result.get("matches", []) or []),
            query_text=primary_symbol,
            preferred_symbol=primary_symbol,
        )
        if exact_symbol_matches:
            search_groups.append(exact_symbol_matches)
        trace.append(
            {
                "step": "search_code",
                "query": _exact_symbol_query(primary_symbol),
                "path_filter": "",
                "match_count": len(exact_symbol_matches),
                "reason": exact_result.get("reason"),
            }
        )

    for query_text, path_filter in _build_usage_search_queries(primary_symbol or query, query):
        result = await search_code(
            redis,
            code_tools,
            query_or_regex=query_text,
            path_filter=path_filter,
            limit=capped_limit,
            session_id=session_id,
        )
        rows = prioritize_usage_matches(
            list(result.get("matches", []) or []),
            query_text=query_text,
            preferred_symbol=primary_symbol,
        )
        if primary_symbol:
            symbol_lower = primary_symbol.lower()
            rows = [
                row
                for row in rows
                if (
                    symbol_lower in str(row.get("match") or "").lower()
                    or symbol_lower in str(row.get("path") or "").lower()
                    or _path_relevance_score(str(row.get("path") or ""), primary_symbol) >= 8
                )
            ]
        if rows:
            search_groups.append(rows)
        trace.append(
            {
                "step": "search_code",
                "query": query_text,
                "path_filter": path_filter or "",
                "match_count": len(rows),
                "reason": result.get("reason"),
            }
        )

    ranked_seed_matches = list(exact_symbol_matches or merge_code_matches(search_groups, max_items=capped_limit * 2))
    if primary_symbol:
        ranked_seed_matches.sort(
            key=lambda row: (
                _match_rerank_score(row, symbol=primary_symbol, query_text=query),
                *_usage_match_sort_key(row, primary_symbol, query),
            ),
            reverse=True,
        )

    if ranked_seed_matches and len(ranked_seed_matches) < capped_limit:
        expansion_terms = _extract_search_expansion_terms(
            ranked_seed_matches,
            primary_symbol=primary_symbol,
            query=query,
            limit=4,
        )
        for term in expansion_terms:
            result = await search_code(
                redis,
                code_tools,
                query_or_regex=term,
                path_filter=None,
                limit=capped_limit,
                session_id=session_id,
            )
            rows = prioritize_usage_matches(
                list(result.get("matches", []) or []),
                query_text=term,
                preferred_symbol=primary_symbol,
            )
            if rows:
                search_groups.append(rows)
            trace.append(
                {
                    "step": "search_code_expand",
                    "query": term,
                    "path_filter": "",
                    "match_count": len(rows),
                    "reason": result.get("reason"),
                }
            )

    candidate_paths = _select_candidate_paths(ranked_seed_matches)
    if candidate_paths:
        follow_up_queries = _build_generic_follow_up_queries(primary_symbol or query)
        for candidate_path in candidate_paths:
            for query_text in follow_up_queries:
                result = await search_code(
                    redis,
                    code_tools,
                    query_or_regex=query_text,
                    path_filter=candidate_path,
                    limit=6,
                    session_id=session_id,
                )
                rows = prioritize_usage_matches(
                    list(result.get("matches", []) or []),
                    query_text=f"{primary_symbol} {query_text}",
                    preferred_symbol=primary_symbol,
                )
                if rows:
                    search_groups.append(rows)
                trace.append(
                    {
                        "step": "search_code",
                        "query": query_text,
                        "path_filter": candidate_path,
                        "match_count": len(rows),
                        "reason": result.get("reason"),
                    }
                )

    merged_matches = merge_code_matches(search_groups, max_items=capped_limit * 4)
    ranked_matches = prioritize_usage_matches(merged_matches, query_text=query, preferred_symbol=primary_symbol)
    resolved_symbol = _resolve_symbol_from_matches(ranked_matches, query)
    if resolved_symbol or indexed_symbol:
        primary_symbol = _choose_canonical_symbol(indexed_symbol, resolved_symbol)
    elif not primary_symbol:
        primary_symbol = _infer_primary_symbol(ranked_matches, query)

    focus_example_dir = _select_focus_example_dir(ranked_matches, primary_symbol)
    focus_example_cluster = _select_focus_example_cluster(ranked_matches, primary_symbol)
    focus_cluster_paths = _unique_preserving_order(
        [
            str(row.get("path") or "")
            for row in ranked_matches
            if _path_in_cluster(str(row.get("path") or ""), focus_example_cluster)
        ]
    )[:4]
    if not focus_cluster_paths:
        focus_cluster_paths = _unique_preserving_order(
            [
                str(row.get("path") or "")
                for row in ranked_matches
                if _path_in_dir(str(row.get("path") or ""), focus_example_dir)
            ]
        )[:4]
    if focus_example_dir:
        target_filters = focus_cluster_paths or [focus_example_dir]
        for target_filter in target_filters:
            result = await search_code(
                redis,
                code_tools,
                query_or_regex=primary_symbol or query,
                path_filter=target_filter,
                limit=8,
                session_id=session_id,
            )
            rows = prioritize_usage_matches(
                list(result.get("matches", []) or []),
                query_text=primary_symbol or query,
                preferred_symbol=primary_symbol,
            )
            if rows:
                search_groups.append(rows)
            trace.append(
                {
                    "step": "search_code",
                    "query": primary_symbol or query,
                    "path_filter": target_filter,
                    "match_count": len(rows),
                    "reason": result.get("reason"),
                }
            )
        merged_matches = merge_code_matches(search_groups, max_items=capped_limit * 4)
        ranked_matches = prioritize_usage_matches(merged_matches, query_text=query, preferred_symbol=primary_symbol)
        resolved_symbol = _resolve_symbol_from_matches(ranked_matches, query)
        if resolved_symbol or indexed_symbol:
            primary_symbol = _choose_canonical_symbol(indexed_symbol, resolved_symbol)
        elif not primary_symbol:
            primary_symbol = _infer_primary_symbol(ranked_matches, query)

    if primary_symbol:
        ranked_matches.sort(
            key=lambda row: (
                _match_rerank_score(
                    row,
                    symbol=primary_symbol,
                    query_text=query,
                    focus_example_dir=focus_example_dir,
                    focus_example_cluster=focus_example_cluster,
                ),
                *_usage_match_sort_key(row, primary_symbol, query),
            ),
            reverse=True,
        )

    windows: List[Dict[str, Any]] = []
    seen_windows = set()
    per_path_count: Dict[str, int] = {}

    for row in ranked_matches:
        path = str(row.get("path") or "").strip()
        if not path:
            continue
        if per_path_count.get(path, 0) >= _max_windows_for_path(path):
            continue
        start_line, end_line = parse_line_range(str(row.get("line_range") or "1-1"))
        start_line, end_line = expand_line_window(start_line, end_line, "usage_guide", max_line_span)
        window = read_code_lines(
            code_tools,
            path=path,
            start_line=start_line,
            end_line=end_line,
            max_line_span=max_line_span,
            max_chars=max_chars,
        )
        if not window.get("found"):
            continue
        key = f"{window.get('path')}::{window.get('line_range')}"
        if key in seen_windows:
            continue
        seen_windows.add(key)
        per_path_count[path] = per_path_count.get(path, 0) + 1
        windows.append(window)
        if len(windows) >= 12:
            break

    sections: Dict[str, List[Dict[str, Any]]] = {name: [] for name in _USAGE_SECTION_ORDER}
    example_files: List[str] = []
    focused_windows = [w for w in windows if _path_in_cluster(str(w.get("path") or ""), focus_example_cluster)]
    if not focused_windows:
        focused_windows = [w for w in windows if _path_in_dir(str(w.get("path") or ""), focus_example_dir)]
    secondary_windows = [w for w in windows if w not in focused_windows and _path_in_dir(str(w.get("path") or ""), focus_example_dir)]
    supporting_windows = [w for w in windows if w not in focused_windows and w not in secondary_windows]
    for window_group in (focused_windows, secondary_windows, supporting_windows):
        for window in window_group:
            serialized = _serialize_window(window)
            for category in _categorize_usage_window(window, primary_symbol):
                if len(sections.get(category, [])) < 2:
                    sections.setdefault(category, []).append(serialized)
            path = str(window.get("path") or "")
            if path:
                example_files.append(path)

    if not sections["definition"] and windows:
        sections["definition"].append(_serialize_window(windows[0]))

    file_profiles = _build_file_profiles(windows, primary_symbol)
    primary_path = str(file_profiles[0].get("path") or "") if file_profiles else ""
    if primary_path:
        reprioritized_sections: Dict[str, List[Dict[str, Any]]] = {name: [] for name in _USAGE_SECTION_ORDER}
        for name in _USAGE_SECTION_ORDER:
            rows = list(sections.get(name, []) or [])
            rows.sort(key=lambda row: (1 if str(row.get("path") or "") == primary_path else 0), reverse=True)
            reprioritized_sections[name] = rows[:2]
        sections = reprioritized_sections
    primary_example = dict(file_profiles[0]) if file_profiles else {}
    supporting_files = [str(item.get("path") or "") for item in file_profiles[1:6]]
    implementation_steps = _build_implementation_steps(sections, file_profiles)
    related_types = _extract_related_types(windows, primary_symbol)
    recommended_sequence = [section for section in _USAGE_SECTION_ORDER if sections.get(section)]
    example_files = sorted(
        _unique_preserving_order(example_files),
        key=lambda value: (
            1 if _path_in_cluster(value, focus_example_cluster) else 0,
            1 if _path_in_dir(value, focus_example_dir) else 0,
            _path_relevance_score(value, primary_symbol),
            len(value),
        ),
        reverse=True,
    )[:8]
    coverage = {
        "has_definition": bool(sections["definition"]),
        "has_examples": bool(example_files),
        "has_usage": bool(sections["usage"]),
        "has_calls": bool(sections["calls"]),
        "has_updates": bool(sections["updates"]),
        "has_support": bool(sections["support"]),
    }

    return {
        "bundle": {
            "symbol": primary_symbol,
            "query": query,
            "example_files": example_files,
            "focus_example_dir": focus_example_dir,
            "focus_example_cluster": focus_example_cluster,
            "focus_cluster_paths": focus_cluster_paths,
            "related_types": related_types,
            "recommended_sequence": recommended_sequence,
            "primary_example": primary_example,
            "supporting_files": supporting_files,
            "implementation_steps": implementation_steps,
            "file_profiles": file_profiles[:6],
            "coverage": coverage,
            "sections": sections,
            "matches": [_serialize_match(row) for row in ranked_matches[:12]],
            "trace": trace,
        },
        "matches": ranked_matches,
        "windows": windows,
    }


import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from ..retrieval.service import run_retrieval
from .code_runtime import (
    find_symbol as _find_symbol_impl,
    list_repo_files as _list_repo_files_impl,
    read_code_lines as _read_code_lines_impl,
    search_code as _search_code_impl,
)
from .codebase import extract_symbol_query_candidates
from .build_runtime import run_build
from .doc_runtime import (
    lookup_sources_and_code as _lookup_sources_and_code_impl,
    get_doc_metadata as _get_doc_metadata_impl,
    open_doc_chunks as _open_doc_chunks_impl,
    search_docs as _search_docs_impl,
)
from .svn_runtime import svn_diff, svn_info, svn_status
from .query_strategy import (
    expand_line_window,
    parse_line_range,
    prioritize_usage_matches,
)
from .support import clamp_int


logger = logging.getLogger(__name__)

def read_code_lines(
    code_tools,
    path: str,
    start_line: int,
    end_line: int,
    max_line_span: int = 500,
    max_chars: int = 12000,
) -> Dict[str, Any]:
    return _read_code_lines_impl(
        code_tools,
        path=path,
        start_line=start_line,
        end_line=end_line,
        max_line_span=max_line_span,
        max_chars=max_chars,
    )
async def search_code(
    redis,
    code_tools,
    query_or_regex: str,
    path_filter: Optional[str],
    limit: int,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    return await _search_code_impl(
        redis,
        code_tools,
        query_or_regex=query_or_regex,
        path_filter=path_filter,
        limit=limit,
        session_id=session_id,
        logger=logger,
    )


async def find_symbol(
    redis,
    code_tools,
    symbol: str,
    limit: int,
    session_id: Optional[str] = None,
    language_filter: Optional[str] = None,
    path_filter: Optional[str] = None,
) -> Dict[str, Any]:
    return await _find_symbol_impl(
        redis,
        code_tools,
        symbol=symbol,
        limit=limit,
        session_id=session_id,
        language_filter=language_filter,
        path_filter=path_filter,
    )


async def list_repo_files(
    redis,
    code_tools,
    glob: str,
    limit: int,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    return await _list_repo_files_impl(redis, code_tools, glob, limit, session_id)


async def search_docs(
    redis,
    search_svc,
    embed_model=None,
    query: str = "",
    filters: Optional[Dict[str, Any]] = None,
    top_k: int = 50,
    collection: Optional[str] = None,
    session_id: Optional[str] = None,
    use_reranker: Optional[bool] = None,
) -> Dict[str, Any]:
    if embed_model is None and hasattr(search_svc, "search_svc"):
        state = search_svc
        search_svc = getattr(state, "search_svc", None)
        embed_model = getattr(state, "embed_model", None)
    return await _search_docs_impl(
        redis,
        search_svc,
        embed_model,
        query=query,
        filters=filters,
        top_k=top_k,
        collection=collection,
        session_id=session_id,
        use_reranker=use_reranker,
        run_retrieval_fn=run_retrieval,
    )


async def open_doc_chunks(
    redis,
    search_svc,
    chunk_ids: Iterable[str],
    max_chars: int,
    collection: Optional[str] = None,
    session_id: Optional[str] = None,
    explicit_reference: bool = False,
) -> Dict[str, Any]:
    return await _open_doc_chunks_impl(
        redis,
        search_svc,
        chunk_ids=chunk_ids,
        max_chars=max_chars,
        collection=collection,
        session_id=session_id,
        explicit_reference=explicit_reference,
    )


async def get_doc_metadata(doc_store, doc_id: str) -> Dict[str, Any]:
    return await _get_doc_metadata_impl(doc_store, doc_id)


async def _collect_code_evidence_async(
    *,
    redis,
    session_id: str,
    query: str,
    extra_query_candidates: Optional[Sequence[str]] = None,
    capped_limit: int,
    max_chars: int,
    max_line_span: int,
    response_type: Optional[str],
    search_only: bool,
    code_window_cap: int,
    code_tools=None,
    state=None,
) -> List[Dict[str, Any]]:
    if code_tools is None and state is not None:
        code_tools = getattr(state, "code_tools", None)

    code_windows: List[Dict[str, Any]] = []

    symbol_candidates = extract_symbol_query_candidates(query, max_candidates=4)
    query_candidates: List[str] = []
    for candidate in [query, *symbol_candidates, *(extra_query_candidates or [])]:
        normalized = str(candidate or "").strip()
        if not normalized or normalized in query_candidates:
            continue
        query_candidates.append(normalized)

    merged_matches: List[Dict[str, Any]] = []
    max_query_candidates = max(1, min(8, capped_limit, len(query_candidates)))
    for candidate_query in query_candidates[:max_query_candidates]:
        candidate_result = await search_code(
            redis,
            code_tools,
            query_or_regex=candidate_query,
            path_filter=None,
            limit=capped_limit,
            session_id=session_id,
        )
        merged_matches.extend(candidate_result.get("matches", []) or [])

    deduped_matches: List[Dict[str, Any]] = []
    seen_match_keys: Set[Tuple[str, str]] = set()
    for row in merged_matches:
        key = (str(row.get("path") or "").strip(), str(row.get("line_range") or "").strip())
        if key in seen_match_keys:
            continue
        seen_match_keys.add(key)
        deduped_matches.append(row)
    merged_matches = deduped_matches

    if symbol_candidates:
        merged_matches = prioritize_usage_matches(
            merged_matches,
            query_text=query,
            preferred_symbol=(symbol_candidates[0] if symbol_candidates else ""),
        )
    high_confidence_matches = [
        row for row in merged_matches
        if str(row.get("evidence_type") or "").strip().lower() in {"declaration", "implementation"}
    ]
    if high_confidence_matches:
        merged_matches = [*high_confidence_matches, *[
            row for row in merged_matches
            if row not in high_confidence_matches
        ]]

    if search_only:
        return code_windows

    seen_windows: Set[str] = set()
    per_path_count: Dict[str, int] = {}
    per_path_cap = 3 if symbol_candidates else 2
    max_windows = min(code_window_cap, max(capped_limit // 2, 6))

    def _window_overlap_ratio(left_range: str, right_range: str) -> float:
        left_start, left_end = parse_line_range(str(left_range or "1-1"))
        right_start, right_end = parse_line_range(str(right_range or "1-1"))
        left_span = max(1, left_end - left_start + 1)
        right_span = max(1, right_end - right_start + 1)
        overlap_start = max(left_start, right_start)
        overlap_end = min(left_end, right_end)
        if overlap_end < overlap_start:
            return 0.0
        overlap_span = overlap_end - overlap_start + 1
        return overlap_span / max(1, min(left_span, right_span))

    for match in merged_matches:
        if len(code_windows) >= max_windows:
            break
        path = str(match.get("path") or "").strip()
        if not path:
            continue
        if per_path_count.get(path, 0) >= per_path_cap:
            continue

        start_line, end_line = parse_line_range(str(match.get("line_range") or "1-1"))
        start_line, end_line = expand_line_window(start_line, end_line, response_type, max_line_span)
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
        window_key = f"{window.get('path')}::{window.get('line_range')}"
        if window_key in seen_windows:
            continue
        if any(
            str(existing.get("path") or "") == str(window.get("path") or "")
            and _window_overlap_ratio(
                str(existing.get("line_range") or ""),
                str(window.get("line_range") or ""),
            ) >= 0.6
            for existing in code_windows
        ):
            continue
        seen_windows.add(window_key)
        per_path_count[path] = per_path_count.get(path, 0) + 1
        window["evidence_type"] = str(match.get("evidence_type") or "")
        if match.get("match_kind"):
            window["match_kind"] = str(match.get("match_kind") or "")
        code_windows.append(window)

    return code_windows


async def lookup_sources_and_code(
    redis,
    search_svc,
    embed_model,
    code_tools,
    session_id: str,
    user_id: Optional[str],
    query: str,
    filters: Optional[Dict[str, Any]],
    top_k: int,
    limit: int,
    max_chars: int,
    max_line_span: int,
    response_type: str = "general",
    search_only: bool = False,
    collection: Optional[str] = None,
) -> Dict[str, Any]:
    return await _lookup_sources_and_code_impl(
        redis=redis,
        search_svc=search_svc,
        embed_model=embed_model,
        code_tools=code_tools,
        session_id=session_id,
        user_id=user_id,
        query=query,
        filters=filters,
        top_k=top_k,
        limit=limit,
        max_chars=max_chars,
        max_line_span=max_line_span,
        response_type=response_type,
        search_only=search_only,
        collection=collection,
        collect_code_evidence_async=_collect_code_evidence_async,
    )



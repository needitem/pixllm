import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from ..chat.retrieval.service import run_retrieval
from .code_runtime import (
    find_symbol as _find_symbol_impl,
    list_repo_files as _list_repo_files_impl,
    read_code_lines as _read_code_lines_impl,
    search_code as _search_code_impl,
)
from .codebase import extract_symbol_query_candidates
from .build_runtime import run_build
from .doc_runtime import (
    collect_evidence_bundle as _collect_evidence_bundle_impl,
    get_doc_metadata as _get_doc_metadata_impl,
    open_doc_chunks as _open_doc_chunks_impl,
    search_docs as _search_docs_impl,
)
from .svn_runtime import svn_diff, svn_info, svn_status
from .query_strategy import (
    expand_line_window,
    parse_line_range,
    prioritize_usage_matches,
    route_collect_mode,
)
from .support import (
    clamp_int,
    decode_file as _decode_file,
    is_subpath as _is_subpath,
)


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


def _collect_code_evidence(
    *,
    state,
    session_id: str,
    query: str,
    capped_limit: int,
    max_chars: int,
    max_line_span: int,
    response_type: Optional[str],
    search_only: bool,
    code_window_cap: int,
    # redis passed separately since this is sync-called wrapper; actual search_code is async
    # caller must have already done search_code; this branch is for sync fallback path
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Sync shell — actual code search is done via async search_code in callers."""
    raise NotImplementedError("Use _collect_code_evidence_async instead")


async def _collect_code_evidence_async(
    *,
    redis,
    session_id: str,
    query: str,
    capped_limit: int,
    max_chars: int,
    max_line_span: int,
    response_type: Optional[str],
    search_only: bool,
    code_window_cap: int,
    code_tools=None,
    state=None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    if code_tools is None and state is not None:
        code_tools = getattr(state, "code_tools", None)

    trace_steps: List[Dict[str, Any]] = []
    code_windows: List[Dict[str, Any]] = []
    code_search_result: Dict[str, Any] = {"matches": [], "limit": capped_limit}

    code_search_result = await search_code(
        redis,
        code_tools,
        query_or_regex=query,
        path_filter=None,
        limit=capped_limit,
        session_id=session_id,
    )
    trace_steps.append(
        {
            "step": "search_code",
            "status": "ok" if not code_search_result.get("reason") else "skipped",
            "result_count": len(code_search_result.get("matches", [])),
            "reason": code_search_result.get("reason"),
        }
    )

    merged_matches = list(code_search_result.get("matches", []))

    if str(response_type or "").strip().lower() in {"usage_guide", "api_lookup"}:
        symbol_candidates = extract_symbol_query_candidates(query, max_candidates=1)
        merged_matches = prioritize_usage_matches(
            merged_matches,
            query_text=query,
            preferred_symbol=(symbol_candidates[0] if symbol_candidates else ""),
        )
    code_search_result["matches"] = merged_matches
    code_search_result["truncated"] = len(merged_matches) > capped_limit

    if search_only:
        trace_steps.append({"step": "read_code_windows", "status": "skipped", "count": 0, "reason": "search_only"})
        return code_search_result, code_windows, trace_steps

    seen_windows: Set[str] = set()
    per_path_count: Dict[str, int] = {}
    per_path_cap = 3 if str(response_type or "").strip().lower() in {"usage_guide", "api_lookup"} else 2
    max_windows = min(code_window_cap, max(capped_limit // 2, 6))

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
        seen_windows.add(window_key)
        per_path_count[path] = per_path_count.get(path, 0) + 1
        code_windows.append(window)

    trace_steps.append({"step": "read_code_windows", "status": "ok", "count": len(code_windows), "max_windows": max_windows})
    return code_search_result, code_windows, trace_steps


async def collect_evidence_bundle(
    redis,
    search_svc,
    embed_model,
    code_tools,
    doc_store,
    session_id: str,
    user_id: Optional[str],
    query: str,
    filters: Optional[Dict[str, Any]],
    mode: str,
    top_k: int,
    limit: int,
    max_chars: int,
    max_line_span: int,
    response_type: str = "general",
    search_only: bool = False,
    collection: Optional[str] = None,
) -> Dict[str, Any]:
    return await _collect_evidence_bundle_impl(
        redis=redis,
        search_svc=search_svc,
        embed_model=embed_model,
        code_tools=code_tools,
        doc_store=doc_store,
        session_id=session_id,
        user_id=user_id,
        query=query,
        filters=filters,
        mode=mode,
        top_k=top_k,
        limit=limit,
        max_chars=max_chars,
        max_line_span=max_line_span,
        response_type=response_type,
        search_only=search_only,
        collection=collection,
        route_collect_mode=route_collect_mode,
        collect_code_evidence_async=_collect_code_evidence_async,
    )



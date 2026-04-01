import asyncio
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ... import config
from ..retrieval.service import run_retrieval
from ...core.policy import SecurityPolicy
from .access import register_doc_search, resolve_tool_user_context
from .support import build_citations, clamp_int, normalize_doc_item, qdrant_point_id


async def search_docs(
    redis,
    search_svc,
    embed_model,
    query: str,
    filters: Optional[Dict[str, Any]],
    top_k: int,
    collection: Optional[str] = None,
    session_id: Optional[str] = None,
    use_reranker: Optional[bool] = None,
    run_retrieval_fn=run_retrieval,
) -> Dict[str, Any]:
    gate = await SecurityPolicy.check_search_gate(redis, session_id)
    if not gate["allow"]:
        return {"query": query, "top_k": clamp_int(top_k, 1, 50), "results": [], "query_time_ms": 0.0, "reason": gate["reason"]}

    capped_top_k = clamp_int(top_k, 1, 50)
    req = SimpleNamespace(
        message=query,
        query=query,
        top_k=capped_top_k,
        collection=collection or config.RAG_DEFAULT_COLLECTION,
        filters=filters or {},
        language_filter=(filters or {}).get("language") if isinstance(filters, dict) else None,
        module_filter=(filters or {}).get("module") if isinstance(filters, dict) else None,
        use_reranker=bool(use_reranker) if use_reranker is not None else False,
        evidence_mode=None,
    )
    results, _, elapsed_ms = run_retrieval_fn(search_svc, req, embed_model)
    docs = [normalize_doc_item(row) for row in results]
    await register_doc_search(redis, session_id, docs)
    return {"query": query, "top_k": capped_top_k, "results": docs, "query_time_ms": elapsed_ms}


async def open_doc_chunks(
    redis,
    search_svc,
    chunk_ids: Iterable[str],
    max_chars: int,
    collection: Optional[str] = None,
    session_id: Optional[str] = None,
    explicit_reference: bool = False,
) -> Dict[str, Any]:
    capped_chars = clamp_int(max_chars, 200, 12000)
    cleaned_ids = [str(x).strip() for x in chunk_ids if str(x).strip()]
    access = await SecurityPolicy.check_doc_chunk_access(redis, session_id, cleaned_ids, explicit_reference)
    if not access["allow"]:
        return {"chunks": [], "missing_chunk_ids": cleaned_ids, "unknown_chunk_ids": access.get("unknown_chunk_ids", []), "max_chars": capped_chars, "used_chars": 0, "reason": access["reason"]}

    qdrant_ids = [qdrant_point_id(x) for x in cleaned_ids]
    if not cleaned_ids:
        return {"chunks": [], "missing_chunk_ids": [], "unknown_chunk_ids": [], "max_chars": capped_chars, "used_chars": 0}

    try:
        points = search_svc.qdrant.retrieve(
            collection_name=collection or config.RAG_DEFAULT_COLLECTION,
            ids=qdrant_ids,
            with_payload=True,
        )
    except Exception:
        points = []

    chunks = []
    found_ids = set()
    used_chars = 0
    for point in points:
        point_id = str(getattr(point, "id", ""))
        found_ids.add(point_id)
        payload = getattr(point, "payload", {}) or {}
        text = payload.get("text", "")
        if not text:
            continue
        remaining = capped_chars - used_chars
        if remaining <= 0:
            break
        clipped = text[:remaining]
        used_chars += len(clipped)
        chunks.append(
            {
                "chunk_id": point_id,
                "doc_id": payload.get("document_id"),
                "source_url": payload.get("source_url") or payload.get("source_file") or payload.get("file_path"),
                "heading_path": payload.get("heading_path"),
                "updated_at": payload.get("updated_at"),
                "paragraph_range": payload.get("paragraph_range") or (
                    f"chunk:{payload.get('chunk_index')}" if payload.get("chunk_index") is not None else None
                ),
                "text": clipped,
                "truncated": len(clipped) < len(text),
            }
        )

    missing = [cid for cid in cleaned_ids if cid not in found_ids]
    return {"chunks": chunks, "missing_chunk_ids": missing, "unknown_chunk_ids": access.get("unknown_chunk_ids", []), "max_chars": capped_chars, "used_chars": used_chars}


async def get_doc_metadata(doc_store, doc_id: str) -> Dict[str, Any]:
    document = await doc_store.get_document(doc_id)
    if not document:
        return {"doc_id": doc_id, "found": False}
    current_revision = await doc_store.get_current_revision(doc_id)
    revisions = await doc_store.list_revisions(doc_id, limit=10)
    return {"doc_id": doc_id, "found": True, "document": document, "current_revision": current_revision, "recent_revisions": revisions}


async def collect_doc_evidence(
    *,
    redis,
    search_svc,
    embed_model,
    doc_store,
    session_id: str,
    query: str,
    filters: Optional[Dict[str, Any]],
    capped_top_k: int,
    doc_open_limit: int,
    max_chars: int,
    capped_limit: int,
    search_only: bool,
    active_collection: str,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    trace_steps: List[Dict[str, Any]] = []
    doc_chunks: List[Dict[str, Any]] = []

    doc_search = await search_docs(
        redis,
        search_svc,
        embed_model,
        query=query,
        filters=filters,
        top_k=capped_top_k,
        collection=active_collection,
        session_id=session_id,
    )
    trace_steps.append({"step": "search_docs", "status": "ok" if not doc_search.get("reason") else "skipped", "result_count": len(doc_search.get("results", [])), "reason": doc_search.get("reason")})

    doc_rows = list(doc_search.get("results", []) or [])
    if search_only:
        trace_steps.append({"step": "open_doc_chunks", "status": "skipped", "opened_count": 0, "reason": "search_only"})
    else:
        chunk_ids = [r.get("chunk_id") for r in doc_rows if r.get("chunk_id")][:doc_open_limit]
        opened = await open_doc_chunks(
            redis,
            search_svc,
            chunk_ids=chunk_ids,
            max_chars=max_chars,
            collection=active_collection,
            session_id=session_id,
            explicit_reference=False,
        )
        doc_chunks = opened.get("chunks", [])
        trace_steps.append({"step": "open_doc_chunks", "status": "ok" if not opened.get("reason") else "skipped", "opened_count": len(doc_chunks), "reason": opened.get("reason")})

    return doc_search, doc_chunks, trace_steps


async def collect_evidence_bundle(
    *,
    redis,
    search_svc=None,
    embed_model=None,
    code_tools=None,
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
    response_type: str,
    search_only: bool,
    collection: Optional[str],
    route_collect_mode,
    collect_code_evidence_async,
    state=None,
) -> Dict[str, Any]:
    if state is not None:
        search_svc = search_svc if search_svc is not None else getattr(state, "search_svc", None)
        embed_model = embed_model if embed_model is not None else getattr(state, "embed_model", None)
        code_tools = code_tools if code_tools is not None else getattr(state, "code_tools", None)

    trace: List[Dict[str, Any]] = []
    context = await resolve_tool_user_context(redis, session_id=session_id, user_id=user_id)
    trace.append({"step": "resolve_user_context", "status": "ok", "session_id": context.get("session_id")})

    resolved_mode = route_collect_mode(response_type=response_type, mode=mode)
    trace.append({"step": "route_intent", "status": "ok", "requested_mode": mode, "resolved_mode": resolved_mode})

    capped_top_k = clamp_int(top_k, 1, 50)
    capped_limit = clamp_int(limit, 1, 50)
    doc_open_limit = min(capped_limit, clamp_int(config.CHAT_TOOL_DOC_OPEN_LIMIT, 1, 50))
    code_window_cap = clamp_int(config.CHAT_TOOL_CODE_MAX_WINDOWS, 4, 24)
    active_collection = collection or config.RAG_DEFAULT_COLLECTION

    doc_search: Dict[str, Any] = {"results": [], "top_k": capped_top_k}
    code_search_result: Dict[str, Any] = {"matches": [], "limit": capped_limit}
    doc_chunks: List[Dict[str, Any]] = []
    code_windows: List[Dict[str, Any]] = []

    if resolved_mode == "docs":
        doc_search, doc_chunks, doc_trace = await collect_doc_evidence(
            redis=redis,
            search_svc=search_svc,
            embed_model=embed_model,
            doc_store=doc_store,
            session_id=session_id,
            query=query,
            filters=filters,
            capped_top_k=capped_top_k,
            doc_open_limit=doc_open_limit,
            max_chars=max_chars,
            capped_limit=capped_limit,
            search_only=search_only,
            active_collection=active_collection,
        )
        trace.extend(doc_trace)

    if resolved_mode == "code":
        code_search_result, code_windows, code_trace = await collect_code_evidence_async(
            redis=redis,
            code_tools=code_tools,
            session_id=session_id,
            query=query,
            capped_limit=capped_limit,
            max_chars=max_chars,
            max_line_span=max_line_span,
            response_type=response_type,
            search_only=search_only,
            code_window_cap=code_window_cap,
        )
        trace.extend(code_trace)

    if resolved_mode == "hybrid":
        (doc_search, doc_chunks, doc_trace), (code_search_result, code_windows, code_trace) = await asyncio.gather(
            collect_doc_evidence(
                redis=redis,
                search_svc=search_svc,
                embed_model=embed_model,
                doc_store=doc_store,
                session_id=session_id,
                query=query,
                filters=filters,
                capped_top_k=capped_top_k,
                doc_open_limit=doc_open_limit,
                max_chars=max_chars,
                capped_limit=capped_limit,
                search_only=search_only,
                active_collection=active_collection,
            ),
            collect_code_evidence_async(
                redis=redis,
                code_tools=code_tools,
                session_id=session_id,
                query=query,
                capped_limit=capped_limit,
                max_chars=max_chars,
                max_line_span=max_line_span,
                response_type=response_type,
                search_only=search_only,
                code_window_cap=code_window_cap,
            ),
        )
        trace.extend(doc_trace)
        trace.extend(code_trace)

    return {
        "session_id": session_id,
        "user_id": user_id or "anonymous",
        "query": query,
        "requested_mode": mode,
        "resolved_mode": resolved_mode,
        "evidence": {"docs": {"search": doc_search, "chunks": doc_chunks}, "code": {"search": code_search_result, "windows": code_windows}},
        "citations": build_citations(doc_chunks, code_windows),
        "trace": trace,
        "policy": {
            "flow": "context->search->open/read",
            "caps": {"top_k_max": 50, "limit_max": 50, "max_chars_max": 12000, "max_line_span_max": 500},
            "collection": active_collection,
        },
    }

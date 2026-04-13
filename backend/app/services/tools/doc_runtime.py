import re
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ... import config
from ..retrieval.service import run_retrieval
from ...core.policy import SecurityPolicy
from .access import register_code_search, register_doc_search, resolve_tool_user_context
from .code_runtime import read_code_lines
from .query_strategy import expand_line_window, parse_line_range
from .support import build_citations, clamp_int, dedupe_doc_items, normalize_doc_item, qdrant_point_id
from .wiki_runtime import search_wiki

_WIKI_SOURCE_REF_RE = re.compile(r"\b(Source/[^`:\s]+):(\d+)(?:-(\d+))?\b")


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


async def collect_sources(
    *,
    redis,
    search_svc,
    embed_model,
    session_id: str,
    query: str,
    filters: Optional[Dict[str, Any]],
    top_k: int,
    doc_open_limit: int,
    max_chars: int,
    active_collection: str,
    search_only: bool,
) -> List[Dict[str, Any]]:
    wiki_rows = list(search_wiki(query=query, top_k=min(top_k, doc_open_limit), max_chars=max_chars).get("results", []) or [])
    doc_rows = list(
        (
            await search_docs(
                redis,
                search_svc,
                embed_model,
                query=query,
                filters=filters,
                top_k=top_k,
                collection=active_collection,
                session_id=session_id,
            )
        ).get("results", [])
        or []
    )
    if search_only:
        return merge_doc_sources([wiki_rows, doc_rows])[:doc_open_limit]

    remaining = max(0, doc_open_limit - len(wiki_rows[:doc_open_limit]))
    chunk_ids = [
        row.get("chunk_id")
        for row in doc_rows
        if row.get("chunk_id") and not str(row.get("chunk_id") or "").startswith("wiki:")
    ][:remaining]
    opened = await open_doc_chunks(
        redis,
        search_svc,
        chunk_ids=chunk_ids,
        max_chars=max_chars,
        collection=active_collection,
        session_id=session_id,
        explicit_reference=False,
    )
    return merge_doc_sources([wiki_rows, opened.get("chunks", []), doc_rows])[:doc_open_limit]


def is_docs_only_request(*, response_type: str, mode: str) -> bool:
    requested = str(mode or "auto").strip().lower()
    return requested == "docs" or (requested not in {"code", "hybrid"} and str(response_type or "").strip().lower() == "doc_lookup")


def extract_wiki_source_anchors(doc_chunks: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    anchors: List[Dict[str, Any]] = []
    seen = set()
    for chunk in doc_chunks or []:
        text = str(chunk.get("text") or "")
        if not text:
            continue
        for raw_line in text.splitlines():
            line = str(raw_line or "").strip()
            if not line:
                continue
            lowered = line.lower()
            evidence_type = "reference"
            if "declaration:" in lowered or "type declaration:" in lowered:
                evidence_type = "declaration"
            elif "implementation:" in lowered:
                evidence_type = "implementation"
            for match in _WIKI_SOURCE_REF_RE.finditer(line):
                path = str(match.group(1) or "").strip().replace("\\", "/")
                start_line = max(1, int(match.group(2) or 1))
                end_line = max(start_line, int(match.group(3) or match.group(2) or start_line))
                key = (path, start_line, end_line, evidence_type)
                if key in seen:
                    continue
                seen.add(key)
                anchors.append(
                    {
                        "path": path,
                        "line_range": f"{start_line}-{end_line}",
                        "evidence_type": evidence_type,
                        "source_url": chunk.get("source_url"),
                        "heading_path": chunk.get("heading_path"),
                    }
                )
    return anchors


def merge_code_windows(groups: Sequence[Sequence[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    seen = set()
    for group in groups or []:
        for row in group or []:
            key = (str(row.get("path") or "").strip(), str(row.get("line_range") or "").strip())
            if not key[0] or key in seen:
                continue
            seen.add(key)
            merged.append(row)
    return merged


def merge_doc_sources(groups: Sequence[Sequence[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    for group in groups or []:
        merged.extend(list(group or []))
    return dedupe_doc_items(merged)


async def collect_wiki_anchor_code_windows(
    *,
    redis,
    session_id: str,
    code_tools,
    doc_chunks: Sequence[Dict[str, Any]],
    max_chars: int,
    max_line_span: int,
    response_type: str,
    code_window_cap: int,
    search_only: bool,
) -> List[Dict[str, Any]]:
    anchors = extract_wiki_source_anchors(doc_chunks)
    if not anchors or code_tools is None:
        return []

    if search_only:
        await register_code_search(redis, session_id, anchors)
        return []

    windows: List[Dict[str, Any]] = []
    seen = set()
    per_path_count: Dict[str, int] = {}
    per_path_cap = 2
    max_windows = min(clamp_int(code_window_cap, 1, 24), max(4, len(anchors)))

    for anchor in anchors:
        if len(windows) >= max_windows:
            break
        path = str(anchor.get("path") or "").strip()
        if not path or per_path_count.get(path, 0) >= per_path_cap:
            continue
        start_line, end_line = parse_line_range(str(anchor.get("line_range") or "1-1"))
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
        key = (str(window.get("path") or "").strip(), str(window.get("line_range") or "").strip())
        if key in seen:
            continue
        seen.add(key)
        per_path_count[path] = per_path_count.get(path, 0) + 1
        window["evidence_type"] = str(anchor.get("evidence_type") or "reference")
        if anchor.get("source_url"):
            window["source_url"] = anchor.get("source_url")
        if anchor.get("heading_path"):
            window["heading_path"] = anchor.get("heading_path")
        windows.append(window)

    if windows:
        await register_code_search(redis, session_id, windows)
    return windows


async def lookup_sources_and_code(
    *,
    redis,
    search_svc=None,
    embed_model=None,
    code_tools=None,
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
    collect_code_evidence_async,
    state=None,
) -> Dict[str, Any]:
    if state is not None:
        search_svc = search_svc if search_svc is not None else getattr(state, "search_svc", None)
        embed_model = embed_model if embed_model is not None else getattr(state, "embed_model", None)
        code_tools = code_tools if code_tools is not None else getattr(state, "code_tools", None)

    await resolve_tool_user_context(redis, session_id=session_id, user_id=user_id)
    docs_only = is_docs_only_request(response_type=response_type, mode=mode)

    capped_top_k = clamp_int(top_k, 1, 50)
    capped_limit = clamp_int(limit, 1, 50)
    doc_open_limit = min(capped_limit, clamp_int(config.CHAT_TOOL_DOC_OPEN_LIMIT, 1, 50))
    code_window_cap = clamp_int(config.CHAT_TOOL_CODE_MAX_WINDOWS, 4, 24)
    active_collection = collection or config.RAG_DEFAULT_COLLECTION

    sources = await collect_sources(
        redis=redis,
        search_svc=search_svc,
        embed_model=embed_model,
        session_id=session_id,
        query=query,
        filters=filters,
        top_k=capped_top_k,
        doc_open_limit=doc_open_limit,
        max_chars=max_chars,
        active_collection=active_collection,
        search_only=search_only,
    )
    wiki_code_windows = await collect_wiki_anchor_code_windows(
        redis=redis,
        session_id=session_id,
        code_tools=code_tools,
        doc_chunks=sources,
        max_chars=max_chars,
        max_line_span=max_line_span,
        response_type=response_type,
        code_window_cap=code_window_cap,
        search_only=search_only,
    )
    code_windows = wiki_code_windows

    if not docs_only:
        _, searched_code_windows, _ = await collect_code_evidence_async(
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
        code_windows = merge_code_windows([wiki_code_windows, searched_code_windows])

    return {
        "query": query,
        "sources": sources,
        "code_windows": code_windows,
        "citations": build_citations(sources, code_windows),
    }

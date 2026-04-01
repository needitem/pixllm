from fastapi import APIRouter, Depends

from ..schemas.search import SearchRequest
from ..envelopes import ok
from ..deps import get_search_svc, get_embed_model, get_code_tools
from ..services.retrieval.service import run_retrieval, run_code_tool_retrieval


router = APIRouter()


@router.post("/search")
async def search(
    request: SearchRequest,
    search_svc=Depends(get_search_svc),
    embed_model=Depends(get_embed_model),
    code_tools=Depends(get_code_tools),
):
    page = max(1, int(getattr(request, "page", 1) or 1))
    per_page = max(1, int(getattr(request, "per_page", 10) or 10))
    raw_top_k = max(1, int(getattr(request, "top_k", 10) or 10))
    effective_top_k = max(raw_top_k, page * per_page)
    request.top_k = effective_top_k

    if not request.query.strip():
        return ok({"results": [], "graph_results": [], "query_time_ms": 0, "page": page, "per_page": per_page, "total": 0, "total_pages": 0})
    mode = (request.source_mode or "docs").strip().lower()
    docs_results = []
    code_results = []
    graph = []
    query_ms = 0.0

    if mode == "docs":
        docs_results, graph, docs_ms = run_retrieval(search_svc, request, embed_model)
        query_ms += docs_ms
    if mode == "code" and code_tools is not None:
        code_results, code_ms = run_code_tool_retrieval(code_tools, request)
        query_ms += code_ms

    if mode == "docs":
        results = docs_results
    else:
        results = code_results
        graph = []

    total = len(results)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0
    start = (page - 1) * per_page
    end = start + per_page
    page_results = results[start:end]

    payloads = []
    for idx, r in enumerate(page_results, start=start + 1):
        md = r.get("payload", {})
        payloads.append({
            "file_path": md.get("file_path"),
            "module": md.get("module"),
            "language": md.get("language"),
            "page_number": md.get("page_number"),
            "total_pages": md.get("total_pages"),
            "line_start": md.get("line_start"),
            "line_end": md.get("line_end"),
            "snippet": (md.get("text", "")[:200] + "...") if md.get("text") else "",
            "rank": r.get("rank") or idx,
        })
    return ok({
        "results": payloads,
        "graph_results": graph,
        "query_time_ms": query_ms,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
    })

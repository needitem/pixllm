from fastapi import APIRouter
from starlette.concurrency import run_in_threadpool

from ..envelopes import err, ok
from ..schemas.source import (
    SourceAnswerRequest,
    SourceGlobRequest,
    SourceGrepRequest,
    SourceListRequest,
    SourceReadRequest,
    SourceSearchRequest,
    SourceSymbolSearchRequest,
    SourceTypeGraphRequest,
    SourceUsagesRequest,
)
from ..services.source import agent as source_agent
from ..services.source import service as source_service


router = APIRouter(prefix="/source")


@router.get("")
async def source_overview_get():
    return ok(source_service.get_context())


@router.post("/context")
async def source_overview():
    return ok(source_service.get_context())


@router.post("/index/rebuild")
async def rebuild_source_index():
    return ok(source_service.rebuild_index())


@router.post("/ls")
async def list_source(payload: SourceListRequest):
    return ok(
        source_service.list_source(
            payload.path or "",
            depth=payload.depth,
            limit=payload.limit,
        )
    )


@router.post("/glob")
async def glob_source(payload: SourceGlobRequest):
    return ok(source_service.glob_source(payload.pattern, limit=payload.limit))


@router.post("/grep")
async def grep_source(payload: SourceGrepRequest):
    return ok(
        source_service.grep_source(
            payload.pattern,
            path_glob=payload.path_glob or "",
            regex=payload.regex,
            case_sensitive=payload.case_sensitive,
            limit=payload.limit,
            context=payload.context,
        )
    )


@router.post("/symbols")
async def search_source_symbols(payload: SourceSymbolSearchRequest):
    return ok(source_service.symbol_search(payload.query, limit=payload.limit))


@router.post("/type-graph")
async def source_type_graph(payload: SourceTypeGraphRequest):
    return ok(source_service.type_graph(payload.query, limit=payload.limit))


@router.post("/usages")
async def source_usages(payload: SourceUsagesRequest):
    return ok(source_service.source_usages(payload.query, limit=payload.limit))


@router.post("/search")
async def search_source(payload: SourceSearchRequest):
    return ok(
        source_service.search_source(
            query=payload.query or "",
            limit=payload.limit,
            include_content=payload.include_content,
            kind=payload.kind,
        )
    )


@router.post("/answer")
async def answer_source(payload: SourceAnswerRequest):
    return ok(
        await run_in_threadpool(
            source_agent.answer_source_question,
            prompt=payload.prompt,
            model=payload.model,
            llm_base_url=payload.llm_base_url,
            session_id=payload.session_id,
            max_tokens=payload.max_tokens,
            max_llm_calls=payload.max_llm_calls,
            enable_thinking=payload.enable_thinking,
        )
    )


@router.post("/read")
async def read_source(payload: SourceReadRequest):
    item = source_service.read_source(
        payload.path,
        start_line=payload.start_line,
        end_line=payload.end_line,
    )
    if not item:
        return err("NOT_FOUND", "source path not found")
    return ok(item)

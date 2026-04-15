from fastapi import APIRouter, Depends

from ..deps import get_redis
from ..envelopes import err, ok
from ..schemas.wiki import (
    WikiContextRequest,
    WikiLintRequest,
    WikiReadPageRequest,
    WikiRebuildIndexRequest,
    WikiSearchRequest,
    WikiWritebackRequest,
    WikiWritePageRequest,
)
from ..services.wiki.service import WikiService


router = APIRouter(prefix="/wiki")


@router.get("")
async def list_wikis(redis=Depends(get_redis)):
    svc = WikiService(redis)
    return ok({"items": await svc.list_wikis()})


@router.post("/context")
async def wiki_context(payload: WikiContextRequest, redis=Depends(get_redis)):
    svc = WikiService(redis)
    return ok(await svc.get_context(payload.wiki_id))


@router.post("/index/rebuild")
async def rebuild_wiki_index(payload: WikiRebuildIndexRequest, redis=Depends(get_redis)):
    svc = WikiService(redis)
    return ok(await svc.rebuild_index(payload.wiki_id))


@router.post("/search")
async def search_wiki(payload: WikiSearchRequest, redis=Depends(get_redis)):
    svc = WikiService(redis)
    return ok(
        await svc.search_pages(
            payload.wiki_id,
            query=payload.query or "",
            limit=payload.limit,
            include_content=payload.include_content,
            kind=payload.kind,
        )
    )


@router.post("/page/read")
async def read_wiki_page(payload: WikiReadPageRequest, redis=Depends(get_redis)):
    svc = WikiService(redis)
    page = await svc.get_page(payload.wiki_id, payload.path)
    if not page:
        return err("NOT_FOUND", "wiki page not found")
    return ok(page)


@router.put("/page")
async def write_wiki_page(payload: WikiWritePageRequest, redis=Depends(get_redis)):
    svc = WikiService(redis)
    page = await svc.write_page(
        payload.wiki_id,
        payload.path,
        payload.content,
        title=payload.title,
        kind=payload.kind,
    )
    return ok(page)


@router.post("/lint")
async def lint_wiki(payload: WikiLintRequest, redis=Depends(get_redis)):
    svc = WikiService(redis)
    return ok(await svc.lint_wiki(payload.wiki_id, repair=payload.repair))


@router.post("/writeback")
async def writeback_wiki_page(payload: WikiWritebackRequest, redis=Depends(get_redis)):
    svc = WikiService(redis)
    return ok(
        await svc.write_query_page(
            payload.wiki_id,
            query=payload.query,
            answer=payload.answer,
            title=payload.title or "",
            category=payload.category,
            page_path=payload.path or "",
            source_paths=payload.source_paths,
        )
    )

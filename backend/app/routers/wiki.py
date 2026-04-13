from fastapi import APIRouter, Depends

from ..deps import get_redis
from ..envelopes import err, ok
from ..schemas.wiki import (
    WikiAppendLogRequest,
    WikiBootstrapRequest,
    WikiContextRequest,
    WikiReadPageRequest,
    WikiSearchRequest,
    WikiWritePageRequest,
)
from ..services.wiki.service import WikiService


router = APIRouter(prefix="/wiki")


@router.get("")
async def list_wikis(redis=Depends(get_redis)):
    svc = WikiService(redis)
    return ok({"items": await svc.list_wikis()})


@router.post("/bootstrap")
async def bootstrap_wiki(payload: WikiBootstrapRequest, redis=Depends(get_redis)):
    svc = WikiService(redis)
    data = await svc.bootstrap_wiki(
        payload.wiki_id,
        name=payload.name,
        description=payload.description,
        overwrite=payload.overwrite,
        user_id=payload.user_id,
    )
    return ok(data)


@router.post("/context")
async def wiki_context(payload: WikiContextRequest, redis=Depends(get_redis)):
    svc = WikiService(redis)
    return ok(await svc.get_context(payload.wiki_id))


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
    page = await svc.upsert_page(
        payload.wiki_id,
        payload.path,
        payload.content,
        title=payload.title,
        kind=payload.kind,
        user_id=payload.user_id,
    )
    return ok(page)


@router.post("/log/append")
async def append_wiki_log(payload: WikiAppendLogRequest, redis=Depends(get_redis)):
    svc = WikiService(redis)
    page = await svc.append_log(
        payload.wiki_id,
        title=payload.title,
        body_lines=payload.body_lines,
        kind=payload.kind,
        user_id=payload.user_id,
    )
    return ok(page)

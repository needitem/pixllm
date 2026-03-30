from fastapi import APIRouter, Depends

from ..envelopes import ok, err
from ..deps import get_redis
from ..schemas.knowledge import KnowledgeCreate, KnowledgeUpdate
from ..services.knowledge.service import KnowledgeService


router = APIRouter()


@router.get("/knowledge")
async def list_knowledge(page: int = 1, per_page: int = 20, redis=Depends(get_redis)):
    svc = KnowledgeService(redis)
    data = await svc.list(page, per_page)
    return ok(data)


@router.get("/knowledge/{kb_id}")
async def get_knowledge(kb_id: str, redis=Depends(get_redis)):
    svc = KnowledgeService(redis)
    data = await svc.get(kb_id)
    if not data:
        return err("NOT_FOUND", "knowledge not found")
    return ok(data)


@router.post("/knowledge")
async def create_knowledge(payload: KnowledgeCreate, redis=Depends(get_redis)):
    svc = KnowledgeService(redis)
    data = await svc.create({
        "name": payload.name,
        "description": payload.description,
        "files": [{"file_id": fid} for fid in payload.file_ids],
    })
    return ok(data)


@router.put("/knowledge/{kb_id}")
async def update_knowledge(kb_id: str, payload: KnowledgeUpdate, redis=Depends(get_redis)):
    svc = KnowledgeService(redis)
    data = await svc.update(kb_id, {
        "name": payload.name,
        "description": payload.description,
        "files": [{"file_id": fid} for fid in (payload.file_ids or [])] if payload.file_ids is not None else None,
    })
    if not data:
        return err("NOT_FOUND", "knowledge not found")
    return ok(data)


@router.delete("/knowledge/{kb_id}")
async def delete_knowledge(kb_id: str, redis=Depends(get_redis)):
    svc = KnowledgeService(redis)
    await svc.delete(kb_id)
    return ok({"deleted": kb_id})

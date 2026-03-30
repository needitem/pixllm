from fastapi import APIRouter, Depends

from ..envelopes import ok, err
from ..deps import get_redis
from ..services.conversations.service import ConversationsService


router = APIRouter()


@router.get("/conversations")
async def list_conversations(page: int = 1, per_page: int = 20, redis = Depends(get_redis)):
    svc = ConversationsService(redis)
    data = await svc.list(page, per_page)
    return ok(data)


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str, redis = Depends(get_redis)):
    svc = ConversationsService(redis)
    data = await svc.get(conv_id)
    if not data:
        return err("NOT_FOUND", "conversation not found")
    return ok(data)


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str, redis = Depends(get_redis)):
    svc = ConversationsService(redis)
    await svc.delete(conv_id)
    return ok({"deleted": conv_id})

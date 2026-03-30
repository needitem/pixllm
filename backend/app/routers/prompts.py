from fastapi import APIRouter, Depends

from ..envelopes import ok, err
from ..deps import get_redis
from ..schemas.prompts import PromptCreate, PromptUpdate
from ..services.prompts.service import PromptsService


router = APIRouter()


@router.get("/prompts")
async def list_prompts(page: int = 1, per_page: int = 20, redis=Depends(get_redis)):
    svc = PromptsService(redis)
    data = await svc.list(page, per_page)
    return ok(data)


@router.get("/prompts/{prompt_id}")
async def get_prompt(prompt_id: str, redis=Depends(get_redis)):
    svc = PromptsService(redis)
    data = await svc.get(prompt_id)
    if not data:
        return err("NOT_FOUND", "prompt not found")
    return ok(data)


@router.post("/prompts")
async def create_prompt(payload: PromptCreate, redis=Depends(get_redis)):
    svc = PromptsService(redis)
    data = await svc.create(payload.model_dump())
    return ok(data)


@router.put("/prompts/{prompt_id}")
async def update_prompt(prompt_id: str, payload: PromptUpdate, redis=Depends(get_redis)):
    svc = PromptsService(redis)
    data = await svc.update(prompt_id, payload.model_dump(exclude_unset=True))
    if not data:
        return err("NOT_FOUND", "prompt not found")
    return ok(data)


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str, redis=Depends(get_redis)):
    svc = PromptsService(redis)
    await svc.delete(prompt_id)
    return ok({"deleted": prompt_id})

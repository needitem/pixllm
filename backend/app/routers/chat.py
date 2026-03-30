from fastapi import APIRouter, HTTPException, Depends

from ..deps import get_chat_deps, ChatDependencies
from ..envelopes import ok
from ..schemas.chat import ChatRequest, IntentVerifyRequest
from ..services.chat.execution import (
    execute_chat_request,
    http_exception_to_json_response,
    stream_chat_events,
    verify_chat_intent_request,
)


router = APIRouter()


@router.post("/chat/intent/verify")
async def verify_chat_intent(payload: IntentVerifyRequest, chat_deps: ChatDependencies = Depends(get_chat_deps)):
    try:
        return ok(await verify_chat_intent_request(payload, chat_deps))
    except HTTPException as exc:
        return http_exception_to_json_response(exc)


@router.post("/chat")
async def chat(request: ChatRequest, chat_deps: ChatDependencies = Depends(get_chat_deps)):
    try:
        return ok(await execute_chat_request(request, chat_deps))
    except HTTPException as exc:
        return http_exception_to_json_response(exc)


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, chat_deps: ChatDependencies = Depends(get_chat_deps)):
    return await stream_chat_events(request, chat_deps)

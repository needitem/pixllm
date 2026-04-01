import asyncio
import json
from contextlib import suppress

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..deps import state
from ..envelopes import ok, ApiError
from ..schemas.llm import LlmChatCompletionRequest
from ..core.llm_utils import (
    safe_chat_completion_create,
    extract_completion_finish_reason,
    extract_message_tool_calls,
    stream_chat_completion_text_with_meta,
)


router = APIRouter(prefix="/llm")


def _resolve_request_kwargs(request: LlmChatCompletionRequest):
    kwargs = {}
    if str(request.response_format or "").strip().lower() == "json_object":
        kwargs["response_format"] = {"type": "json_object"}
    if request.stop:
        kwargs["stop"] = list(request.stop)
    if request.tools:
        kwargs["tools"] = list(request.tools)
    if request.tool_choice is not None:
        kwargs["tool_choice"] = request.tool_choice
    return kwargs


def _sse_event(event: str, payload) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/chat_completions")
async def llm_chat_completions(request: LlmChatCompletionRequest):
    if state.vllm_client is None:
        raise ApiError("LLM_UNAVAILABLE", "vLLM client is not initialized", status_code=503)

    kwargs = _resolve_request_kwargs(request)

    completion = safe_chat_completion_create(
        model=request.model,
        messages=[message.model_dump() for message in list(request.messages or [])],
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        stream=False,
        client=state.vllm_client,
        **kwargs,
    )
    choices = getattr(completion, "choices", []) or []
    if not choices:
        return ok({"text": "", "tool_calls": [], "finish_reason": "", "usage": {}})
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", "") if message is not None else ""
    tool_calls = extract_message_tool_calls(message) if message is not None else []
    usage = getattr(completion, "usage", None)
    usage_payload = {}
    if usage is not None:
        usage_payload = {
            "prompt_tokens": int(getattr(usage, "prompt_tokens", 0) or 0),
            "completion_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
            "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
        }
    return ok(
        {
            "text": str(content or "").strip(),
            "tool_calls": tool_calls,
            "finish_reason": extract_completion_finish_reason(completion),
            "usage": usage_payload,
        }
    )


@router.post("/chat_completions/stream")
async def llm_chat_completions_stream(request: LlmChatCompletionRequest):
    if state.vllm_client is None:
        raise ApiError("LLM_UNAVAILABLE", "vLLM client is not initialized", status_code=503)

    kwargs = _resolve_request_kwargs(request)

    async def event_stream():
        queue: asyncio.Queue = asyncio.Queue()

        async def on_token(token: str):
            await queue.put(("token", {"content": str(token or "")}))

        async def runner():
            try:
                result = await stream_chat_completion_text_with_meta(
                    model=request.model,
                    messages=[message.model_dump() for message in list(request.messages or [])],
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    on_token=on_token,
                    client=state.vllm_client,
                    **kwargs,
                )
                await queue.put(
                    (
                        "done",
                        {
                            "text": str(result.get("text") or ""),
                            "tool_calls": list(result.get("tool_calls") or []),
                            "finish_reason": str(result.get("finish_reason") or ""),
                            "usage": {},
                        },
                    )
                )
            except Exception as exc:
                await queue.put(("error", {"message": str(exc)}))

        task = asyncio.create_task(runner())
        try:
            while True:
                event_name, payload = await queue.get()
                yield _sse_event(event_name, payload)
                if event_name in {"done", "error"}:
                    break
        finally:
            if not task.done():
                task.cancel()
                with suppress(Exception):
                    await task

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

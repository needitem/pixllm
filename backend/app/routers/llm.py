import asyncio
import json
import urllib.request
import urllib.error
from contextlib import suppress
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from .. import config
from ..deps import get_redis, state
from ..envelopes import ok, ApiError
from ..schemas.llm import LlmChatCompletionRequest, LlmTokenizeRequest
from ..core.llm_utils import (
    fallback_model_name,
    safe_chat_completion_create,
    extract_completion_finish_reason,
    extract_message_tool_calls,
    stream_chat_completion_text_with_meta,
)
from ..services.conversations.history import merge_conversation_messages, normalize_chat_messages
from ..services.conversations.service import ConversationsService


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


async def _prepare_conversation_messages(
    request: LlmChatCompletionRequest,
    redis,
) -> Tuple[List[Dict[str, str]], Optional[Dict[str, object]]]:
    conversation_id = str(request.conversation_id or "").strip()
    session_id = str(request.session_id or "").strip()
    request_messages = normalize_chat_messages(request.messages)
    if redis is None or (not conversation_id and not session_id):
        return request_messages, None

    svc = ConversationsService(redis)
    title_hint = ""
    for message in request_messages:
        if str(message.get("role") or "").strip().lower() == "user" and str(message.get("content") or "").strip():
            title_hint = str(message.get("content") or "").strip()
            break

    conversation = await svc.ensure_conversation(
        conv_id=conversation_id or None,
        session_id=session_id or None,
        model=request.model,
        title=title_hint,
    )
    stored_messages = list(conversation.get("messages") or [])
    merged_messages = merge_conversation_messages(stored_messages, request_messages)
    if merged_messages != stored_messages:
        conversation = await svc.replace_messages(
            conv_id=str(conversation.get("id") or ""),
            session_id=str(conversation.get("session_id") or ""),
            model=request.model,
            messages=merged_messages,
            title=str(conversation.get("title") or title_hint or ""),
        )
    return merged_messages, {"service": svc, "conversation": conversation}


def _normalize_tokenize_payload(payload):
    data = payload if isinstance(payload, dict) else {}
    tokens = data.get("tokens")
    if not isinstance(tokens, list):
        tokens = data.get("token_ids")
    if not isinstance(tokens, list):
        tokens = data.get("ids")
    if not isinstance(tokens, list):
        tokens = []
    token_strs = data.get("token_strs")
    if not isinstance(token_strs, list):
        token_strs = []
    count = 0
    for candidate in [
        data.get("count"),
        data.get("token_count"),
        data.get("prompt_tokens"),
        len(tokens),
    ]:
        try:
            value = int(candidate or 0)
        except Exception:
            value = 0
        if value >= 0:
            count = value
            break
    max_model_len = 0
    for candidate in [
        data.get("max_model_len"),
        data.get("max_model_len_tokens"),
        data.get("model_max_length"),
    ]:
        try:
            value = int(candidate or 0)
        except Exception:
            value = 0
        if value > 0:
            max_model_len = value
            break
    normalized_tokens = []
    for item in tokens:
        try:
            normalized_tokens.append(int(item))
        except Exception:
            continue
    return {
        "count": count,
        "max_model_len": max_model_len,
        "tokens": normalized_tokens,
        "token_strs": [str(item) for item in token_strs],
    }


@router.post("/chat_completions")
async def llm_chat_completions(request: LlmChatCompletionRequest, redis=Depends(get_redis)):
    if state.vllm_client is None:
        raise ApiError("LLM_UNAVAILABLE", "vLLM client is not initialized", status_code=503)

    kwargs = _resolve_request_kwargs(request)
    model_messages, conversation_ctx = await _prepare_conversation_messages(request, redis)

    completion = safe_chat_completion_create(
        model=request.model,
        messages=model_messages,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        stream=False,
        client=state.vllm_client,
        **kwargs,
    )
    choices = getattr(completion, "choices", []) or []
    conversation = conversation_ctx.get("conversation") if conversation_ctx else None
    if not choices:
        return ok(
            {
                "text": "",
                "tool_calls": [],
                "finish_reason": "",
                "usage": {},
                "conversation_id": str((conversation or {}).get("id") or request.conversation_id or "").strip() or None,
                "session_id": str((conversation or {}).get("session_id") or request.session_id or "").strip() or None,
            }
        )
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", "") if message is not None else ""
    tool_calls = extract_message_tool_calls(message) if message is not None else []
    usage = getattr(completion, "usage", None)
    if conversation_ctx and str(content or "").strip():
        svc = conversation_ctx["service"]
        conversation = await svc.append_message(
            str((conversation or {}).get("id") or ""),
            request.model,
            "assistant",
            str(content or ""),
            session_id=str((conversation or {}).get("session_id") or ""),
        )
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
            "conversation_id": str((conversation or {}).get("id") or request.conversation_id or "").strip() or None,
            "session_id": str((conversation or {}).get("session_id") or request.session_id or "").strip() or None,
        }
    )


@router.post("/tokenize")
async def llm_tokenize(request: LlmTokenizeRequest):
    if state.vllm_client is None:
        raise ApiError("LLM_UNAVAILABLE", "vLLM client is not initialized", status_code=503)

    resolved_model = fallback_model_name(request.model, client=state.vllm_client) or request.model
    request_body = json.dumps(
        {
            "model": resolved_model,
            "messages": [message.model_dump() for message in list(request.messages or [])],
            "return_token_strs": bool(request.return_token_strs),
        },
        ensure_ascii=False,
    ).encode("utf-8")
    upstream_request = urllib.request.Request(
        f"{config.VLLM_URL}/tokenize",
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(upstream_request, timeout=10) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise ApiError("LLM_TOKENIZE_FAILED", detail or str(exc), status_code=502)
    except Exception as exc:
        raise ApiError("LLM_TOKENIZE_FAILED", str(exc), status_code=502)

    return ok(_normalize_tokenize_payload(payload))


@router.post("/chat_completions/stream")
async def llm_chat_completions_stream(request: LlmChatCompletionRequest, redis=Depends(get_redis)):
    if state.vllm_client is None:
        raise ApiError("LLM_UNAVAILABLE", "vLLM client is not initialized", status_code=503)

    kwargs = _resolve_request_kwargs(request)
    model_messages, conversation_ctx = await _prepare_conversation_messages(request, redis)

    async def event_stream():
        queue: asyncio.Queue = asyncio.Queue()

        async def on_token(token: str):
            await queue.put(("token", {"content": str(token or "")}))

        async def runner():
            try:
                result = await stream_chat_completion_text_with_meta(
                    model=request.model,
                    messages=model_messages,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    on_token=on_token,
                    client=state.vllm_client,
                    **kwargs,
                )
                conversation = conversation_ctx.get("conversation") if conversation_ctx else None
                if conversation_ctx and str(result.get("text") or "").strip():
                    svc = conversation_ctx["service"]
                    conversation = await svc.append_message(
                        str((conversation or {}).get("id") or ""),
                        request.model,
                        "assistant",
                        str(result.get("text") or ""),
                        session_id=str((conversation or {}).get("session_id") or ""),
                    )
                await queue.put(
                    (
                        "done",
                        {
                            "text": str(result.get("text") or ""),
                            "tool_calls": list(result.get("tool_calls") or []),
                            "finish_reason": str(result.get("finish_reason") or ""),
                            "usage": {},
                            "conversation_id": str((conversation or {}).get("id") or request.conversation_id or "").strip() or None,
                            "session_id": str((conversation or {}).get("session_id") or request.session_id or "").strip() or None,
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

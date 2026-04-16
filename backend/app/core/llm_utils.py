import asyncio
import logging
import re
import threading
from inspect import isawaitable
from typing import Any, Dict, List, Optional

from .. import config
from ..deps import state


logger = logging.getLogger(__name__)


def _resolve_client(client=None):
    return client or state.vllm_client


def available_model_ids(client=None) -> List[str]:
    resolved_client = _resolve_client(client)
    if resolved_client is None:
        return []
    try:
        resp = resolved_client.models.list()
        rows = getattr(resp, "data", []) or []
        ids: List[str] = []
        for r in rows:
            rid = getattr(r, "id", None)
            if not rid and isinstance(r, dict):
                rid = r.get("id")
            if rid:
                ids.append(str(rid))
        return [x for x in ids if x]
    except Exception:
        return []


def fallback_model_name(current: str, client=None) -> Optional[str]:
    model_ids = available_model_ids(client)
    if not model_ids:
        return None
    if current in model_ids:
        return current
    return model_ids[0]


def parse_allowed_completion_tokens(error_message: str) -> Optional[int]:
    msg = str(error_message or "")
    safety_buffer = 64 if "requested" in msg.lower() and "output tokens" in msg.lower() else 32
    patterns = [
        r"maximum context length is\s*(\d+)\s*tokens\s*and your request has\s*(\d+)\s*input tokens",
        r"passed\s*(\d+)\s*input tokens[\s\S]*?context length is only\s*(\d+)\s*tokens",
    ]
    for pattern in patterns:
        m = re.search(pattern, msg, flags=re.IGNORECASE)
        if not m:
            continue
        try:
            if "passed" in pattern:
                input_tokens = int(m.group(1))
                window = int(m.group(2))
            else:
                window = int(m.group(1))
                input_tokens = int(m.group(2))
        except Exception:
            return None
        return max(64, window - input_tokens - safety_buffer)
    return None


def _coerce_stream_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: List[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
                continue
            text = getattr(item, "text", None)
            if isinstance(text, str):
                parts.append(text)
        return "".join(parts)
    return ""


def extract_choice_finish_reason(choice: Any) -> str:
    reason = getattr(choice, "finish_reason", None)
    if reason is None and isinstance(choice, dict):
        reason = choice.get("finish_reason")
    return str(reason or "").strip().lower()


def extract_completion_finish_reason(completion: Any) -> str:
    choices = getattr(completion, "choices", None)
    if choices is None and isinstance(completion, dict):
        choices = completion.get("choices")
    if not choices:
        return ""
    return extract_choice_finish_reason(choices[0])


def extract_stream_delta_text(chunk: Any) -> str:
    choices = getattr(chunk, "choices", None)
    if choices is None and isinstance(chunk, dict):
        choices = chunk.get("choices")
    if not choices:
        return ""

    choice = choices[0]
    delta = getattr(choice, "delta", None)
    if delta is None and isinstance(choice, dict):
        delta = choice.get("delta")
    if delta is None:
        return ""

    content = getattr(delta, "content", None)
    if content is None and isinstance(delta, dict):
        content = delta.get("content")
    return _coerce_stream_text(content)


def _normalize_tool_call_item(item: Any) -> Dict[str, Any]:
    function = getattr(item, "function", None)
    if function is None and isinstance(item, dict):
        function = item.get("function")
    if function is None:
        function = {}
    name = getattr(function, "name", None)
    if name is None and isinstance(function, dict):
        name = function.get("name")
    arguments = getattr(function, "arguments", None)
    if arguments is None and isinstance(function, dict):
        arguments = function.get("arguments")
    item_id = getattr(item, "id", None)
    if item_id is None and isinstance(item, dict):
        item_id = item.get("id")
    index = getattr(item, "index", None)
    if index is None and isinstance(item, dict):
        index = item.get("index")
    return {
        "id": str(item_id or ""),
        "index": int(index or 0),
        "function": {
            "name": str(name or ""),
            "arguments": str(arguments or ""),
        },
    }


def extract_stream_delta_tool_calls(chunk: Any) -> List[Dict[str, Any]]:
    choices = getattr(chunk, "choices", None)
    if choices is None and isinstance(chunk, dict):
        choices = chunk.get("choices")
    if not choices:
        return []

    choice = choices[0]
    delta = getattr(choice, "delta", None)
    if delta is None and isinstance(choice, dict):
        delta = choice.get("delta")
    if delta is None:
        return []

    tool_calls = getattr(delta, "tool_calls", None)
    if tool_calls is None and isinstance(delta, dict):
        tool_calls = delta.get("tool_calls")
    if not tool_calls:
        return []
    return [_normalize_tool_call_item(item) for item in list(tool_calls)]


def extract_message_tool_calls(message: Any) -> List[Dict[str, Any]]:
    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls is None and isinstance(message, dict):
        tool_calls = message.get("tool_calls")
    if not tool_calls:
        return []
    return [_normalize_tool_call_item(item) for item in list(tool_calls)]


async def _maybe_await_callback(callback, *args, **kwargs) -> None:
    if callback is None:
        return
    result = callback(*args, **kwargs)
    if isawaitable(result):
        await result


async def stream_chat_completion_text_with_meta(
    *,
    model: str,
    messages: List[Dict[str, Any]],
    max_tokens: int,
    temperature: float,
    on_token=None,
    client=None,
    **kwargs,
) -> Dict[str, Any]:
    resolved_client = _resolve_client(client)
    if resolved_client is None:
        raise RuntimeError("vLLM client is not initialized")

    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def _emit(kind: str, payload: Any) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, (kind, payload))

    def _worker() -> None:
        try:
            stream = safe_chat_completion_create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                client=resolved_client,
                **kwargs,
            )
            saw_token = False
            finish_reason = ""
            tool_calls: List[Dict[str, Any]] = []
            for chunk in stream:
                choices = getattr(chunk, "choices", None)
                if choices is None and isinstance(chunk, dict):
                    choices = chunk.get("choices")
                if choices:
                    chunk_reason = extract_choice_finish_reason(choices[0])
                    if chunk_reason:
                        finish_reason = chunk_reason
                text = extract_stream_delta_text(chunk)
                if text:
                    saw_token = True
                    _emit("token", text)
                for item in extract_stream_delta_tool_calls(chunk):
                    index = int(item.get("index", 0) or 0)
                    while len(tool_calls) <= index:
                        tool_calls.append({"id": "", "function": {"name": "", "arguments": ""}})
                    target = tool_calls[index]
                    if item.get("id"):
                        target["id"] = str(item["id"])
                    function = item.get("function") if isinstance(item.get("function"), dict) else {}
                    target_fn = target.setdefault("function", {})
                    if function.get("name"):
                        target_fn["name"] = str(function["name"])
                    if function.get("arguments"):
                        target_fn["arguments"] = f'{target_fn.get("arguments", "")}{function["arguments"]}'
            _emit("done", {"saw_token": saw_token, "finish_reason": finish_reason, "tool_calls": tool_calls})
        except Exception as exc:  # pragma: no cover - exercised via callers
            _emit("error", exc)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

    parts: List[str] = []
    finish_reason = ""
    streamed_tool_calls: List[Dict[str, Any]] = []
    while True:
        kind, payload = await queue.get()
        if kind == "token":
            token = str(payload or "")
            parts.append(token)
            await _maybe_await_callback(on_token, token)
            continue
        if kind == "error":
            raise payload
        if kind == "done":
            if isinstance(payload, dict):
                finish_reason = str(payload.get("finish_reason") or "").strip().lower()
                streamed_tool_calls = list(payload.get("tool_calls") or [])
            break

    answer = "".join(parts).strip()
    if answer or streamed_tool_calls:
        return {
            "text": answer,
            "tool_calls": streamed_tool_calls,
            "finish_reason": finish_reason,
            "truncated": finish_reason == "length",
        }

    completion = await asyncio.to_thread(
        safe_chat_completion_create,
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=False,
        client=resolved_client,
        **kwargs,
    )
    if not completion.choices:
        return {"text": "", "tool_calls": [], "finish_reason": "", "truncated": False}
    fallback = str(completion.choices[0].message.content or "").strip()
    if fallback:
        await _maybe_await_callback(on_token, fallback)
    completion_finish_reason = extract_completion_finish_reason(completion)
    fallback_tool_calls = extract_message_tool_calls(completion.choices[0].message)
    return {
        "text": fallback,
        "tool_calls": fallback_tool_calls,
        "finish_reason": completion_finish_reason,
        "truncated": completion_finish_reason == "length",
    }


def safe_chat_completion_create(
    *,
    model: str,
    messages: List[Dict[str, Any]],
    max_tokens: int,
    temperature: float,
    stream: bool = False,
    client=None,
    **kwargs,
):
    resolved_client = _resolve_client(client)
    if resolved_client is None:
        raise RuntimeError("vLLM client is not initialized")

    use_model = model or config.VLLM_MODEL
    use_max_tokens = max(64, int(max_tokens or 256))

    for _ in range(4):
        try:
            return resolved_client.chat.completions.create(
                model=use_model,
                messages=messages,
                max_tokens=use_max_tokens,
                temperature=temperature,
                stream=stream,
                **kwargs,
            )
        except Exception as exc:
            err_text = str(exc)
            lowered = err_text.lower()

            if "does not exist" in lowered or "notfounderror" in lowered:
                fallback_model = fallback_model_name(use_model, resolved_client)
                if fallback_model and fallback_model != use_model:
                    logger.warning("Model not found, falling back", extra={"from": use_model, "to": fallback_model})
                    use_model = fallback_model
                    continue

            allowed = parse_allowed_completion_tokens(err_text)
            if allowed and allowed < use_max_tokens:
                logger.warning(
                    "Reducing max_tokens due to context window",
                    extra={"from": use_max_tokens, "to": allowed, "model": use_model},
                )
                use_max_tokens = allowed
                continue

            raise

    return resolved_client.chat.completions.create(
        model=use_model,
        messages=messages,
        max_tokens=use_max_tokens,
        temperature=temperature,
        stream=stream,
        **kwargs,
    )


async def stream_chat_completion_text(
    *,
    model: str,
    messages: List[Dict[str, Any]],
    max_tokens: int,
    temperature: float,
    on_token=None,
    client=None,
    **kwargs,
) -> str:
    result = await stream_chat_completion_text_with_meta(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        on_token=on_token,
        client=client,
        **kwargs,
    )
    return str(result.get("text") or "")

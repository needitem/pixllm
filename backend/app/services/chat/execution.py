import asyncio
import logging
from contextlib import suppress
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from ... import rag_config
from ...schemas.chat import ChatRequest, IntentVerifyRequest
from ...utils.sse import sse_event
from .http import http_exception_to_error_payload, http_exception_to_json_response, raise_http_error
from .pipeline import execute_prepared_chat
from .preparation import PreparedChatExecution, prepare_chat_execution, verify_chat_intent_request
from .react.engine import StageTimeoutError


logger = logging.getLogger(__name__)


def chunk_text_for_sse(text: str, chunk_size: int = 80) -> List[str]:
    content = str(text or "")
    if not content:
        return []
    size = max(20, min(int(chunk_size), 300))
    return [content[i : i + size] for i in range(0, len(content), size)]


async def execute_chat_request(request: ChatRequest, chat_deps: Any) -> Dict[str, Any]:
    prepared: Optional[PreparedChatExecution] = None
    try:
        prepared = await prepare_chat_execution(request, chat_deps)
        return await execute_prepared_chat(prepared)
    except HTTPException:
        raise
    except StageTimeoutError as exc:
        if prepared is not None:
            await prepared.run_tracker.record_error("CHAT_STAGE_TIMEOUT", str(exc), stage=exc.stage)
        raise_http_error(
            504,
            "CHAT_STAGE_TIMEOUT",
            str(exc),
            stage=exc.stage,
            timeout_sec=exc.timeout_sec,
            run_id=prepared.run_id if prepared is not None else None,
        )
    except Exception as exc:
        logger.exception("Chat execution failed")
        if prepared is not None:
            stage = prepared.run_tracker.current_phase or "answer"
            await prepared.run_tracker.record_error("LLM_UNAVAILABLE", str(exc), stage=stage)
        raise_http_error(
            503,
            "LLM_UNAVAILABLE",
            str(exc),
            run_id=prepared.run_id if prepared is not None else None,
        )


async def stream_chat_events(request: ChatRequest, chat_deps: Any) -> StreamingResponse:
    async def generate() -> AsyncGenerator[str, None]:
        queue: asyncio.Queue = asyncio.Queue()
        sentinel = object()

        async def _enqueue(event_name: str, payload: Dict[str, Any]) -> None:
            await queue.put((event_name, payload))

        async def _worker() -> None:
            prepared: Optional[PreparedChatExecution] = None
            streamed_token_count = 0
            sources_emitted = False
            prepare_timeout = int(rag_config.react_prepare_timeout_sec() or 0)

            try:
                await _enqueue("status", {"phase": "accepted", "message": "Request accepted."})
                await _enqueue("status", {"phase": "prepare", "message": "Preparing request."})

                if prepare_timeout > 0:
                    prepared = await asyncio.wait_for(
                        prepare_chat_execution(request, chat_deps),
                        timeout=float(prepare_timeout),
                    )
                else:
                    prepared = await prepare_chat_execution(request, chat_deps)

                await _enqueue(
                    "status",
                    {
                        "phase": "plan",
                        "message": "Execution plan prepared.",
                        "response_type": prepared.resolved.response_type,
                        "run_id": prepared.run_id,
                    },
                )

                async def _status(payload: Dict[str, Any]) -> None:
                    enriched = dict(payload or {})
                    enriched.setdefault("run_id", prepared.run_id)
                    await _enqueue("status", enriched)

                async def _token(token: str) -> None:
                    nonlocal streamed_token_count
                    if not token:
                        return
                    streamed_token_count += len(token)
                    await _enqueue("token", {"content": token})

                async def _sources(rows: List[Dict[str, Any]]) -> None:
                    nonlocal sources_emitted
                    if not rows:
                        return
                    sources_emitted = True
                    await _enqueue("sources", {"sources": rows})

                payload = await execute_prepared_chat(
                    prepared,
                    status_callback=_status,
                    token_callback=_token,
                    sources_callback=_sources,
                )

                if payload["sources"] and not sources_emitted:
                    await _enqueue("sources", {"sources": payload["sources"]})

                if streamed_token_count == 0:
                    for token in chunk_text_for_sse(payload["answer"]):
                        await _enqueue("token", {"content": token})

                await _enqueue("done", payload)
            except HTTPException as exc:
                await _enqueue("error", http_exception_to_error_payload(exc))
            except asyncio.TimeoutError:
                code = "CHAT_STAGE_TIMEOUT"
                message = f"prepare stage timed out after {prepare_timeout}s"
                if prepared is not None:
                    await prepared.run_tracker.record_error(code, message, stage="prepare")
                await _enqueue(
                    "error",
                    {
                        "code": code,
                        "message": message,
                        "stage": "prepare",
                        "timeout_sec": prepare_timeout,
                        "run_id": prepared.run_id if prepared is not None else None,
                    },
                )
            except StageTimeoutError as exc:
                if prepared is not None:
                    await prepared.run_tracker.record_error("CHAT_STAGE_TIMEOUT", str(exc), stage=exc.stage)
                await _enqueue(
                    "error",
                    {
                        "code": "CHAT_STAGE_TIMEOUT",
                        "message": str(exc),
                        "stage": exc.stage,
                        "timeout_sec": exc.timeout_sec,
                        "run_id": prepared.run_id if prepared is not None else None,
                    },
                )
            except Exception as exc:
                logger.exception("Chat stream execution failed")
                if prepared is not None:
                    stage = prepared.run_tracker.current_phase or "answer"
                    await prepared.run_tracker.record_error("LLM_UNAVAILABLE", str(exc), stage=stage)
                await _enqueue(
                    "error",
                    {
                        "code": "LLM_UNAVAILABLE",
                        "message": str(exc),
                        "run_id": prepared.run_id if prepared is not None else None,
                    },
                )
            finally:
                await queue.put(sentinel)

        worker_task = asyncio.create_task(_worker())
        try:
            while True:
                item = await queue.get()
                if item is sentinel:
                    break
                event_name, payload = item
                yield sse_event(event_name, payload)
        finally:
            if not worker_task.done():
                worker_task.cancel()
            with suppress(asyncio.CancelledError):
                await worker_task

    return StreamingResponse(generate(), media_type="text/event-stream")


__all__ = [
    "chunk_text_for_sse",
    "execute_chat_request",
    "http_exception_to_json_response",
    "stream_chat_events",
    "verify_chat_intent_request",
]

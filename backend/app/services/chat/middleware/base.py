from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ..preparation import PreparedChatExecution


StatusCallback = Optional[Callable[[Dict[str, Any]], Awaitable[None] | None]]
TokenCallback = Optional[Callable[[str], Awaitable[None] | None]]
SourcesCallback = Optional[Callable[[List[Dict[str, Any]]], Awaitable[None] | None]]


@dataclass
class ChatExecutionContext:
    prepared: "PreparedChatExecution"
    status_callback: StatusCallback = None
    token_callback: TokenCallback = None
    sources_callback: SourcesCallback = None
    react_payload: Optional[Dict[str, Any]] = None
    sources_recorded: bool = False
    workspace_snapshot: Optional[Dict[str, Any]] = None
    final_payload: Optional[Dict[str, Any]] = None


ChatExecutionHandler = Callable[[ChatExecutionContext], Awaitable[ChatExecutionContext]]


class ChatExecutionMiddleware(Protocol):
    async def __call__(self, ctx: ChatExecutionContext, call_next: ChatExecutionHandler) -> ChatExecutionContext:
        ...


def build_chat_execution_pipeline(
    middlewares: List[ChatExecutionMiddleware],
    terminal_handler: ChatExecutionHandler,
) -> ChatExecutionHandler:
    handler = terminal_handler
    for middleware in reversed(list(middlewares or [])):
        next_handler = handler

        async def _wrapped(ctx: ChatExecutionContext, _mw=middleware, _next=next_handler) -> ChatExecutionContext:
            return await _mw(ctx, _next)

        handler = _wrapped
    return handler

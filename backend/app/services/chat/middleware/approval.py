from ..approval import ensure_execution_approval
from .base import ChatExecutionContext, ChatExecutionHandler


class ApprovalGateMiddleware:
    async def __call__(self, ctx: ChatExecutionContext, call_next: ChatExecutionHandler) -> ChatExecutionContext:
        await ensure_execution_approval(ctx.prepared)
        return await call_next(ctx)

from ..cancellation import ensure_run_not_cancelled
from .base import ChatExecutionContext, ChatExecutionHandler


class CancellationMiddleware:
    def __init__(self, *, before_stage: str = "prepare", after_stage: str = "verify"):
        self.before_stage = before_stage
        self.after_stage = after_stage

    async def __call__(self, ctx: ChatExecutionContext, call_next: ChatExecutionHandler) -> ChatExecutionContext:
        await ensure_run_not_cancelled(ctx.prepared, stage=self.before_stage)
        result = await call_next(ctx)
        await ensure_run_not_cancelled(ctx.prepared, stage=self.after_stage)
        return result

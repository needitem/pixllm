from .middleware import (
    ApprovalGateMiddleware,
    CancellationMiddleware,
    ChatExecutionContext,
    build_chat_execution_pipeline,
)
from .results import finalize_react_payload, run_react_payload


async def _execute_terminal(ctx: ChatExecutionContext) -> ChatExecutionContext:
    ctx.react_payload, ctx.sources_recorded, ctx.workspace_snapshot = await run_react_payload(
        ctx.prepared,
        status_callback=ctx.status_callback,
        token_callback=ctx.token_callback,
        sources_callback=ctx.sources_callback,
    )
    ctx.final_payload = await finalize_react_payload(
        ctx.prepared,
        ctx.react_payload,
        sources_recorded=ctx.sources_recorded,
        workspace_snapshot=ctx.workspace_snapshot,
    )
    return ctx


async def execute_prepared_chat(
    prepared,
    *,
    status_callback=None,
    token_callback=None,
    sources_callback=None,
):
    pipeline = build_chat_execution_pipeline(
        [
            CancellationMiddleware(before_stage="plan", after_stage="verify"),
            ApprovalGateMiddleware(),
        ],
        _execute_terminal,
    )
    ctx = ChatExecutionContext(
        prepared=prepared,
        status_callback=status_callback,
        token_callback=token_callback,
        sources_callback=sources_callback,
    )
    result = await pipeline(ctx)
    return result.final_payload

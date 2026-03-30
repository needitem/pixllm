from typing import TYPE_CHECKING

from .http import raise_http_error

if TYPE_CHECKING:
    from .preparation import PreparedChatExecution


async def ensure_run_not_cancelled(prepared: "PreparedChatExecution", *, stage: str) -> None:
    if await prepared.run_svc.is_cancel_requested(prepared.run_id):
        await prepared.run_tracker.record_error("RUN_CANCELLED", f"Run cancelled during {stage}", stage=stage)
        raise_http_error(409, "RUN_CANCELLED", f"Run cancelled during {stage}", run_id=prepared.run_id, stage=stage)

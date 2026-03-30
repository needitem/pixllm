from typing import Any, Dict, Optional, TYPE_CHECKING

from .http import raise_http_error

if TYPE_CHECKING:
    from .preparation import PreparedChatExecution


async def ensure_execution_approval(prepared: "PreparedChatExecution") -> Optional[Dict[str, Any]]:
    if not bool(prepared.execution_plan.get("needs_approval")):
        return None

    approval = await prepared.run_svc.get_latest_approval(prepared.run_id, "execution_plan")
    if approval is None:
        approval = await prepared.run_svc.create_approval(
            prepared.run_id,
            approval_type="execution_plan",
            title="Execution plan review required",
            reason="Run marked as approval-required by planning policy",
            owner_agent="planner",
            task_key="plan",
            metadata={
                "risk_class": prepared.execution_plan.get("risk_class"),
                "required_agents": list(prepared.execution_plan.get("required_agents") or []),
            },
        )

    status = str((approval or {}).get("status") or "").strip().lower()
    if status == "approved":
        await prepared.run_svc.update_run(
            prepared.run_id,
            status="running",
            metadata={"approval_cleared_at": (approval or {}).get("resolved_at")},
        )
        return approval

    if status == "rejected":
        await prepared.run_tracker.record_error(
            "EXECUTION_PLAN_REJECTED",
            "Execution plan was rejected and cannot continue.",
            stage="approval",
        )
        raise_http_error(
            409,
            "EXECUTION_PLAN_REJECTED",
            "Execution plan was rejected and cannot continue.",
            run_id=prepared.run_id,
            approval_id=(approval or {}).get("approval_id"),
        )

    await prepared.run_tracker.record_phase(
        "approval",
        "Waiting for approval before execution.",
        approval_id=(approval or {}).get("approval_id"),
        approval_type=(approval or {}).get("type"),
    )
    await prepared.run_svc.update_run(
        prepared.run_id,
        status="waiting_approval",
        metadata={"approval_pending_at": (approval or {}).get("created_at")},
    )
    raise_http_error(
        409,
        "APPROVAL_REQUIRED",
        "Execution requires approval before continuing.",
        run_id=prepared.run_id,
        approval_id=(approval or {}).get("approval_id"),
        approval_type=(approval or {}).get("type"),
    )

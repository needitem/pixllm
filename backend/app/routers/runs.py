from fastapi import APIRouter
from pydantic import BaseModel

from ..envelopes import err, ok


router = APIRouter()


class ResumeRunRequest(BaseModel):
    from_task_key: str = ""
    from_step_key: str = ""


class CancelRunRequest(BaseModel):
    reason: str = ""


class ResolveApprovalRequest(BaseModel):
    reviewer: str = ""
    note: str = ""


@router.get("/runs")
async def list_runs(page: int = 1, per_page: int = 20):
    return ok(
        {
            "items": [],
            "total": 0,
            "page": max(1, int(page)),
            "per_page": max(1, int(per_page)),
        }
    )


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    return err("NOT_FOUND", f"run not found: {run_id}")


@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str, payload: CancelRunRequest):
    del payload
    return err("NOT_FOUND", f"run not found: {run_id}")


@router.post("/runs/{run_id}/resume")
async def resume_run(run_id: str, payload: ResumeRunRequest):
    del payload
    return err("NOT_FOUND", f"run not found: {run_id}")


@router.get("/runs/{run_id}/approvals")
async def list_approvals(run_id: str):
    return err("NOT_FOUND", f"run not found: {run_id}")


@router.post("/runs/{run_id}/approvals/{approval_id}/approve")
async def approve_run_action(run_id: str, approval_id: str, payload: ResolveApprovalRequest):
    del approval_id, payload
    return err("NOT_FOUND", f"run not found: {run_id}")


@router.post("/runs/{run_id}/approvals/{approval_id}/reject")
async def reject_run_action(run_id: str, approval_id: str, payload: ResolveApprovalRequest):
    del approval_id, payload
    return err("NOT_FOUND", f"run not found: {run_id}")

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..deps import get_redis
from ..envelopes import ok, err
from ..services.execution.runs import ExecutionRunsService


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
async def list_runs(page: int = 1, per_page: int = 20, redis=Depends(get_redis)):
    svc = ExecutionRunsService(redis)
    data = await svc.list(page=page, per_page=per_page)
    return ok(data)


@router.get("/runs/{run_id}")
async def get_run(run_id: str, redis=Depends(get_redis)):
    svc = ExecutionRunsService(redis)
    data = await svc.get(run_id)
    if not data:
        return err("NOT_FOUND", "run not found")
    return ok(data)


@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str, payload: CancelRunRequest, redis=Depends(get_redis)):
    svc = ExecutionRunsService(redis)
    data = await svc.request_cancel(run_id, reason=payload.reason)
    if not data:
        return err("NOT_FOUND", "run not found")
    return ok(data)


@router.post("/runs/{run_id}/resume")
async def resume_run(run_id: str, payload: ResumeRunRequest, redis=Depends(get_redis)):
    svc = ExecutionRunsService(redis)
    data = await svc.resume_run(run_id, from_task_key=payload.from_task_key, from_step_key=payload.from_step_key)
    if not data:
        return err("NOT_FOUND", "run not found")
    return ok(data)


@router.get("/runs/{run_id}/approvals")
async def list_approvals(run_id: str, redis=Depends(get_redis)):
    svc = ExecutionRunsService(redis)
    data = await svc.get(run_id)
    if not data:
        return err("NOT_FOUND", "run not found")
    return ok({"items": list(data.get("approvals") or []), "total": len(list(data.get("approvals") or []))})


@router.post("/runs/{run_id}/approvals/{approval_id}/approve")
async def approve_run_action(run_id: str, approval_id: str, payload: ResolveApprovalRequest, redis=Depends(get_redis)):
    svc = ExecutionRunsService(redis)
    approval = await svc.update_approval(run_id, approval_id, status="approved", reviewer=payload.reviewer, note=payload.note)
    if not approval:
        return err("NOT_FOUND", "approval not found")
    return ok(approval)


@router.post("/runs/{run_id}/approvals/{approval_id}/reject")
async def reject_run_action(run_id: str, approval_id: str, payload: ResolveApprovalRequest, redis=Depends(get_redis)):
    svc = ExecutionRunsService(redis)
    approval = await svc.update_approval(run_id, approval_id, status="rejected", reviewer=payload.reviewer, note=payload.note)
    if not approval:
        return err("NOT_FOUND", "approval not found")
    return ok(approval)

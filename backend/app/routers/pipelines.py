import asyncio
from pathlib import Path
from typing import Callable
from typing import Optional

from fastapi import APIRouter, Header

from .. import config
from ..core.policy import SecurityPolicy
from ..envelopes import ApiError, ok
from ..schemas.pipelines import (
    StartEmbedDocsRequest,
    StartResetRagRequest,
    StartVerifyEmbeddingsRequest,
)
from ..services.pipelines.pipeline_jobs import get_job, list_jobs, start_job


router = APIRouter(prefix="/pipelines")


def _load_pipeline_action(action_name: str) -> Callable:
    try:
        from ..services.pipelines import pipeline_tasks
    except Exception as exc:
        raise ApiError(
            "PIPELINE_DEPENDENCY_UNAVAILABLE",
            f"pipeline dependencies unavailable: {exc}",
            status_code=503,
        ) from exc

    actions = {
        "embed_docs": pipeline_tasks.run_embed_docs_task,
        "verify_embeddings": pipeline_tasks.run_verify_embeddings_task,
        "reset_rag_data": pipeline_tasks.run_reset_rag_task,
    }
    return actions[action_name]


def _require_pipeline_access(x_pipeline_token: Optional[str]) -> None:
    SecurityPolicy.require_pipeline_access(x_pipeline_token)


@router.get("/jobs")
async def pipeline_jobs(limit: int = 50, x_pipeline_token: Optional[str] = Header(default=None)):
    _require_pipeline_access(x_pipeline_token)
    return ok({"items": await asyncio.to_thread(list_jobs, limit=limit)})


@router.get("/jobs/{job_id}")
async def pipeline_job(job_id: str, x_pipeline_token: Optional[str] = Header(default=None)):
    _require_pipeline_access(x_pipeline_token)
    row = await asyncio.to_thread(get_job, job_id)
    if not row:
        raise ApiError("PIPELINE_JOB_NOT_FOUND", "pipeline job not found", status_code=404)
    return ok(row)


@router.post("/docs/embed/start")
async def pipeline_embed_docs(
    request: StartEmbedDocsRequest,
    x_pipeline_token: Optional[str] = Header(default=None),
):
    _require_pipeline_access(x_pipeline_token)
    docs_dir = Path(request.docs_dir)
    if not docs_dir.exists() or not docs_dir.is_dir():
        raise ApiError("PIPELINE_INVALID_DOCS_DIR", "docs_dir must be an existing directory", status_code=400)

    job = await asyncio.to_thread(
        start_job,
        name="embed_docs",
        action=_load_pipeline_action("embed_docs"),
        payload={
            "docs_dir": str(docs_dir),
            "qdrant_url": request.qdrant_url,
            "batch_size": request.batch_size,
            "model": request.model,
            "force_reindex": request.force_reindex,
        },
    )
    return ok(job)


@router.post("/docs/verify/start")
async def pipeline_verify_docs(
    request: StartVerifyEmbeddingsRequest,
    x_pipeline_token: Optional[str] = Header(default=None),
):
    _require_pipeline_access(x_pipeline_token)
    job = await asyncio.to_thread(
        start_job,
        name="verify_embeddings",
        action=_load_pipeline_action("verify_embeddings"),
        payload={
            "qdrant_url": request.qdrant_url,
            "model": request.model,
            "top_k": request.top_k,
            "query": request.query,
            "collection": request.collection,
        },
    )
    return ok(job)


@router.post("/rag/reset/start")
async def pipeline_reset_rag(
    request: StartResetRagRequest,
    x_pipeline_token: Optional[str] = Header(default=None),
):
    _require_pipeline_access(x_pipeline_token)
    job = await asyncio.to_thread(
        start_job,
        name="reset_rag_data",
        action=_load_pipeline_action("reset_rag_data"),
        payload={
            "skip_minio": request.skip_minio,
            "keep_documents_only": request.keep_documents_only,
        },
    )
    return ok(job)

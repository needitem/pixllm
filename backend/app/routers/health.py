from fastapi import APIRouter, Depends
from fastapi.responses import Response

from ..deps import get_redis, get_minio, get_search_svc, get_embed_model, get_vllm_client
from ..envelopes import ok
from ..metrics import metrics_registry, render_health_metrics
from ..services.health.service import (
    build_health_response,
    build_liveness_response,
    build_readiness_response,
)


router = APIRouter()


@router.get("/health/live")
async def live():
    return ok(build_liveness_response())


@router.get("/health")
async def health(
    redis=Depends(get_redis),
    minio=Depends(get_minio),
    search_svc=Depends(get_search_svc),
    embed_model=Depends(get_embed_model),
    vllm_client=Depends(get_vllm_client),
):
    return ok(await build_health_response(
        redis=redis,
        minio=minio,
        search_svc=search_svc,
        embed_model=embed_model,
        vllm_client=vllm_client,
    ))


@router.get("/health/ready")
async def ready(
    redis=Depends(get_redis),
    minio=Depends(get_minio),
    search_svc=Depends(get_search_svc),
    embed_model=Depends(get_embed_model),
    vllm_client=Depends(get_vllm_client),
):
    return ok(await build_readiness_response(
        redis=redis,
        minio=minio,
        search_svc=search_svc,
        embed_model=embed_model,
        vllm_client=vllm_client,
    ))


@router.get("/metrics", include_in_schema=False)
async def metrics(
    redis=Depends(get_redis),
    minio=Depends(get_minio),
    search_svc=Depends(get_search_svc),
    embed_model=Depends(get_embed_model),
    vllm_client=Depends(get_vllm_client),
):
    readiness = await build_readiness_response(
        redis=redis,
        minio=minio,
        search_svc=search_svc,
        embed_model=embed_model,
        vllm_client=vllm_client,
    )
    metrics_registry.record_scrape()
    payload = metrics_registry.render_prometheus(
        extra_lines=render_health_metrics(readiness),
    )
    return Response(
        content=payload,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )

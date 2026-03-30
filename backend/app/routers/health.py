from fastapi import APIRouter, Depends

from ..deps import get_redis, get_minio, get_search_svc, get_embed_model, get_vllm_client, get_orchestrator
from ..envelopes import ok
from ..services.health.service import build_health_response


router = APIRouter()


@router.get("/health")
async def health(
    redis=Depends(get_redis),
    minio=Depends(get_minio),
    search_svc=Depends(get_search_svc),
    embed_model=Depends(get_embed_model),
    vllm_client=Depends(get_vllm_client),
    orchestrator=Depends(get_orchestrator),
):
    return ok(await build_health_response(
        redis=redis,
        minio=minio,
        search_svc=search_svc,
        embed_model=embed_model,
        vllm_client=vllm_client,
        orchestration_policy=orchestrator,
    ))

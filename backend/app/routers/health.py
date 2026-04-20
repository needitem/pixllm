from fastapi import APIRouter

from ..envelopes import ok
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
async def health():
    return ok(await build_health_response())


@router.get("/health/ready")
async def ready():
    return ok(await build_readiness_response())

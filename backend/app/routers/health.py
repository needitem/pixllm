"""헬스체크 라우터.

쿠버네티스/로드밸런서 관례를 따라 세 단계로 나뉜다:
- /health/live  : 프로세스가 살아만 있으면 OK (liveness probe)
- /health       : 소스 저장소·인덱스 상태까지 포함한 상세 점검
- /health/ready : 트래픽을 받아도 되는 상태인지 (readiness probe)
실제 점검 로직은 services/health/service.py에 있다.
"""

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
    """liveness 체크: 서버 프로세스 생존 여부만 확인한다. 항상 status=ok."""
    return ok(build_liveness_response())


@router.get("/health")
async def health():
    """상세 헬스체크: 원본 소스 디렉터리 존재 여부, 소스 파일 수, 인덱스 파일 유무까지 보고한다."""
    return ok(await build_health_response())


@router.get("/health/ready")
async def ready():
    """readiness 체크: 상세 헬스체크 결과에 `ready` 불리언을 더해 반환한다."""
    return ok(await build_readiness_response())

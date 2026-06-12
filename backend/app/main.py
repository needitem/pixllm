"""FastAPI 앱 조립 모듈 (서버 진입점).

이 파일이 하는 일은 세 가지다:
1. 앱 생성 + 수명주기(lifespan) 연결 — 시작/종료 시 deps.init_state/close_state 실행
2. 예외 → 표준 응답 봉투 변환 — 어떤 예외가 나도 envelopes.err 형태의 JSON으로 통일
3. 라우터 등록 — /api/v1 아래에 health, source 엔드포인트를 붙임

실행 예: `uvicorn app.main:app`
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import config
from .deps import close_state, init_state
from .envelopes import ApiError, err
from .routers import health, source


def _build_exception_response(exc: Exception) -> JSONResponse:
    """예외 종류별로 적절한 HTTP 상태 코드와 err() 봉투를 골라 JSON 응답을 만든다.

    - ApiError: 서비스 코드가 의도적으로 던진 예외 → 예외에 담긴 code/status 그대로 사용
    - HTTPException: FastAPI/Starlette 기본 예외 → "HTTP_ERROR" 코드로 래핑
    - RequestValidationError: 요청 본문 검증 실패 → 422 "VALIDATION_ERROR"
    - 그 외: 예상 못 한 버그 → 내부 정보 노출을 막기 위해 고정 메시지의 500
    """
    if isinstance(exc, ApiError):
        status_code = exc.status_code
        payload = err(exc.code, exc.message)
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
        payload = err("HTTP_ERROR", str(exc.detail))
    elif isinstance(exc, RequestValidationError):
        status_code = 422
        payload = err("VALIDATION_ERROR", str(exc))
    else:
        status_code = 500
        payload = err("INTERNAL_SERVER_ERROR", "internal server error")
    return JSONResponse(status_code=status_code, content=payload)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 수명주기 관리: 시작 시 전역 상태 초기화, 종료 시 정리."""
    del app
    await init_state()
    try:
        yield
    finally:
        await close_state()


app = FastAPI(title=config.APP_NAME, lifespan=lifespan)


@app.middleware("http")
async def exception_middleware(request: Request, call_next):
    """모든 요청을 감싸는 최후의 안전망 미들웨어.

    아래의 exception_handler들이 잡지 못하는 경우(예: 다른 미들웨어에서 터진 예외)까지
    잡아서, 어떤 상황에서도 응답이 표준 봉투 형태를 벗어나지 않게 한다.
    """
    try:
        return await call_next(request)
    except Exception as exc:
        return _build_exception_response(exc)


# 아래 4개의 핸들러는 라우트 함수 안에서 발생한 예외를 종류별로 받아
# 전부 _build_exception_response 한 곳으로 모은다.
# (미들웨어와 역할이 겹쳐 보이지만, FastAPI는 라우트 예외를 핸들러에서 먼저 처리하므로
#  두 층을 모두 두어야 모든 경로가 커버된다.)
@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    """서비스 코드가 던진 ApiError를 표준 봉투로 변환."""
    del request
    return _build_exception_response(exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """FastAPI 기본 HTTPException(404 등)을 표준 봉투로 변환."""
    del request
    return _build_exception_response(exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """요청 스키마 검증 실패(422)를 표준 봉투로 변환."""
    del request
    return _build_exception_response(exc)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """처리되지 않은 모든 예외를 500 표준 봉투로 변환."""
    del request
    return _build_exception_response(exc)


# 라우터 등록: 최종 경로는 /api/v1/health..., /api/v1/source/... 형태가 된다.
app.include_router(health.router, prefix=config.API_PREFIX, tags=["health"])
app.include_router(source.router, prefix=config.API_PREFIX, tags=["source"])

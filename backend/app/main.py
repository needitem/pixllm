from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import config
from .deps import close_state, init_state
from .envelopes import ApiError, err
from .routers import health, runs, wiki


def _build_exception_response(exc: Exception) -> JSONResponse:
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
    del app
    await init_state()
    try:
        yield
    finally:
        await close_state()


app = FastAPI(title=config.APP_NAME, lifespan=lifespan)


@app.middleware("http")
async def exception_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        return _build_exception_response(exc)


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    del request
    return _build_exception_response(exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    del request
    return _build_exception_response(exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    del request
    return _build_exception_response(exc)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    del request
    return _build_exception_response(exc)


app.include_router(health.router, prefix=config.API_PREFIX, tags=["health"])
app.include_router(wiki.router, prefix=config.API_PREFIX, tags=["wiki"])
app.include_router(runs.router, prefix=config.API_PREFIX, tags=["runs"])

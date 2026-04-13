from time import perf_counter
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import config
from .core.policy import SecurityPolicy
from .envelopes import err, ApiError
from .deps import init_state, close_state, state
from .metrics import metric_path_label, metrics_registry
from .observability import (
    configure_logger,
    log_event,
    log_exception,
    log_request,
    request_id_from_request,
    request_id_headers,
)
from .services.auth.service import auth_is_enabled, extract_api_session_token, read_access_token
from .routers import (
    auth,
    llm,
    models,
    search,
    conversations,
    prompts,
    knowledge,
    wiki,
    imports,
    health,
    tools,
    tool_runtime,
    pipelines,
    runs,
)



api_logger = configure_logger()


def _build_exception_response(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, ApiError):
        status_code = exc.status_code
        payload = err(exc.code, exc.message)
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
        payload = err("HTTP_ERROR", exc.detail)
    elif isinstance(exc, RequestValidationError):
        status_code = 422
        payload = err("VALIDATION_ERROR", str(exc))
    else:
        status_code = 500
        payload = err("INTERNAL_SERVER_ERROR", "internal server error")
    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers=request_id_headers(request),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_event(api_logger, "app_starting", app_name=config.APP_NAME, api_prefix=config.API_PREFIX)
    await init_state()
    try:
        yield
    finally:
        await close_state()
        log_event(api_logger, "app_stopped", app_name=config.APP_NAME, api_prefix=config.API_PREFIX)


app = FastAPI(title=config.APP_NAME, lifespan=lifespan)

def _extract_api_session_token(request: Request) -> Optional[str]:
    return extract_api_session_token(request)


def _is_session_auth_exempt(path: str) -> bool:
    return SecurityPolicy.is_session_auth_exempt(path)


@app.middleware("http")
async def api_request_middleware(request: Request, call_next):
    request.state.request_id = request_id_from_request(request)
    started_at = perf_counter()
    response = None
    try:
        if auth_is_enabled() and not _is_session_auth_exempt(request.url.path):
            provided = _extract_api_session_token(request)
            if SecurityPolicy.validate_api_session_token(provided):
                request.state.api_session = {"kind": "static", "token_id": "static", "label": "static"}
            else:
                token_payload = await read_access_token(state.redis, provided)
                if token_payload:
                    request.state.api_session = {"kind": "issued", **token_payload}
                else:
                    response = JSONResponse(
                        status_code=401,
                        content=err("UNAUTHORIZED", "invalid or missing api session token"),
                        headers=request_id_headers(request),
                    )
                    return response

        response = await call_next(request)
        return response
    except Exception as exc:
        log_exception(api_logger, request, exc)
        metrics_registry.record_exception(
            method=request.method,
            path=metric_path_label(request),
            error_type=exc.__class__.__name__,
        )
        response = _build_exception_response(request, exc)
        return response
    finally:
        duration_ms = (perf_counter() - started_at) * 1000
        if response is not None:
            response.headers.update(request_id_headers(request))
            metrics_registry.record_http_request(
                method=request.method,
                path=metric_path_label(request),
                status_code=response.status_code,
                duration_ms=duration_ms,
            )
            log_request(
                api_logger,
                request,
                status_code=response.status_code,
                duration_ms=duration_ms,
                api_session=getattr(request.state, "api_session", None),
            )


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return _build_exception_response(request, exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return _build_exception_response(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return _build_exception_response(request, exc)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log_exception(api_logger, request, exc)
    metrics_registry.record_exception(
        method=request.method,
        path=metric_path_label(request),
        error_type=exc.__class__.__name__,
    )
    return _build_exception_response(request, exc)


app.include_router(auth.router, prefix=config.API_PREFIX, tags=["auth"])
app.include_router(health.router, prefix=config.API_PREFIX, tags=["health"])
app.include_router(llm.router, prefix=config.API_PREFIX, tags=["llm"])
app.include_router(models.router, prefix=config.API_PREFIX, tags=["models"])
app.include_router(search.router, prefix=config.API_PREFIX, tags=["search"])
app.include_router(conversations.router, prefix=config.API_PREFIX, tags=["conversations"])
app.include_router(prompts.router, prefix=config.API_PREFIX, tags=["prompts"])
app.include_router(knowledge.router, prefix=config.API_PREFIX, tags=["knowledge"])
app.include_router(wiki.router, prefix=config.API_PREFIX, tags=["wiki"])
app.include_router(imports.router, prefix=config.API_PREFIX, tags=["files"])
app.include_router(tools.router, prefix=config.API_PREFIX, tags=["tools"])

app.include_router(tool_runtime.router, prefix=config.API_PREFIX, tags=["tool-api"])
app.include_router(pipelines.router, prefix=config.API_PREFIX, tags=["pipelines"])
app.include_router(runs.router, prefix=config.API_PREFIX, tags=["runs"])

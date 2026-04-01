from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import config
from .core.policy import SecurityPolicy
from .envelopes import err, ApiError
from .deps import init_state, close_state, state
from .services.auth.service import auth_is_enabled, extract_api_session_token, read_access_token
from .routers import (
    auth,
    llm,
    models,
    search,
    conversations,
    prompts,
    knowledge,
    imports,
    health,
    tools,
    tool_runtime,
    pipelines,
    runs,
)




@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_state()
    yield
    await close_state()


app = FastAPI(title=config.APP_NAME, lifespan=lifespan)

def _extract_api_session_token(request: Request) -> Optional[str]:
    return extract_api_session_token(request)


def _is_session_auth_exempt(path: str) -> bool:
    return SecurityPolicy.is_session_auth_exempt(path)


@app.middleware("http")
async def api_session_auth_middleware(request: Request, call_next):
    if not auth_is_enabled() or _is_session_auth_exempt(request.url.path):
        return await call_next(request)

    provided = _extract_api_session_token(request)
    if SecurityPolicy.validate_api_session_token(provided):
        request.state.api_session = {"kind": "static", "token_id": "static", "label": "static"}
        return await call_next(request)

    token_payload = await read_access_token(state.redis, provided)
    if token_payload:
        request.state.api_session = {"kind": "issued", **token_payload}
        return await call_next(request)

    return JSONResponse(
        status_code=401,
        content=err("UNAUTHORIZED", "invalid or missing api session token"),
    )


@app.exception_handler(ApiError)
async def api_error_handler(_, exc: ApiError):
    return JSONResponse(status_code=exc.status_code, content=err(exc.code, exc.message))


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=err("HTTP_ERROR", exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    return JSONResponse(status_code=422, content=err("VALIDATION_ERROR", str(exc)))


app.include_router(auth.router, prefix=config.API_PREFIX, tags=["auth"])
app.include_router(health.router, prefix=config.API_PREFIX, tags=["health"])
app.include_router(llm.router, prefix=config.API_PREFIX, tags=["llm"])
app.include_router(models.router, prefix=config.API_PREFIX, tags=["models"])
app.include_router(search.router, prefix=config.API_PREFIX, tags=["search"])
app.include_router(conversations.router, prefix=config.API_PREFIX, tags=["conversations"])
app.include_router(prompts.router, prefix=config.API_PREFIX, tags=["prompts"])
app.include_router(knowledge.router, prefix=config.API_PREFIX, tags=["knowledge"])
app.include_router(imports.router, prefix=config.API_PREFIX, tags=["files"])
app.include_router(tools.router, prefix=config.API_PREFIX, tags=["tools"])

app.include_router(tool_runtime.router, prefix=config.API_PREFIX, tags=["tool-api"])
app.include_router(pipelines.router, prefix=config.API_PREFIX, tags=["pipelines"])
app.include_router(runs.router, prefix=config.API_PREFIX, tags=["runs"])

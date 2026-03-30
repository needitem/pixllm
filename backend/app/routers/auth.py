from fastapi import APIRouter, Request, Depends

from ..deps import get_redis, state
from ..envelopes import ApiError, ok
from ..schemas.auth import IssueSessionTokenRequest, RevokeSessionTokenRequest
from ..services.auth.service import (
    extract_api_session_token,
    is_admin_token_valid,
    issue_access_token,
    revoke_access_token,
    revoke_access_token_by_id,
)


router = APIRouter(prefix="/auth")


def _require_admin_request(request: Request) -> str:
    token = extract_api_session_token(request)
    if not is_admin_token_valid(token):
        raise ApiError("UNAUTHORIZED", "invalid or missing admin token", status_code=401)
    return token


def _resolve_redis_dependency(redis):
    if hasattr(redis, "dependency"):
        return state.redis
    return redis if redis is not None else state.redis


@router.post("/token")
async def issue_session_token(payload: IssueSessionTokenRequest, request: Request, redis=Depends(get_redis)):
    _require_admin_request(request)
    redis = _resolve_redis_dependency(redis)
    if redis is None:
        raise ApiError("SERVICE_UNAVAILABLE", "redis unavailable", status_code=503)
    issued = await issue_access_token(
        redis,
        label=payload.label,
        ttl_sec=payload.ttl_sec,
    )
    return ok(issued)


@router.post("/token/revoke")
async def revoke_session_token(payload: RevokeSessionTokenRequest, request: Request, redis=Depends(get_redis)):
    _require_admin_request(request)
    redis = _resolve_redis_dependency(redis)
    if redis is None:
        raise ApiError("SERVICE_UNAVAILABLE", "redis unavailable", status_code=503)
    revoked = await revoke_access_token_by_id(redis, payload.token_id)
    if not revoked:
        raise ApiError("NOT_FOUND", "session token not found", status_code=404)
    return ok({"revoked": payload.token_id})


@router.get("/me")
async def get_current_auth(request: Request):
    auth_context = getattr(request.state, "api_session", None)
    if not auth_context:
        raise ApiError("UNAUTHORIZED", "invalid or missing api session token", status_code=401)
    return ok(auth_context)


@router.delete("/token/current")
async def revoke_current_session_token(request: Request, redis=Depends(get_redis)):
    redis = _resolve_redis_dependency(redis)
    auth_context = getattr(request.state, "api_session", None)
    if not auth_context:
        raise ApiError("UNAUTHORIZED", "invalid or missing api session token", status_code=401)
    if str(auth_context.get("kind") or "") != "issued":
        raise ApiError("BAD_REQUEST", "static api session token cannot be revoked via api", status_code=400)
    token = extract_api_session_token(request)
    revoked = await revoke_access_token(redis, token)
    if not revoked:
        raise ApiError("NOT_FOUND", "session token not found", status_code=404)
    return ok({"revoked": True, "token_id": auth_context.get("token_id")})

import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from ... import config
from ...utils.ids import new_id
from ...utils.time import now_iso


_TOKEN_KEY_PREFIX = "api_session_token:"
_TOKEN_ID_KEY_PREFIX = "api_session_token_id:"


def extract_api_session_token(source: Any) -> str:
    headers = getattr(source, "headers", source) or {}
    auth = str(headers.get("authorization") or headers.get("Authorization") or "").strip()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return str(headers.get("x-api-token") or headers.get("X-Api-Token") or "").strip()


def auth_is_enabled() -> bool:
    return bool(str(config.API_SESSION_TOKEN or "").strip())


def is_admin_token_valid(token: str) -> bool:
    provided = str(token or "").strip()
    if not provided:
        return False
    expected = str(config.API_SESSION_TOKEN or "").strip()
    return bool(expected and hmac.compare_digest(provided, expected))


def session_token_ttl_seconds(requested_ttl_sec: Optional[int]) -> int:
    default_ttl = max(60, int(config.API_SESSION_ACCESS_TTL_SEC or 43200))
    max_ttl = max(default_ttl, int(config.API_SESSION_ACCESS_MAX_TTL_SEC or 604800))
    if requested_ttl_sec is None:
        return default_ttl
    return max(60, min(int(requested_ttl_sec), max_ttl))


def _token_digest(token: str) -> str:
    return hashlib.sha256(str(token or "").encode("utf-8")).hexdigest()


def _token_key_from_digest(digest: str) -> str:
    return f"{_TOKEN_KEY_PREFIX}{digest}"


def _token_key(token: str) -> str:
    return _token_key_from_digest(_token_digest(token))


def _token_id_key(token_id: str) -> str:
    return f"{_TOKEN_ID_KEY_PREFIX}{token_id}"


async def issue_access_token(
    redis,
    *,
    label: str = "",
    ttl_sec: Optional[int] = None,
    permanent: bool = False,
    issued_by: str = "admin",
) -> dict:
    is_permanent = bool(permanent)
    if is_permanent and not bool(config.API_SESSION_ACCESS_ALLOW_PERMANENT):
        raise ValueError("permanent api session tokens are disabled")

    effective_ttl = None if is_permanent else session_token_ttl_seconds(ttl_sec)
    raw_token = secrets.token_urlsafe(32)
    token_id = new_id()
    issued_at = now_iso()
    expires_at = (
        None
        if effective_ttl is None
        else (datetime.now(timezone.utc) + timedelta(seconds=effective_ttl)).isoformat()
    )
    payload = {
        "token_id": token_id,
        "label": str(label or "").strip(),
        "issued_by": str(issued_by or "").strip() or "admin",
        "issued_at": issued_at,
        "expires_at": expires_at,
        "ttl_sec": effective_ttl,
        "permanent": is_permanent,
    }
    token_key = _token_key(raw_token)
    token_id_key = _token_id_key(token_id)
    serialized_payload = json.dumps(payload, ensure_ascii=False)
    if effective_ttl is None:
        await redis.set(token_key, serialized_payload)
        await redis.set(token_id_key, _token_digest(raw_token))
    else:
        await redis.set(token_key, serialized_payload, ex=effective_ttl)
        await redis.set(token_id_key, _token_digest(raw_token), ex=effective_ttl)
    return {
        **payload,
        "access_token": raw_token,
        "token_type": "bearer",
    }


async def read_access_token(redis, token: str) -> Optional[dict]:
    normalized = str(token or "").strip()
    if not normalized or redis is None:
        return None
    raw = await redis.get(_token_key(normalized))
    if not raw:
        return None
    return json.loads(raw)


async def revoke_access_token(redis, token: str) -> bool:
    normalized = str(token or "").strip()
    if not normalized or redis is None:
        return False
    payload = await read_access_token(redis, normalized)
    deleted = await redis.delete(_token_key(normalized))
    if payload:
        await redis.delete(_token_id_key(str(payload.get("token_id") or "").strip()))
    return bool(deleted)


async def revoke_access_token_by_id(redis, token_id: str) -> bool:
    normalized = str(token_id or "").strip()
    if not normalized or redis is None:
        return False
    digest = await redis.get(_token_id_key(normalized))
    if not digest:
        return False
    deleted = await redis.delete(_token_key_from_digest(str(digest)))
    await redis.delete(_token_id_key(normalized))
    return bool(deleted)

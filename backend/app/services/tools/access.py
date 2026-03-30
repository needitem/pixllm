"""
Tool policy session store, Redis-backed and async.

Session data is stored in Redis using two key types per session:
  - Hash: tool_policy:session:{id}  -> context_resolved, search_used, user_id, updated_at
  - Set:  tool_policy:chunks:{id}   -> known doc chunk IDs
  - Set:  tool_policy:paths:{id}    -> known code paths

All keys share the same TTL (TOOL_POLICY_SESSION_TTL_SEC).
Falls back to allow=True / legacy_no_session when Redis is unavailable.
"""

import logging
from typing import Any, Dict, Iterable, List, Optional

from ... import config
from ...core.policy import SecurityPolicy

logger = logging.getLogger(__name__)

_PFX_SESSION = "tool_policy:session:"
_PFX_CHUNKS = "tool_policy:chunks:"
_PFX_PATHS = "tool_policy:paths:"


def _session_key(session_id: str) -> str:
    return f"{_PFX_SESSION}{session_id}"


def _chunks_key(session_id: str) -> str:
    return f"{_PFX_CHUNKS}{session_id}"


def _paths_key(session_id: str) -> str:
    return f"{_PFX_PATHS}{session_id}"


def _ttl() -> int:
    return max(60, int(config.TOOL_POLICY_SESSION_TTL_SEC))


def _session_id_or_none(session_id: Optional[str]) -> Optional[str]:
    raw = str(session_id or "").strip()
    return raw or None


async def _ensure_session(redis, session_id: Optional[str]) -> Optional[str]:
    key = _session_id_or_none(session_id)
    if not key or redis is None:
        return None
    try:
        ttl = _ttl()
        pipe = redis.pipeline(transaction=False)
        pipe.hsetnx(_session_key(key), "context_resolved", "0")
        pipe.hsetnx(_session_key(key), "search_used", "0")
        pipe.expire(_session_key(key), ttl)
        await pipe.execute()
    except Exception as exc:
        logger.warning("tool_policy: Redis _ensure_session failed: %s", exc)
        return None
    return key


async def _get_session_field(redis, session_id: str, field: str) -> Optional[str]:
    try:
        return await redis.hget(_session_key(session_id), field)
    except Exception:
        return None


async def _set_session_fields(redis, session_id: str, **fields) -> None:
    try:
        ttl = _ttl()
        pipe = redis.pipeline(transaction=False)
        pipe.hset(_session_key(session_id), mapping={k: str(v) for k, v in fields.items()})
        pipe.expire(_session_key(session_id), ttl)
        await pipe.execute()
    except Exception as exc:
        logger.warning("tool_policy: Redis _set_session_fields failed: %s", exc)


async def resolve_tool_user_context(
    redis,
    session_id: Optional[str],
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    key = await _ensure_session(redis, session_id)
    if key is None:
        return {"session_id": None, "policy_gate_active": False}
    updates: Dict[str, Any] = {"context_resolved": "1"}
    if user_id:
        updates["user_id"] = user_id
    await _set_session_fields(redis, key, **updates)
    return {"session_id": key, "policy_gate_active": True}





async def register_doc_search(redis, session_id: Optional[str], rows: Iterable[Dict[str, Any]]) -> None:
    key = _session_id_or_none(session_id)
    if not key or redis is None:
        return
    chunk_ids = [str(r.get("chunk_id") or "").strip() for r in rows if str(r.get("chunk_id") or "").strip()]
    if not chunk_ids:
        await _set_session_fields(redis, key, search_used="1")
        return
    try:
        ttl = _ttl()
        pipe = redis.pipeline(transaction=False)
        pipe.sadd(_chunks_key(key), *chunk_ids)
        pipe.expire(_chunks_key(key), ttl)
        pipe.hset(_session_key(key), mapping={"search_used": "1"})
        pipe.expire(_session_key(key), ttl)
        await pipe.execute()
    except Exception as exc:
        logger.warning("tool_policy: register_doc_search failed: %s", exc)


async def register_code_search(
    redis, session_id: Optional[str], rows: Iterable[Dict[str, Any]]
) -> None:
    key = _session_id_or_none(session_id)
    if not key or redis is None:
        return
    paths = [
        str(r.get("path") or "").strip().replace("\\", "/")
        for r in rows
        if str(r.get("path") or "").strip()
    ]
    if not paths:
        await _set_session_fields(redis, key, search_used="1")
        return
    try:
        ttl = _ttl()
        pipe = redis.pipeline(transaction=False)
        pipe.sadd(_paths_key(key), *paths)
        pipe.expire(_paths_key(key), ttl)
        pipe.hset(_session_key(key), mapping={"search_used": "1"})
        pipe.expire(_session_key(key), ttl)
        await pipe.execute()
    except Exception as exc:
        logger.warning("tool_policy: register_code_search failed: %s", exc)


async def register_listed_files(
    redis, session_id: Optional[str], rows: Iterable[Dict[str, Any]]
) -> None:
    await register_code_search(redis, session_id, rows)


async def check_search_gate(redis, session_id: Optional[str]) -> Dict[str, Any]:
    return await SecurityPolicy.check_search_gate(redis, session_id)


async def check_doc_chunk_access(
    redis,
    session_id: Optional[str],
    chunk_ids: List[str],
    explicit_reference: bool,
) -> Dict[str, Any]:
    return await SecurityPolicy.check_doc_chunk_access(redis, session_id, chunk_ids, explicit_reference)


async def check_code_path_access(
    redis,
    session_id: Optional[str],
    path: str,
    explicit_reference: bool,
) -> Dict[str, Any]:
    return await SecurityPolicy.check_code_path_access(redis, session_id, path, explicit_reference)

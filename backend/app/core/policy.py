import hmac
import os
from pathlib import Path
from typing import Optional, Dict, Any, Iterable, List

from .. import config
from ..envelopes import ApiError


class SecurityPolicy:
    """Centralized policy evaluator for system security boundaries."""

    _PRIMARY_SESSION_PREFIX = "tool_policy:session:"
    _PRIMARY_CHUNKS_PREFIX = "tool_policy:chunks:"
    _PRIMARY_PATHS_PREFIX = "tool_policy:paths:"

    @staticmethod
    def is_session_auth_exempt(path: str) -> bool:
        if path in {"/docs", "/redoc", "/openapi.json"}:
            return True
        if path == f"{config.API_PREFIX}/auth/token":
            return True
        if path == f"{config.API_PREFIX}/auth/token/revoke":
            return True
        if path == f"{config.API_PREFIX}/health":
            return True
        if path.startswith(f"{config.API_PREFIX}/health/"):
            return True
        if path == f"{config.API_PREFIX}/metrics":
            return True
        return False

    @staticmethod
    def validate_api_session_token(provided: Optional[str]) -> bool:
        expected = str(config.API_SESSION_TOKEN or "").strip()
        if not expected:
            return False
        if not provided:
            return False
        return hmac.compare_digest(provided, expected)

    @staticmethod
    def require_pipeline_access(token: Optional[str]) -> None:
        if not config.PIPELINE_API_ENABLED:
            raise ApiError("PIPELINE_API_DISABLED", "pipeline api is disabled", status_code=403)
        expected = str(config.PIPELINE_API_TOKEN or "").strip()
        if expected and str(token or "").strip() != expected:
            raise ApiError("PIPELINE_API_FORBIDDEN", "invalid pipeline api token", status_code=403)

    @staticmethod
    def _iter_code_roots(code_tools) -> Iterable[Path]:
        configured_roots = getattr(code_tools, "configured_roots", None)
        if configured_roots is not None:
            for root in configured_roots:
                yield Path(root)
            return

        if isinstance(code_tools, list):
            for cfg in code_tools:
                if not isinstance(cfg, dict) or cfg.get("type") != "local_workspace":
                    continue
                root = cfg.get("root_path")
                if root:
                    yield Path(root)

    @classmethod
    def execute_code_tools_boundary(cls, code_tools, requested_path: str) -> Optional[Path]:
        """Validate that a requested workspace path stays within configured code roots."""
        raw = str(requested_path or "").strip()
        if not raw:
            return None

        candidate = Path(raw)
        roots = [root.resolve() for root in cls._iter_code_roots(code_tools) if root.exists() and root.is_dir()]
        if not roots:
            return None

        if candidate.is_absolute():
            resolved = candidate.resolve()
            if not resolved.exists() or not resolved.is_dir():
                return None
            for root in roots:
                try:
                    resolved.relative_to(root)
                    return resolved
                except ValueError:
                    continue
            return None

        normalized_rel = raw.replace("\\", "/")
        for root in roots:
            resolved = (root / normalized_rel).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                continue
            if resolved.exists() and resolved.is_dir():
                return resolved
        return None

    @staticmethod
    def _session_id_or_none(session_id: Optional[str]) -> Optional[str]:
        raw = str(session_id or "").strip()
        return raw if raw else None

    @staticmethod
    def _paths_key(key: str) -> str:
        return f"{SecurityPolicy._PRIMARY_PATHS_PREFIX}{key}"

    @staticmethod
    def _chunks_key(key: str) -> str:
        return f"{SecurityPolicy._PRIMARY_CHUNKS_PREFIX}{key}"

    @staticmethod
    def _session_key(key: str) -> str:
        return f"{SecurityPolicy._PRIMARY_SESSION_PREFIX}{key}"

    @staticmethod
    async def _get_session_field(redis, key: str, field: str) -> Optional[str]:
        try:
            return await redis.hget(SecurityPolicy._session_key(key), field)
        except Exception:
            return None

    @staticmethod
    async def _read_known_members(redis, *keys: str) -> set[str]:
        known: set[str] = set()
        for member_key in keys:
            try:
                values = await redis.smembers(member_key)
            except Exception:
                values = set()
            for value in values or set():
                if isinstance(value, bytes):
                    known.add(value.decode("utf-8", errors="replace"))
                else:
                    known.add(str(value))
        return known

    @staticmethod
    async def _ensure_session(redis, key: str) -> None:
        try:
            ttl = max(60, int(config.TOOL_POLICY_SESSION_TTL_SEC or 60))
            exists = await redis.exists(SecurityPolicy._session_key(key))
            if not exists:
                await redis.hset(
                    SecurityPolicy._session_key(key),
                    mapping={
                        "id": key,
                        "search_used": "0",
                        "context_resolved": "0",
                    },
                )
                await redis.expire(SecurityPolicy._session_key(key), ttl)
        except Exception:
            pass

    @classmethod
    async def check_search_gate(cls, redis, session_id: Optional[str]) -> Dict[str, Any]:
        key = cls._session_id_or_none(session_id)
        if key is None or redis is None:
            if config.TOOL_POLICY_STRICT:
                return {"allow": False, "reason": "context_required"}
            return {"allow": True, "reason": "no_session"}

        await cls._ensure_session(redis, key)
        resolved = await cls._get_session_field(redis, key, "context_resolved")
        if resolved != "1":
            return {"allow": False, "reason": "context_required"}
        return {"allow": True, "reason": "ok"}

    @classmethod
    async def check_doc_chunk_access(
        cls,
        redis,
        session_id: Optional[str],
        chunk_ids: List[str],
        explicit_reference: bool,
    ) -> Dict[str, Any]:
        cleaned = [str(cid).strip() for cid in chunk_ids if str(cid).strip()]
        if not cleaned:
            return {"allow": True, "reason": "empty_chunks", "unknown_chunk_ids": []}

        if explicit_reference:
            return {"allow": True, "reason": "explicit_reference", "unknown_chunk_ids": []}

        key = cls._session_id_or_none(session_id)
        if key is None or redis is None:
            if config.TOOL_POLICY_STRICT:
                return {"allow": False, "reason": "context_required", "unknown_chunk_ids": cleaned}
            return {"allow": True, "reason": "no_session", "unknown_chunk_ids": []}

        await cls._ensure_session(redis, key)
        resolved = await cls._get_session_field(redis, key, "context_resolved")
        if resolved != "1":
            return {"allow": False, "reason": "context_required", "unknown_chunk_ids": cleaned}

        search_used = await cls._get_session_field(redis, key, "search_used")
        if search_used != "1":
            return {"allow": False, "reason": "search_required", "unknown_chunk_ids": cleaned}

        known = await cls._read_known_members(redis, cls._chunks_key(key))

        unknown = [cid for cid in cleaned if cid not in known]
        return {
            "allow": len(unknown) == 0,
            "reason": "unknown_chunk_ids" if unknown else "ok",
            "unknown_chunk_ids": unknown,
        }

    @classmethod
    async def check_code_path_access(
        cls,
        redis,
        session_id: Optional[str],
        path: str,
        explicit_reference: bool,
    ) -> Dict[str, Any]:
        if explicit_reference:
            return {"allow": True, "reason": "explicit_reference", "unknown_paths": []}

        clean_path = str(path or "").strip().replace("\\", "/")
        key = cls._session_id_or_none(session_id)

        if key is None or redis is None:
            if config.TOOL_POLICY_STRICT:
                return {"allow": False, "reason": "context_required", "unknown_paths": [clean_path] if clean_path else []}
            return {"allow": True, "reason": "no_session", "unknown_paths": []}

        await cls._ensure_session(redis, key)
        resolved = await cls._get_session_field(redis, key, "context_resolved")
        if resolved != "1":
            return {"allow": False, "reason": "context_required", "unknown_paths": [clean_path] if clean_path else []}

        search_used = await cls._get_session_field(redis, key, "search_used")
        if search_used != "1":
            return {"allow": False, "reason": "search_required", "unknown_paths": [clean_path] if clean_path else []}

        if not clean_path:
            return {"allow": True, "reason": "ok", "unknown_paths": []}

        known_paths = await cls._read_known_members(redis, cls._paths_key(key))
        is_member = clean_path in known_paths

        unknown = [] if is_member else [clean_path]
        return {
            "allow": len(unknown) == 0,
            "reason": "unknown_path" if unknown else "ok",
            "unknown_paths": unknown,
        }

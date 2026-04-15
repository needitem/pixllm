import asyncio
import urllib.request
import shutil
import inspect
from types import SimpleNamespace
from pathlib import Path
from datetime import datetime, timezone

import redis
try:
    from minio import Minio
except Exception:  # pragma: no cover - optional in lightweight tests
    Minio = object
try:
    from qdrant_client import QdrantClient
except Exception:  # pragma: no cover - optional in lightweight tests
    QdrantClient = object

from ... import config
from ...utils.health import aggregate_status


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_liveness_response() -> dict:
    return {
        "status": "ok",
        "service": config.APP_NAME,
        "checked_at": _timestamp(),
    }


def check_http(url: str, timeout: int = 2) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


async def _maybe_await(value):
    if inspect.isawaitable(value):
        return await value
    return value


async def build_health_response(
    state_obj=None,
    *,
    redis=None,
    minio=None,
    search_svc=None,
    embed_model=None,
    vllm_client=None,
    code_tools=None,
) -> dict:
    if state_obj is not None:
        redis = redis if redis is not None else getattr(state_obj, "redis", None)
        minio = minio if minio is not None else getattr(state_obj, "minio", None)
        search_svc = search_svc if search_svc is not None else getattr(state_obj, "search_svc", None)
        embed_model = embed_model if embed_model is not None else getattr(state_obj, "embed_model", None)
        vllm_client = vllm_client if vllm_client is not None else getattr(state_obj, "vllm_client", None)
        code_tools = code_tools if code_tools is not None else getattr(state_obj, "code_tools", None)

    components = {}

    try:
        qdrant = getattr(search_svc, "qdrant", None) if search_svc else None
        if qdrant is None:
            raise RuntimeError("qdrant unavailable")
        collections = await _maybe_await(qdrant.get_collections()) if hasattr(qdrant, "get_collections") else None
        collection_count = len(getattr(collections, "collections", []) or [])
        components["qdrant"] = {"status": "ok", "collection_count": collection_count}
    except Exception:
        components["qdrant"] = {"status": "error"}

    components["llm"] = {
        "status": "ok" if check_http(f"{config.VLLM_URL}/v1/models") else "error",
        "model": config.VLLM_MODEL,
        "url": config.VLLM_URL,
    }

    if code_tools is not None:
        try:
            status_payload = code_tools.status() if hasattr(code_tools, "status") else {}
        except Exception:
            status_payload = {}
        status = str(status_payload.get("status") or "ok")
        components["code_tools"] = {"status": status or "ok", **status_payload}
    elif config.CODE_TOOL_ENABLED:
        rg_ok = bool(shutil.which("rg"))
        roots = [str(Path(p)) for p in config.effective_code_search_roots()]
        available = [p for p in roots if Path(p).exists() and Path(p).is_dir()]
        components["code_tools"] = {
            "status": "ok" if (rg_ok and len(available) > 0) else "error",
            "rg": "ok" if rg_ok else "error",
            "roots_available": available,
        }
    else:
        components["code_tools"] = {"status": "disabled"}

    try:
        redis_client = redis
        if redis_client is None:
            raise RuntimeError("redis unavailable")
        await _maybe_await(redis_client.ping())
        components["redis"] = {"status": "ok"}
    except Exception:
        components["redis"] = {"status": "error"}

    try:
        if minio is None:
            raise RuntimeError("minio unavailable")
        bucket_exists = await _maybe_await(minio.bucket_exists(config.MINIO_BUCKET))
        components["minio"] = {"status": "ok" if bucket_exists else "error", "bucket": config.MINIO_BUCKET}
    except Exception:
        components["minio"] = {"status": "error"}

    embedding_model = (
        getattr(embed_model, "model_name_or_path", None)
        or getattr(embed_model, "model_name", None)
        or config.EMBEDDING_MODEL
    )

    return {
        "status": aggregate_status(components),
        "service": config.APP_NAME,
        "components": components,
        "embedding_model": embedding_model,
        "checked_at": _timestamp(),
    }


async def build_readiness_response(**kwargs) -> dict:
    payload = await build_health_response(**kwargs)
    return {
        **payload,
        "ready": str(payload.get("status") or "") == "ok",
    }


def get_health():
    search_svc = SimpleNamespace(qdrant=QdrantClient(url=config.QDRANT_URL))
    try:
        search_svc.qdrant.get_collections = search_svc.qdrant.get_collections
    except Exception:
        pass

    return asyncio.run(build_health_response(
        redis=redis.Redis.from_url(config.REDIS_URL),
        minio=Minio(
            config.MINIO_ENDPOINT,
            access_key=config.MINIO_ACCESS_KEY,
            secret_key=config.MINIO_SECRET_KEY,
            secure=False,
        ),
        search_svc=search_svc,
        embed_model=SimpleNamespace(model_name_or_path=config.EMBEDDING_MODEL),
        code_tools=None,
    ))

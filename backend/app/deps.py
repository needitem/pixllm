import json
import logging
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis_async
from minio import Minio

try:
    from qdrant_client.models import Distance, VectorParams, SparseVectorParams, SparseIndexParams
except Exception:  # pragma: no cover - optional in lightweight test environments
    Distance = None
    VectorParams = None
    SparseVectorParams = None
    SparseIndexParams = None

from FlagEmbedding import BGEM3FlagModel
import openai

from . import config
from .services.tools.codebase import CodeToolService
from .services.tools.workspace_sync import restore_import_code_workspace
from .core.orchestration import OrchestrationPolicy
from .services.search.service import SearchService


logger = logging.getLogger(__name__)


async def _recover_stale_indexing_files(redis_client: redis_async.Redis):
    try:
        ids = list(await redis_client.smembers("file:index"))
    except Exception:
        logger.warning("Failed to read file index during stale recovery", exc_info=True)
        return

    recovered = 0
    for fid in ids:
        key = f"file:{fid}"
        try:
            raw = await redis_client.get(key)
            if not raw:
                continue
            payload = json.loads(raw)
            if payload.get("status") != "indexing":
                continue
            payload["status"] = "failed"
            payload["error_message"] = "Indexing interrupted by restart. Please retry upload."
            await redis_client.set(key, json.dumps(payload))
            recovered += 1
        except Exception:
            logger.warning("Failed stale recovery for file_id=%s", fid, exc_info=True)

    if recovered:
        logger.warning("Recovered %s stale indexing file(s) to failed status", recovered)


async def _recover_stale_import_jobs(redis_client: redis_async.Redis):
    try:
        job_ids = list(await redis_client.smembers("import_job:index"))
    except Exception:
        logger.warning("Failed to read import index during stale recovery", exc_info=True)
        return

    recovered = 0
    for job_id in job_ids:
        key = f"import_job:{job_id}"
        try:
            raw = await redis_client.get(key)
            if not raw:
                continue
            payload = json.loads(raw)
            status = str(payload.get("status") or "").strip().lower()
            if status not in {"queued", "running"}:
                continue
            payload["status"] = "failed"
            payload["finished_at"] = payload.get("finished_at") or datetime.now(timezone.utc).isoformat()
            payload["error_message"] = "Import interrupted by restart. Please retry import job."
            await redis_client.set(key, json.dumps(payload))
            recovered += 1
        except Exception:
            logger.warning("Failed stale recovery for import_job=%s", job_id, exc_info=True)

    if recovered:
        logger.warning("Recovered %s stale import job(s) to failed status", recovered)


class AppState:
    redis: Optional[redis_async.Redis] = None
    minio: Optional[Minio] = None
    search_svc: Optional[SearchService] = None
    embed_model: Optional[BGEM3FlagModel] = None
    vllm_client: Optional[openai.OpenAI] = None
    orchestration_policy: Optional[OrchestrationPolicy] = None
    code_tools: Optional[CodeToolService] = None


state = AppState()

async def init_state():
    if not str(config.MINIO_SECRET_KEY or "").strip():
        logger.warning("MINIO_SECRET_KEY is empty; object storage access may fail")

    state.redis = redis_async.from_url(config.REDIS_URL, decode_responses=True)
    await _recover_stale_indexing_files(state.redis)
    await _recover_stale_import_jobs(state.redis)
    state.minio = Minio(
        config.MINIO_ENDPOINT,
        access_key=config.MINIO_ACCESS_KEY,
        secret_key=config.MINIO_SECRET_KEY,
        secure=False,
    )
    if not state.minio.bucket_exists(config.MINIO_BUCKET):
        state.minio.make_bucket(config.MINIO_BUCKET)

    state.search_svc = SearchService(
        qdrant_url=config.QDRANT_URL,
    )
    if all(x is not None for x in (Distance, VectorParams, SparseVectorParams, SparseIndexParams)):
        try:
            collections = state.search_svc.qdrant.get_collections().collections
            names = {c.name for c in collections}
            if config.RAG_DEFAULT_COLLECTION not in names:
                state.search_svc.qdrant.create_collection(
                    collection_name=config.RAG_DEFAULT_COLLECTION,
                    vectors_config={"dense": VectorParams(size=1024, distance=Distance.COSINE)},
                    sparse_vectors_config={"sparse": SparseVectorParams(index=SparseIndexParams())},
                )
        except Exception:
            logger.warning("Failed to ensure default Qdrant collection", exc_info=True)
    if config.IMPORT_CODE_RESTORE_ON_START:
        try:
            restored = await restore_import_code_workspace(
                state.redis,
                state.minio,
                config.MINIO_BUCKET,
                config.IMPORT_CODE_ROOT,
            )
            logger.info("Restored imported code workspace", extra=restored)
        except Exception:
            logger.warning("Failed to restore imported code workspace", exc_info=True)
    embedding_device = str(config.EMBEDDING_DEVICE or "cpu").strip() or "cpu"
    embedding_use_fp16 = bool(config.EMBEDDING_USE_FP16)
    try:
        state.embed_model = BGEM3FlagModel(
            config.EMBEDDING_MODEL,
            use_fp16=embedding_use_fp16,
            device=embedding_device,
        )
    except Exception as exc:
        logger.warning(
            "Failed to initialize embedding model on configured device; falling back to CPU",
            extra={"embedding_device": embedding_device, "error": str(exc)[:240]},
        )
        state.embed_model = BGEM3FlagModel(config.EMBEDDING_MODEL, use_fp16=False, device="cpu")

    state.vllm_client = openai.OpenAI(
        base_url=f"{config.VLLM_URL}/v1",
        api_key="EMPTY",
    )
    state.orchestration_policy = OrchestrationPolicy(config.ORCHESTRATION_CONFIG_DIR)

    if config.CODE_TOOL_ENABLED:
        state.code_tools = CodeToolService(
            roots=config.effective_code_search_roots(),
            max_results=config.CODE_SEARCH_MAX_RESULTS,
            context_lines=config.CODE_SEARCH_CONTEXT_LINES,
            max_file_bytes=config.CODE_SEARCH_MAX_FILE_BYTES,
        )
    else:
        state.code_tools = None

async def close_state():
    if state.redis:
        await state.redis.close()


def get_redis() -> Optional[redis_async.Redis]:
    return state.redis


def get_minio() -> Optional[Minio]:
    return state.minio


def get_search_svc() -> Optional[SearchService]:
    return state.search_svc


def get_embed_model() -> Optional[BGEM3FlagModel]:
    return state.embed_model


def get_vllm_client() -> Optional[openai.OpenAI]:
    return state.vllm_client


def get_orchestrator() -> Optional[OrchestrationPolicy]:
    return state.orchestration_policy


def get_code_tools() -> Optional[CodeToolService]:
    return state.code_tools

import os
import json
import secrets
from pathlib import PurePosixPath


def env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def env_json(name: str, default):
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def env_list(name: str, default_csv: str) -> list[str]:
    value = os.getenv(name, default_csv)
    return [item.strip() for item in str(value).split(",") if item.strip()]


APP_NAME = "PIXLLM RAG API"
API_PREFIX = "/api/v1"

# External services.
QDRANT_URL = env("QDRANT_URL", "http://pixllm-qdrant:6333")
REDIS_URL = env("REDIS_URL", "redis://pixllm-redis:6379/0")
MINIO_ENDPOINT = env("MINIO_ENDPOINT", "pixllm-minio:9000")
MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY", "pixllm")
MINIO_SECRET_KEY = env("MINIO_SECRET_KEY", "")
MINIO_BUCKET = env("MINIO_BUCKET", "documents")
VLLM_URL = env("VLLM_URL", "http://vllm:8000")
VLLM_MODEL = env("VLLM_MODEL", "Qwen/Qwen3.5-27B")

# Embedding.
EMBEDDING_MODEL = env("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DEVICE = env("EMBEDDING_DEVICE", "cuda")
EMBEDDING_USE_FP16 = env_bool("EMBEDDING_USE_FP16", True)
EMBEDDING_BATCH_SIZE = env_int("EMBEDDING_BATCH_SIZE", 64)
RAG_DEFAULT_COLLECTION = env("RAG_DEFAULT_COLLECTION", "documents")

# Code retrieval tools.
CODE_TOOL_ENABLED = env_bool("CODE_TOOL_ENABLED", True)
CODE_SEARCH_ROOTS = env_list("CODE_SEARCH_ROOTS", "")
CODE_SEARCH_EXCLUDE_GLOBS = env_list(
    "CODE_SEARCH_EXCLUDE_GLOBS",
    "!.git,!node_modules,!dist,!build,!out,!vendor,!backend/tests/**,!app/tests/**,!*.min.js,!*.min.css,!*.lock",
)
CODE_SEARCH_MAX_RESULTS = env_int("CODE_SEARCH_MAX_RESULTS", 50)
CODE_SEARCH_CONTEXT_LINES = env_int("CODE_SEARCH_CONTEXT_LINES", 10)
CODE_SEARCH_MAX_FILE_BYTES = env_int("CODE_SEARCH_MAX_FILE_BYTES", 1500000)
CODE_SEARCH_TIMEOUT_SEC = env_int("CODE_SEARCH_TIMEOUT_SEC", 6)
TOOL_POLICY_STRICT = env_bool("TOOL_POLICY_STRICT", True)
TOOL_POLICY_SESSION_TTL_SEC = env_int("TOOL_POLICY_SESSION_TTL_SEC", 1800)
TOOL_POLICY_SESSION_MAX_ITEMS = env_int("TOOL_POLICY_SESSION_MAX_ITEMS", 5000)

# Pipeline API.
PIPELINE_API_ENABLED = env_bool("PIPELINE_API_ENABLED", True)
_generated_pipeline_token = secrets.token_urlsafe(32)
PIPELINE_API_TOKEN = env("PIPELINE_API_TOKEN", _generated_pipeline_token)
PIPELINE_JOB_HEARTBEAT_SECONDS = env_int("PIPELINE_JOB_HEARTBEAT_SECONDS", 10)
PIPELINE_JOB_STALE_SECONDS = env_int("PIPELINE_JOB_STALE_SECONDS", 120)
_generated_session_token = secrets.token_urlsafe(32)
API_SESSION_TOKEN = env("API_SESSION_TOKEN", _generated_session_token)
API_SESSION_ACCESS_TTL_SEC = env_int("API_SESSION_ACCESS_TTL_SEC", 43200)
API_SESSION_ACCESS_MAX_TTL_SEC = env_int("API_SESSION_ACCESS_MAX_TTL_SEC", 604800)

# Repository sync imports (TFS/SVN).
IMPORT_DOCS_ROOT = env("IMPORT_DOCS_ROOT", "/workspace_host/pixoneer_project")
IMPORT_CODE_ROOT = env("IMPORT_CODE_ROOT", "/workspace_host/pixoneer_source")
IMPORT_CODE_RESTORE_ON_START = env_bool("IMPORT_CODE_RESTORE_ON_START", True)
SVN_BIN = env("SVN_BIN", "svn")
MSBUILD_BIN = env("MSBUILD_BIN", "msbuild")
DOTNET_BIN = env("DOTNET_BIN", "dotnet")
CMAKE_BIN = env("CMAKE_BIN", "cmake")
NINJA_BIN = env("NINJA_BIN", "ninja")
TFS_DOCS_SYNC_COMMAND = env("TFS_DOCS_SYNC_COMMAND", "")


def effective_code_search_roots() -> list[str]:
    import_root = str(IMPORT_CODE_ROOT or "").strip().replace("\\", "/")
    roots: list[str] = []
    seen = set()
    for raw in [IMPORT_CODE_ROOT, *CODE_SEARCH_ROOTS]:
        value = str(raw or "").strip().replace("\\", "/")
        if not value or value in seen:
            continue
        if import_root:
            candidate_parts = PurePosixPath(value).parts
            import_parts = PurePosixPath(import_root).parts
            if candidate_parts[: len(import_parts)] != import_parts:
                continue
        seen.add(value)
        roots.append(value)
    return roots

# Orchestration/runtime.
ORCHESTRATION_CONFIG_DIR = env("ORCHESTRATION_CONFIG_DIR", ".profiles")
CHAT_CODE_DEFAULT_REPO = env("CHAT_CODE_DEFAULT_REPO", "")
CHAT_TOOL_MAX_CHARS = env_int("CHAT_TOOL_MAX_CHARS", 5000)
CHAT_TOOL_MAX_LINE_SPAN = env_int("CHAT_TOOL_MAX_LINE_SPAN", 220)
CHAT_TOOL_DOC_OPEN_LIMIT = env_int("CHAT_TOOL_DOC_OPEN_LIMIT", 10)
CHAT_TOOL_CODE_MAX_WINDOWS = env_int("CHAT_TOOL_CODE_MAX_WINDOWS", 12)
INTENT_LLM_MAX_TOKENS = env_int("INTENT_LLM_MAX_TOKENS", 96)
INTENT_LLM_TEMPERATURE = env_float("INTENT_LLM_TEMPERATURE", 0.0)
INTENT_LLM_CONFIDENCE_THRESHOLD = env_float("INTENT_LLM_CONFIDENCE_THRESHOLD", 0.15)


# Usage-code expansion controls.
CODE_USAGE_EXPANSION_TRIGGER_MAX_MATCHES = env_int("CODE_USAGE_EXPANSION_TRIGGER_MAX_MATCHES", 8)
CODE_USAGE_EXPANSION_MAX_QUERIES = env_int("CODE_USAGE_EXPANSION_MAX_QUERIES", 0)

# Conversations.
MAX_CONVERSATION_MESSAGES = int(env("MAX_CONVERSATION_MESSAGES", "20"))
CHAT_CONTROL_MESSAGE_PREFIXES = env_json(
    "CHAT_CONTROL_MESSAGE_PREFIXES",
    ["[analyze-mode]", "[search-mode]"],
)
CHAT_CONTROL_MESSAGE_CONTAINS = env_json(
    "CHAT_CONTROL_MESSAGE_CONTAINS",
    ["analysis mode.", "maximize search effort"],
)

# Imports / uploads.
FILE_UPLOAD_MAX_BYTES = env_int("FILE_UPLOAD_MAX_BYTES", 50 * 1024 * 1024)
FILE_UPLOAD_READ_CHUNK_BYTES = env_int("FILE_UPLOAD_READ_CHUNK_BYTES", 1024 * 1024)
FILE_INDEXING_STALE_SECONDS = env_int("FILE_INDEXING_STALE_SECONDS", 0)

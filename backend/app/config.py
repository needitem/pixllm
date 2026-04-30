import os
from pathlib import Path


def env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


APP_NAME = env("PIXLLM_APP_NAME", "PIXLLM Source API")
API_PREFIX = env("PIXLLM_API_PREFIX", "/api/v1")
SOURCE_DATA_DIR = env("PIXLLM_SOURCE_DATA_DIR", ".profiles")
SOURCE_RUNTIME_DIR = env("SOURCE_RUNTIME_DIR", str(Path(SOURCE_DATA_DIR) / "source"))
LLM_BASE_URL = env("PIXLLM_LLM_BASE_URL", "http://192.168.2.212:8000/v1")
DEFAULT_MODEL = env("PIXLLM_DEFAULT_MODEL", "Qwen/Qwen3.6-27B")
REWRITE_LLM_BASE_URL = env("PIXLLM_REWRITE_LLM_BASE_URL", "http://192.168.2.238:8002/v1")
REWRITE_MODEL = env("PIXLLM_REWRITE_MODEL", "workflow-rewrite-qwen")

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SOURCE_DATA_ROOT = _BACKEND_ROOT / SOURCE_DATA_DIR
RAW_SOURCE_ROOT = env(
    "RAW_SOURCE_ROOT",
    str((_SOURCE_DATA_ROOT / "raw_source" / "source").resolve()),
)

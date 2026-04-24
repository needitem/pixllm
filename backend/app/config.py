import os
from pathlib import Path


def env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        return int(str(value).strip())
    except Exception:
        return default


APP_NAME = env("PIXLLM_APP_NAME", "PIXLLM Wiki API")
API_PREFIX = env("PIXLLM_API_PREFIX", "/api/v1")
WIKI_PROFILE_DIR = env("WIKI_PROFILE_DIR", ".profiles")
ANSWER_MODE = env("PIXLLM_ANSWER_MODE", "wiki-only")
WORKFLOW_CLASSIFIER_URL = env("WORKFLOW_CLASSIFIER_URL", "")
WORKFLOW_CLASSIFIER_MODEL = env("WORKFLOW_CLASSIFIER_MODEL", "")
WORKFLOW_FAMILY_RANK_MARGIN = max(0, env_int("WORKFLOW_FAMILY_RANK_MARGIN", 18))

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
RAW_SOURCE_ROOT = env(
    "RAW_SOURCE_ROOT",
    str((_BACKEND_ROOT / WIKI_PROFILE_DIR / "wiki" / "raw_source" / "source").resolve()),
)

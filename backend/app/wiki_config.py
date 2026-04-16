"""Centralized wiki/runtime configuration loader."""

import os
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


_CONFIG_CACHE: Dict[str, Any] = {}


def _profile_root() -> Path:
    base = Path(__file__).resolve().parents[1]  # backend/
    raw = str(os.getenv("WIKI_PROFILE_DIR") or ".profiles").strip() or ".profiles"
    root = Path(raw)
    if root.is_absolute():
        return root
    return base / root


def _find_config_path() -> Path:
    return _profile_root() / "wiki_config.yaml"


def _load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def load() -> Dict[str, Any]:
    global _CONFIG_CACHE
    if _CONFIG_CACHE:
        return _CONFIG_CACHE
    _CONFIG_CACHE = _load_yaml(_find_config_path())
    return _CONFIG_CACHE


def _get(section: str, key: str, default: Any = None) -> Any:
    cfg = load()
    return cfg.get(section, {}).get(key, default)


def _coerce_like(value: Any, default: Any) -> Any:
    if isinstance(default, bool):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"1", "true", "yes", "on"}:
                return True
            if lowered in {"0", "false", "no", "off"}:
                return False
        return default
    if isinstance(default, int) and not isinstance(default, bool):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
    if isinstance(default, float):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    if isinstance(default, str):
        return str(value)
    return value if isinstance(value, type(default)) else default


def heuristics_weights(name: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
    raw = load().get("heuristics", {}).get(name, {})
    merged = dict(defaults)
    if not isinstance(raw, dict):
        return merged
    for key, default in defaults.items():
        if key in raw:
            merged[key] = _coerce_like(raw.get(key), default)
    return merged


def routing_doc_first_response_types() -> List[str]:
    return list(_get("routing", "doc_first_response_types", ["doc_lookup"]))


def retrieval_query_rewrite_enabled() -> bool:
    v = os.getenv("CHAT_QUERY_REWRITE_ENABLED")
    if v is not None and str(v).strip() != "":
        return str(v).strip().lower() in {"1", "true", "yes", "on"}
    return bool(_get("retrieval", "query_rewrite_enabled", True))


def retrieval_query_rewrite_max_candidates() -> int:
    v = os.getenv("CHAT_QUERY_REWRITE_MAX_CANDIDATES")
    if v is not None and str(v).strip() != "":
        try:
            return max(1, int(v))
        except ValueError:
            pass
    return max(1, int(_get("retrieval", "query_rewrite_max_candidates", 3)))

"""Centralized RAG configuration loader."""

import os
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


_CONFIG_CACHE: Dict[str, Any] = {}


def _find_config_path() -> Path:
    base = Path(__file__).resolve().parents[1]  # backend/
    return base / ".profiles" / "rag_config.yaml"


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


def reload() -> Dict[str, Any]:
    global _CONFIG_CACHE
    _CONFIG_CACHE = {}
    return load()


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


def routing_probe_enabled() -> bool:
    v = os.getenv("CHAT_ROUTER_PROBE_ENABLED")
    if v is not None and str(v).strip() != "":
        return str(v).strip().lower() in {"1", "true", "yes", "on"}
    return bool(_get("routing", "probe_enabled", True))


def routing_probe_ratio() -> float:
    v = os.getenv("CHAT_ROUTER_PROBE_RATIO")
    if v:
        try:
            return float(v)
        except ValueError:
            pass
    return float(_get("routing", "probe_ratio", 1.35))


def routing_code_first_response_types() -> List[str]:
    return list(
        _get(
            "routing",
            "code_first_response_types",
            [
                "code_explain",
                "code_review",
                "bug_fix",
                "code_generate",
                "refactor",
                "troubleshooting",
                "design_review",
                "compare",
                "migration",
                "api_lookup",
            ],
        )
    )


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


def context_doc_limit(response_type: str = "general") -> int:
    return int(_get("context", "doc_limit", 5))


def context_code_limit(response_type: str = "general") -> int:
    return int(_get("context", "code_limit", 6))


def react_max_rounds() -> int:
    v = os.getenv("CHAT_RUNTIME_MAX_TOOL_ROUNDS")
    if v:
        try:
            return int(v)
        except ValueError:
            pass
    return int(_get("react", "max_rounds", 3))


def react_max_tool_calls() -> int:
    v = os.getenv("CHAT_RUNTIME_MAX_TOOL_CALLS")
    if v:
        try:
            return int(v)
        except ValueError:
            pass
    return int(_get("react", "max_tool_calls", 8))


def react_timeout_sec() -> int:
    """Max seconds for the entire ReAct loop. 0 = no timeout.

    Set CHAT_REACT_TIMEOUT_SEC=0 to disable, or rag_config.yaml react.timeout_sec: 0.
    Defaults to 60 seconds.
    """
    v = os.getenv("CHAT_REACT_TIMEOUT_SEC")
    if v is not None and str(v).strip() != "":
        try:
            return max(0, int(v))
        except ValueError:
            pass
    return int(_get("react", "timeout_sec", 60))


def react_prepare_timeout_sec() -> int:
    """Max seconds for request preparation/classification. 0 = no timeout."""
    v = os.getenv("CHAT_REACT_PREPARE_TIMEOUT_SEC")
    if v is not None and str(v).strip() != "":
        try:
            return max(0, int(v))
        except ValueError:
            pass
    return int(_get("react", "prepare_timeout_sec", 20))


def react_retrieve_timeout_sec() -> int:
    """Max seconds for the retrieval/evidence-building stage. 0 = no timeout."""
    v = os.getenv("CHAT_REACT_RETRIEVE_TIMEOUT_SEC")
    if v is not None and str(v).strip() != "":
        try:
            return max(0, int(v))
        except ValueError:
            pass
    return int(_get("react", "retrieve_timeout_sec", 45))


def react_answer_timeout_sec() -> int:
    """Max seconds for the final answer synthesis stage. 0 = no timeout."""
    v = os.getenv("CHAT_REACT_ANSWER_TIMEOUT_SEC")
    if v is not None and str(v).strip() != "":
        try:
            return max(0, int(v))
        except ValueError:
            pass
    return int(_get("react", "answer_timeout_sec", 120))


def evidence_threshold() -> float:
    """Minimum evidence score [0..1] to produce a direct answer.

    Below this threshold, the evidence_policy() determines the response style.
    Set CHAT_EVIDENCE_THRESHOLD or rag_config.yaml evidence.threshold.
    """
    v = os.getenv("CHAT_EVIDENCE_THRESHOLD")
    if v:
        try:
            return float(v)
        except ValueError:
            pass
    return float(_get("evidence", "threshold", 0.4))


def evidence_policy() -> str:
    """Policy when evidence is below threshold: 'ask' | 'constrained' | 'reject'.

    Set CHAT_EVIDENCE_POLICY or rag_config.yaml evidence.policy.
    """
    v = os.getenv("CHAT_EVIDENCE_POLICY")
    if v and str(v).strip() in {"ask", "constrained", "reject"}:
        return str(v).strip()
    raw = str(_get("evidence", "policy", "ask") or "ask").strip().lower()
    return raw if raw in {"ask", "constrained", "reject"} else "ask"


def react_native_tool_calling() -> bool:
    """Whether to use OpenAI-compatible native function calling in the ReAct loop.

    Set CHAT_REACT_NATIVE_TOOL_CALLING=1 or rag_config.yaml react.native_tool_calling: true.
    Defaults to True (enabled) — falls back to text JSON if model doesn't support it.
    """
    v = os.getenv("CHAT_REACT_NATIVE_TOOL_CALLING")
    if v is not None and str(v).strip() != "":
        return str(v).strip().lower() in {"1", "true", "yes", "on"}
    return bool(_get("react", "native_tool_calling", True))


def react_force_text_tool_models() -> list[str]:
    raw = _get("react", "force_text_tool_models", [])
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    return []


def react_model_prefers_text_tool_mode(model_name: str) -> bool:
    normalized = str(model_name or "").strip().lower()
    if not normalized:
        return False
    return any(pattern.lower() in normalized for pattern in react_force_text_tool_models())


def model_intent_enable_thinking() -> bool:
    v = os.getenv("CHAT_MODEL_INTENT_ENABLE_THINKING")
    if v is not None and str(v).strip() != "":
        return str(v).strip().lower() in {"1", "true", "yes", "on"}
    return bool(_get("model", "intent_enable_thinking", False))


def model_native_generation_enable_thinking() -> bool:
    v = os.getenv("CHAT_MODEL_NATIVE_ENABLE_THINKING")
    if v is not None and str(v).strip() != "":
        return str(v).strip().lower() in {"1", "true", "yes", "on"}
    return bool(_get("model", "native_generation_enable_thinking", True))


def model_structured_generation_enable_thinking() -> bool:
    v = os.getenv("CHAT_MODEL_STRUCTURED_ENABLE_THINKING")
    if v is not None and str(v).strip() != "":
        return str(v).strip().lower() in {"1", "true", "yes", "on"}
    return bool(_get("model", "structured_generation_enable_thinking", False))

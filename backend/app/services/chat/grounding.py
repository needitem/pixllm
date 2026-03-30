import json
import logging
from typing import Any, Dict, List

from ...deps import state
from ...utils.source_guard import (
    extract_answer_file_mentions,
    find_ungrounded_source_mentions,
    normalize_source_path,
)


logger = logging.getLogger(__name__)
def enforce_source_whitelist(
    answer: str,
    sources: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    trace_id: str,
    extra_allowed_paths: List[str] | None = None,
) -> tuple[str, Dict[str, Any]]:
    allowed_paths: set[str] = set()
    for src in sources or []:
        file_path = normalize_source_path(str(src.get("file_path") or ""))
        if file_path:
            allowed_paths.add(file_path)
    for item in results or []:
        payload = item.get("payload", {}) if isinstance(item, dict) else {}
        file_path = normalize_source_path(str(payload.get("file_path") or payload.get("source_file") or ""))
        if file_path:
            allowed_paths.add(file_path)
    for item in list(extra_allowed_paths or []):
        file_path = normalize_source_path(str(item or ""))
        if file_path:
            allowed_paths.add(file_path)

    mentions = extract_answer_file_mentions(answer)
    ungrounded = find_ungrounded_source_mentions(answer, allowed_paths)
    if not ungrounded:
        return answer, {
            "mentions": len(mentions),
            "ungrounded_mentions": 0,
            "ungrounded_examples": [],
            "passed": True,
            "rejected": False,
        }

    logger.warning(
        "Answer source guard detected ungrounded references",
        extra={
            "trace_id": trace_id,
            "ungrounded_count": len(ungrounded),
            "ungrounded_examples": ungrounded[:5],
            "allowed_source_count": len(allowed_paths),
        },
    )
    return answer, {
        "mentions": len(mentions),
        "ungrounded_mentions": len(ungrounded),
        "ungrounded_examples": ungrounded[:5],
        "passed": False,
        "rejected": True,
    }


async def project_scope_has_known_assets(project_name: str) -> bool:
    normalized = str(project_name or "").strip().lower()
    if not normalized:
        return False

    code_tools = getattr(state, "code_tools", None)
    for root in getattr(code_tools, "configured_roots", []) if code_tools is not None else []:
        try:
            candidate = root / normalized
        except Exception:
            continue
        if candidate.exists() and candidate.is_dir():
            return True

    redis = getattr(state, "redis", None)
    if redis is None:
        return False

    try:
        doc_ids = await redis.smembers("doc:index")
    except Exception:
        return False

    for doc_id in doc_ids or []:
        try:
            raw = await redis.get(f"doc:{doc_id}")
        except Exception:
            continue
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        project = str(payload.get("project") or "").strip().lower()
        if project == normalized:
            return True
    return False

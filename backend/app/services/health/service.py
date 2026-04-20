from datetime import datetime, timezone
from pathlib import Path

from ... import config
from ..wiki.service import wiki_parent_root


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _wiki_stats() -> dict:
    root = wiki_parent_root()
    page_count = 0
    wiki_ids: list[str] = []

    if root.exists() and root.is_dir():
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            wiki_ids.append(child.name)
            page_count += len(list(Path(child).rglob("*.md")))

    return {
        "root_path": str(root),
        "wiki_ids": wiki_ids,
        "page_count": page_count,
        "present": root.exists() and root.is_dir(),
    }


def _raw_source_stats() -> dict:
    root = Path(config.RAW_SOURCE_ROOT)
    return {
        "root_path": str(root),
        "present": root.exists() and root.is_dir(),
    }


def build_liveness_response() -> dict:
    return {
        "status": "ok",
        "service": config.APP_NAME,
        "checked_at": _timestamp(),
    }


async def build_health_response() -> dict:
    wiki = _wiki_stats()
    raw_source = _raw_source_stats()
    return {
        "status": "ok" if (wiki["present"] and raw_source["present"]) else "degraded",
        "service": config.APP_NAME,
        "checked_at": _timestamp(),
        "components": {
            "wiki_store": {
                "status": "ok" if wiki["present"] else "error",
                "root_path": wiki["root_path"],
                "wiki_ids": wiki["wiki_ids"],
                "page_count": wiki["page_count"],
            },
            "raw_source_store": {
                "status": "ok" if raw_source["present"] else "error",
                "root_path": raw_source["root_path"],
            }
        },
    }


async def build_readiness_response() -> dict:
    payload = await build_health_response()
    return {
        **payload,
        "ready": payload["status"] == "ok",
    }

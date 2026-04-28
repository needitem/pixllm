from datetime import datetime, timezone
from pathlib import Path

from ... import config
from ..source.service import methods_index_file, source_manifest_file, source_root


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _raw_source_stats() -> dict:
    root = source_root()
    source_file_count = 0
    if root.exists() and root.is_dir():
        source_file_count = sum(
            1
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".h", ".hpp", ".cpp", ".cxx", ".cc", ".cs"}
        )
    return {
        "root_path": str(root),
        "present": root.exists() and root.is_dir(),
        "source_file_count": source_file_count,
        "methods_index_path": methods_index_file().as_posix(),
        "methods_index_present": methods_index_file().exists(),
        "source_manifest_path": source_manifest_file().as_posix(),
        "source_manifest_present": source_manifest_file().exists(),
    }


def build_liveness_response() -> dict:
    return {
        "status": "ok",
        "service": config.APP_NAME,
        "checked_at": _timestamp(),
    }


async def build_health_response() -> dict:
    raw_source = _raw_source_stats()
    return {
        "status": "ok" if raw_source["present"] else "degraded",
        "service": config.APP_NAME,
        "checked_at": _timestamp(),
        "components": {
            "raw_source_store": {
                "status": "ok" if raw_source["present"] else "error",
                "root_path": raw_source["root_path"],
                "source_file_count": raw_source["source_file_count"],
            },
            "source_index": {
                "status": "ok" if raw_source["methods_index_present"] else "missing",
                "methods_index_path": raw_source["methods_index_path"],
                "source_manifest_path": raw_source["source_manifest_path"],
                "source_manifest_present": raw_source["source_manifest_present"],
            },
        },
    }


async def build_readiness_response() -> dict:
    payload = await build_health_response()
    return {
        **payload,
        "ready": payload["status"] == "ok",
    }

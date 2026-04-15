import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Optional


logger = logging.getLogger(__name__)

_RESTORE_WRITE_ATTEMPTS = 2


def _is_subpath(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False


def source_path_from_key(source_key: str) -> Optional[Path]:
    raw = str(source_key or "").strip()
    prefix = "path::"
    if not raw.startswith(prefix):
        return None
    candidate = raw[len(prefix):].strip()
    if not candidate:
        return None
    return Path(candidate)


def resolve_import_code_target_path(doc: dict[str, Any], revision: dict[str, Any], import_root: str) -> Optional[Path]:
    import_root_path = Path(import_root).resolve()
    source_path = source_path_from_key(doc.get("source_key") or "")
    if source_path is not None:
        resolved_source = source_path.resolve()
        if _is_subpath(resolved_source, import_root_path):
            return resolved_source

    project = str(doc.get("project") or "").strip()
    source_file = str(revision.get("source_file") or "").strip().replace("\\", "/")
    if not project or not source_file:
        return None
    return (import_root_path / project / source_file).resolve()


def _content_matches(path: Path, content_hash: str) -> bool:
    if not path.exists() or not path.is_file() or not content_hash:
        return False
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest() == str(content_hash).strip()
    except Exception:
        return False


async def restore_import_code_workspace(
    redis,
    minio_client,
    bucket: str,
    import_root: str,
    *,
    project: Optional[str] = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    import_root_path = Path(import_root).resolve()
    import_root_path.mkdir(parents=True, exist_ok=True)

    normalized_project = str(project or "").strip().lower()
    doc_ids = list(await redis.smembers("doc:index"))

    documents = 0
    restored = 0
    skipped = 0
    missing_revision = 0
    missing_object = 0
    errors = 0

    for doc_id in doc_ids:
        raw_doc = await redis.get(f"doc:{doc_id}")
        if not raw_doc:
            continue
        try:
            doc = json.loads(raw_doc)
        except Exception:
            errors += 1
            continue

        if str(doc.get("source_type") or "").strip() != "import_code":
            continue
        if normalized_project and str(doc.get("project") or "").strip().lower() != normalized_project:
            continue

        documents += 1
        revision_id = str(doc.get("current_revision_id") or "").strip()
        if not revision_id:
            missing_revision += 1
            continue

        raw_revision = await redis.get(f"doc_rev:{revision_id}")
        if not raw_revision:
            missing_revision += 1
            continue
        try:
            revision = json.loads(raw_revision)
        except Exception:
            errors += 1
            continue

        target_path = resolve_import_code_target_path(doc, revision, str(import_root_path))
        if target_path is None or not _is_subpath(target_path, import_root_path):
            errors += 1
            continue

        content_hash = str(revision.get("content_hash") or "").strip()
        if not overwrite and _content_matches(target_path, content_hash):
            skipped += 1
            continue

        object_name = str(revision.get("object_name") or "").strip()
        if not object_name:
            missing_object += 1
            continue

        try:
            response = minio_client.get_object(bucket, object_name)
            try:
                data = response.read()
            finally:
                response.close()
                response.release_conn()
            last_write_error = None
            preserved_existing_file = False
            for attempt in range(_RESTORE_WRITE_ATTEMPTS):
                try:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.write_bytes(data)
                    last_write_error = None
                    break
                except FileNotFoundError as exc:
                    if target_path.exists() and target_path.is_file():
                        preserved_existing_file = True
                        last_write_error = None
                        break
                    last_write_error = exc
                    if attempt + 1 >= _RESTORE_WRITE_ATTEMPTS:
                        raise
            if preserved_existing_file:
                skipped += 1
                continue
            if last_write_error is not None:
                raise last_write_error
            restored += 1
        except Exception:
            logger.warning(
                "Failed to restore imported code file",
                extra={
                    "doc_id": doc_id,
                    "project": doc.get("project"),
                    "object_name": object_name,
                    "target_path": str(target_path),
                },
                exc_info=True,
            )
            errors += 1

    return {
        "project": normalized_project or None,
        "documents": documents,
        "restored": restored,
        "skipped": skipped,
        "missing_revision": missing_revision,
        "missing_object": missing_object,
        "errors": errors,
    }

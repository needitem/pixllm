import asyncio
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
try:
    from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct
except Exception:  # pragma: no cover - optional dependency in lightweight tests
    FieldCondition = Filter = MatchValue = PointStruct = object

from .. import config
from ..core.document_store import DocumentStoreService
from ..deps import state
from ..envelopes import err, ok
from ..services.imports.documents import extract_document_sections as _extract_document_sections
from ..services.imports.errors import (
    UPLOAD_ERROR_CONNECTION_ABORTED as _UPLOAD_ERROR_CONNECTION_ABORTED,
    UPLOAD_ERROR_PAYLOAD_TOO_LARGE as _UPLOAD_ERROR_PAYLOAD_TOO_LARGE,
    UPLOAD_ERROR_PERMISSION_DENIED as _UPLOAD_ERROR_PERMISSION_DENIED,
    UPLOAD_ERROR_SERVER_ERROR as _UPLOAD_ERROR_SERVER_ERROR,
    UPLOAD_ERROR_TIMEOUT as _UPLOAD_ERROR_TIMEOUT,
    UPLOAD_ERROR_UNKNOWN as _UPLOAD_ERROR_UNKNOWN,
    classify_upload_error as _classify_upload_error,
    format_svn_sync_error as _format_svn_sync_error,
)
from ..services.imports.jobs import (
    IMPORT_INDEX_KEY,
    local_folder_session_key as _local_folder_session_key_impl,
    read_job_payload as _read_job_payload,
    save_local_folder_session as _save_local_folder_session_impl,
)
from ..services.imports.paths import (
    SUPPORTED_DOC_EXTENSIONS,
    copy_upload_stream_to_path as _copy_upload_stream_to_path,
    extensions_for_mode as _extensions_for_mode,
    normalize_import_mode as _normalize_import_mode,
    normalize_svn_revision as _normalize_svn_revision,
    resolve_import_path as _resolve_import_path,
    resolve_source_workspace_path as _resolve_source_workspace_path,
    safe_project_path as _safe_project_path,
    safe_upload_relative_path as _safe_upload_relative_path,
    sanitize_project as _sanitize_project,
    source_file_response as _source_file_response,
    source_object_response as _source_object_response,
)
from ..services.imports.service import FilesService
from ..services.imports.tasks import (
    delete_import_document_records as _delete_import_document_records_impl,
    encode_chunks as _encode_chunks_impl,
    import_job_collection_for_mode as _import_job_collection_for_mode,
    job_collection_name as _job_collection_name,
    list_import_object_names_for_job as _list_import_object_names_for_job_impl,
    remove_document_points as _remove_document_points,
    remove_import_objects as _remove_import_objects_impl,
    remove_points_by_field as _remove_points_by_field_impl,
    run_import_path_task,
    run_import_repo_task,
    run_index_file_task,
)
from ..services.tools.workspace_sync import resolve_import_code_target_path
from ..utils.ids import new_id
from ..utils.time import now_iso


router = APIRouter()


class ImportRequest(BaseModel):
    path: str = Field(..., description="Server-side directory path to import")
    collection: str = Field(default="documents", pattern="^documents$")
    mode: str = Field(default="docs", pattern="^(docs|code)$")
    project: Optional[str] = Field(default=None, description="Optional project name override")


class RepoImportRequest(BaseModel):
    source: str = Field(..., pattern="^(tfs|svn)$")
    mode: str = Field(..., pattern="^(docs|code)$")
    project: str = Field(..., min_length=1, description="Project key used under import root")
    tfs_path: Optional[str] = Field(default=None, description="TFS path label (for metadata)")
    tfs_sync_command: Optional[str] = Field(default=None, description="Optional override sync command")
    svn_url: Optional[str] = Field(default=None, description="SVN repository URL")
    svn_username: Optional[str] = Field(default=None)
    svn_password: Optional[str] = Field(default=None)
    svn_revision: Optional[str] = Field(default=None)
    svn_export: bool = Field(default=False)


class LocalFolderFinalizeRequest(BaseModel):
    project: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    mode: str = Field(default="docs", pattern="^(docs|code)$")


async def _save_job(job: dict):
    await state.redis.set(f"import_job:{job['job_id']}", json.dumps(job))
    await state.redis.sadd(IMPORT_INDEX_KEY, job["job_id"])


async def _update_job(job_id: str, **patch):
    raw = await state.redis.get(f"import_job:{job_id}")
    payload = _read_job_payload(raw)
    if not payload:
        return None
    payload.update(patch)
    await _save_job(payload)
    return payload


async def _is_cancel_requested(job_id: str) -> bool:
    raw = await state.redis.get(f"import_job:{job_id}")
    payload = _read_job_payload(raw)
    if not payload:
        return False
    return bool(payload.get("cancel_requested", False))


def _local_folder_session_key(session_id: str) -> str:
    return _local_folder_session_key_impl(session_id)


async def _get_local_folder_session(session_id: str):
    raw = await state.redis.get(_local_folder_session_key(session_id))
    return _read_job_payload(raw)


async def _save_local_folder_session(session: dict):
    return await _save_local_folder_session_impl(session)


async def _encode_chunks(chunks: list[str]):
    return await _encode_chunks_impl(chunks, state_obj=state)


def _remove_points_by_field(field: str, value: str, collection_name: Optional[str] = None):
    kwargs = {"collection_name": collection_name or config.RAG_DEFAULT_COLLECTION}
    try:
        kwargs["points_selector"] = Filter(must=[FieldCondition(key=field, match=MatchValue(value=value))])
    except Exception:
        pass
    return state.search_svc.qdrant.delete(**kwargs)


def _list_import_object_names_for_job(job_id: str) -> set[str]:
    return _list_import_object_names_for_job_impl(job_id, state_obj=state)


def _remove_import_objects(object_names: set[str]):
    return _remove_import_objects_impl(object_names, state_obj=state)


async def _delete_import_document_records(job_id: str, collection_name: Optional[str] = None) -> set[str]:
    return await _delete_import_document_records_impl(
        job_id,
        collection_name=collection_name,
        state_obj=state,
        document_store_cls=DocumentStoreService,
    )


def _build_import_job(
    *,
    job_id: str,
    path: str,
    mode: str,
    project: Optional[str],
    collection: Optional[str] = None,
    **extra,
) -> dict:
    return {
        "job_id": job_id,
        "path": path,
        "collection": collection or _import_job_collection_for_mode(mode),
        "mode": mode,
        "project": project,
        "status": "queued",
        "total_files": 0,
        "processed_files": 0,
        "total_chunks": 0,
        "embedded_chunks": 0,
        "created_at": now_iso(),
        "started_at": None,
        "finished_at": None,
        "cancel_requested": False,
        "error_message": None,
        **extra,
    }


async def _collect_valid_local_upload_entries(
    uploads: list[UploadFile],
    *,
    mode: str,
) -> list[tuple[UploadFile, str, Path]]:
    allowed_extensions = _extensions_for_mode(mode)
    valid_entries: list[tuple[UploadFile, str, Path]] = []
    for upload in uploads:
        filename = upload.filename or ""
        suffix = Path(filename).suffix.lower()
        if suffix not in allowed_extensions:
            await upload.close()
            continue
        try:
            root_name, relative_tail = _safe_upload_relative_path(filename)
        except ValueError:
            await upload.close()
            continue
        valid_entries.append((upload, root_name, relative_tail))
    return valid_entries


async def _copy_local_upload_entries(
    entries: list[tuple[UploadFile, str, Path]],
    *,
    target_root: Path,
    resolved_folder_root: str,
) -> int:
    copied_files = 0
    for upload, root_name, relative_tail in entries:
        destination = (
            target_root / relative_tail
            if root_name == resolved_folder_root
            else target_root / root_name / relative_tail
        )
        await asyncio.to_thread(_copy_upload_stream_to_path, upload.file, destination)
        copied_files += 1
        await upload.close()
    return copied_files


async def _read_upload_bytes(upload: UploadFile, *, max_bytes: int, chunk_size: int) -> bytes:
    limit = max(1, int(max_bytes or 0))
    read_chunk_size = max(4096, int(chunk_size or 0))
    payload = bytearray()
    while True:
        chunk = await upload.read(read_chunk_size)
        if not chunk:
            break
        payload.extend(chunk)
        if len(payload) > limit:
            raise ValueError(f"payload too large: exceeds {limit} bytes")
    return bytes(payload)


def _validate_import_path(path_value: str, *, mode: str) -> Path:
    root_dir = config.IMPORT_CODE_ROOT if _normalize_import_mode(mode) == "code" else config.IMPORT_DOCS_ROOT
    return _resolve_import_path(root_dir, path_value)


async def import_repo_task(job_id: str):
    return await run_import_repo_task(job_id, state_obj=state, update_job_fn=_update_job, read_job_payload_fn=_read_job_payload)


async def import_path_task(job_id: str):
    return await run_import_path_task(
        job_id,
        state_obj=state,
        document_store_cls=DocumentStoreService,
        extract_document_sections_fn=_extract_document_sections,
        encode_chunks_fn=_encode_chunks,
        update_job_fn=_update_job,
        is_cancel_requested_fn=_is_cancel_requested,
        classify_upload_error_fn=_classify_upload_error,
        remove_document_points_fn=lambda document_id, collection_name=None: _remove_points_by_field("document_id", document_id, collection_name),
        read_job_payload_fn=_read_job_payload,
        point_struct_cls=PointStruct,
    )


async def index_file_task(file_id: str):
    return await run_index_file_task(
        file_id,
        state_obj=state,
        files_service_cls=FilesService,
        document_store_cls=DocumentStoreService,
        extract_document_sections_fn=_extract_document_sections,
        encode_chunks_fn=_encode_chunks,
        remove_document_points_fn=lambda document_id, collection_name=None: _remove_points_by_field("document_id", document_id, collection_name),
        point_struct_cls=PointStruct,
    )


@router.get("/files")
async def list_files(page: int = 1, per_page: int = 20):
    svc = FilesService(state.redis, state.minio, config.MINIO_BUCKET)
    data = await svc.list(page, per_page)
    return ok(data)


@router.get("/files/{file_id}")
async def get_file(file_id: str):
    svc = FilesService(state.redis, state.minio, config.MINIO_BUCKET)
    data = await svc.get(file_id)
    if not data:
        return err("NOT_FOUND", "file not found")
    return ok(data)


@router.get("/files/source/open")
async def open_source_file(
    document_id: Optional[str] = Query(default=None),
    module: Optional[str] = Query(default=None),
    source_file: Optional[str] = Query(default=None),
    download: bool = Query(default=False),
):
    normalized_document_id = str(document_id or "").strip()
    normalized_module = str(module or "").strip() or None
    normalized_source_file = str(source_file or "").strip() or None

    if normalized_document_id:
        doc_store = DocumentStoreService(state.redis)
        doc = await doc_store.get_document(normalized_document_id)
        if doc:
            current_revision = await doc_store.get_current_revision(normalized_document_id)
            if not current_revision:
                raise HTTPException(status_code=404, detail="document revision not found")

            filename = str(current_revision.get("source_file") or doc.get("title") or "source")
            source_type = str(doc.get("source_type") or "").strip()
            if source_type == "import_code":
                target_path = resolve_import_code_target_path(doc, current_revision, config.IMPORT_CODE_ROOT)
                if target_path and target_path.exists() and target_path.is_file():
                    return _source_file_response(target_path, filename, download)

            object_name = str(current_revision.get("object_name") or "").strip()
            if object_name:
                return await _source_object_response(object_name, filename, download)

    target_path = _resolve_source_workspace_path(normalized_module, normalized_source_file)
    if target_path is not None:
        return _source_file_response(target_path, target_path.name, download)

    raise HTTPException(status_code=404, detail="source file not found")


@router.get("/documents")
async def list_documents(page: int = 1, per_page: int = 20):
    svc = DocumentStoreService(state.redis)
    data = await svc.list_documents(page, per_page)
    return ok(data)


@router.get("/documents/{document_id}/revisions")
async def list_document_revisions(document_id: str, limit: int = 50):
    svc = DocumentStoreService(state.redis)
    doc = await svc.get_document(document_id)
    if not doc:
        return err("NOT_FOUND", "document not found")
    revisions = await svc.list_revisions(document_id, limit=limit)
    return ok({"document": doc, "revisions": revisions})


@router.post("/files")
async def upload_file(
    background_tasks: BackgroundTasks,
    upload: UploadFile = File(...),
    collection: str = Form("documents"),
    project: str = Form(""),
):
    if collection != "documents":
        return err("BAD_REQUEST", "collection은 documents만 지원합니다.")

    filename = upload.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_DOC_EXTENSIONS:
        return err(
            "BAD_REQUEST",
            f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(SUPPORTED_DOC_EXTENSIONS)}",
        )

    try:
        data = await _read_upload_bytes(
            upload,
            max_bytes=config.FILE_UPLOAD_MAX_BYTES,
            chunk_size=config.FILE_UPLOAD_READ_CHUNK_BYTES,
        )
    except asyncio.TimeoutError as exc:
        error_code, user_message = _classify_upload_error(exc)
        return err(error_code, user_message)
    except Exception as exc:
        error_code, user_message = _classify_upload_error(exc)
        return err(error_code, user_message)
    finally:
        await upload.close()

    try:
        svc = FilesService(state.redis, state.minio, config.MINIO_BUCKET)
        normalized_project = _sanitize_project(project) or "uploads"
        meta = await svc.create(
            filename,
            upload.content_type or "application/octet-stream",
            data,
            "documents",
            project=normalized_project,
        )
    except PermissionError as exc:
        error_code, user_message = _classify_upload_error(exc)
        return err(error_code, user_message)
    except Exception as exc:
        error_code, user_message = _classify_upload_error(exc)
        return err(error_code, user_message)

    background_tasks.add_task(index_file_task, meta["file_id"])
    return ok(meta)


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    svc = FilesService(state.redis, state.minio, config.MINIO_BUCKET)
    meta = await svc.get(file_id)
    if meta:
        doc_store = DocumentStoreService(state.redis)
        source_key = f"upload::{file_id}"
        doc = await doc_store.get_document_by_source_key(source_key)
        if doc:
            _remove_document_points(doc["document_id"])
            await doc_store.delete_document(doc["document_id"])
        else:
            _remove_points_by_field("file_id", file_id)
    await svc.delete(file_id)
    return ok({"deleted": file_id})


@router.post("/imports")
async def create_import_job(payload: ImportRequest, background_tasks: BackgroundTasks):
    normalized_mode = _normalize_import_mode(payload.mode)
    try:
        target_path = _validate_import_path(payload.path, mode=normalized_mode)
    except ValueError as exc:
        return err("BAD_REQUEST", str(exc))
    if not target_path.exists() or not target_path.is_dir():
        return err("BAD_REQUEST", "path must be an existing directory inside the configured import root")

    job_id = new_id()
    project = _sanitize_project(payload.project)
    job = _build_import_job(
        job_id=job_id,
        path=str(target_path),
        collection=_import_job_collection_for_mode(normalized_mode),
        mode=normalized_mode,
        project=project,
    )
    await _save_job(job)
    background_tasks.add_task(import_path_task, job_id)
    return ok(job)


@router.post("/imports/repo")
async def create_repo_import_job(payload: RepoImportRequest, background_tasks: BackgroundTasks):
    project = _sanitize_project(payload.project)
    if not project:
        return err("BAD_REQUEST", "project is required")

    if payload.source == "tfs" and payload.mode != "docs":
        return err("BAD_REQUEST", "tfs source supports docs mode only")
    if payload.source == "svn" and payload.mode != "code":
        return err("BAD_REQUEST", "svn source supports code mode only")

    if payload.source == "tfs":
        command = (payload.tfs_sync_command or "").strip() or config.TFS_DOCS_SYNC_COMMAND
        if not command:
            return err("BAD_REQUEST", "TFS sync command is not configured")
    if payload.source == "svn" and not (payload.svn_url or "").strip():
        return err("BAD_REQUEST", "svn_url is required for svn source")

    svn_revision = _normalize_svn_revision(payload.svn_revision) if payload.source == "svn" else None
    svn_url = (payload.svn_url or "").strip() or None
    svn_username = (payload.svn_username or "").strip() or None
    svn_password = payload.svn_password if payload.svn_password else None

    job_id = new_id()
    root_dir = config.IMPORT_DOCS_ROOT if payload.mode == "docs" else config.IMPORT_CODE_ROOT
    target_path = str(_safe_project_path(root_dir, project))

    job = _build_import_job(
        job_id=job_id,
        path=target_path,
        mode=payload.mode,
        project=project,
        source=payload.source,
        sync_status="queued",
        sync_path=target_path,
        tfs_path=payload.tfs_path,
        tfs_sync_command=payload.tfs_sync_command,
        svn_url=svn_url,
        svn_username=svn_username,
        svn_password=svn_password,
        svn_revision=svn_revision,
        svn_export=payload.svn_export,
    )
    await _save_job(job)
    background_tasks.add_task(import_repo_task, job_id)
    return ok(job)


@router.post("/imports/local-folder/stage")
async def stage_local_folder_import_batch(
    uploads: list[UploadFile] = File(...),
    project: str = Form(""),
    session_id: str = Form(""),
    folder_root: str = Form(""),
    mode: str = Form("docs"),
):
    normalized_project = _sanitize_project(project)
    normalized_mode = _normalize_import_mode(mode)
    if not normalized_project:
        return err("BAD_REQUEST", "project is required")
    if not uploads:
        return err("BAD_REQUEST", "uploads are required")

    normalized_session_id = (session_id or "").strip() or new_id()
    existing_session = await _get_local_folder_session(normalized_session_id)

    project_root = config.IMPORT_CODE_ROOT if normalized_mode == "code" else config.IMPORT_DOCS_ROOT
    project_dir = _safe_project_path(project_root, normalized_project)
    valid_entries = await _collect_valid_local_upload_entries(uploads, mode=normalized_mode)

    if not valid_entries:
        kind = "code" if normalized_mode == "code" else "document"
        return err("BAD_REQUEST", f"no supported {kind} files in uploads")

    inferred_root_names = {entry[1] for entry in valid_entries}
    normalized_folder_root = _sanitize_project(folder_root)

    if existing_session:
        if existing_session.get("project") != normalized_project:
            for upload, _, _ in valid_entries:
                await upload.close()
            return err("BAD_REQUEST", "project does not match existing upload session")
        existing_mode = _normalize_import_mode(existing_session.get("mode"))
        if existing_mode != normalized_mode:
            for upload, _, _ in valid_entries:
                await upload.close()
            return err("BAD_REQUEST", "mode does not match existing upload session")
        resolved_folder_root = existing_session.get("folder_root")
        target_root = Path(existing_session.get("path") or "")
        staged_files = int(existing_session.get("staged_files") or 0)
        if not resolved_folder_root or not target_root:
            for upload, _, _ in valid_entries:
                await upload.close()
            return err("BAD_REQUEST", "invalid upload session")
    else:
        if normalized_folder_root:
            resolved_folder_root = normalized_folder_root
        elif len(inferred_root_names) == 1:
            resolved_folder_root = next(iter(inferred_root_names))
        else:
            resolved_folder_root = "local_folder"
        target_root = project_dir / resolved_folder_root
        staged_files = 0

    target_root.mkdir(parents=True, exist_ok=True)
    copied_files = await _copy_local_upload_entries(
        valid_entries,
        target_root=target_root,
        resolved_folder_root=resolved_folder_root,
    )

    session_payload = {
        "session_id": normalized_session_id,
        "project": normalized_project,
        "mode": normalized_mode,
        "folder_root": resolved_folder_root,
        "path": str(target_root),
        "staged_files": staged_files + copied_files,
        "created_at": existing_session.get("created_at") if existing_session else now_iso(),
        "updated_at": now_iso(),
    }
    await _save_local_folder_session(session_payload)

    return ok({
        **session_payload,
        "batch_files": copied_files,
    })


@router.post("/imports/local-folder/finalize")
async def finalize_local_folder_import(payload: LocalFolderFinalizeRequest, background_tasks: BackgroundTasks):
    normalized_project = _sanitize_project(payload.project)
    normalized_mode = _normalize_import_mode(payload.mode)
    if not normalized_project:
        return err("BAD_REQUEST", "project is required")

    normalized_session_id = payload.session_id.strip()
    if not normalized_session_id:
        return err("BAD_REQUEST", "session_id is required")

    session_payload = await _get_local_folder_session(normalized_session_id)
    if not session_payload:
        return err("NOT_FOUND", "upload session not found")

    if session_payload.get("project") != normalized_project:
        return err("BAD_REQUEST", "project does not match upload session")
    session_mode = _normalize_import_mode(session_payload.get("mode"))
    if session_mode != normalized_mode:
        return err("BAD_REQUEST", "mode does not match upload session")

    import_root = Path(session_payload.get("path") or "")
    if not import_root.exists() or not import_root.is_dir():
        return err("BAD_REQUEST", "staged folder path not found")

    job_id = new_id()
    job = _build_import_job(
        job_id=job_id,
        path=str(import_root),
        mode=normalized_mode,
        project=normalized_project,
        source="local-folder",
        sync_status="completed",
        sync_path=str(import_root),
        uploaded_files=int(session_payload.get("staged_files") or 0),
    )
    await _save_job(job)
    await state.redis.delete(_local_folder_session_key(normalized_session_id))
    background_tasks.add_task(import_path_task, job_id)
    return ok(job)


@router.get("/imports")
async def list_import_jobs(page: int = 1, per_page: int = 20):
    ids = list(await state.redis.smembers(IMPORT_INDEX_KEY))
    items = []
    for job_id in ids:
        raw = await state.redis.get(f"import_job:{job_id}")
        payload = _read_job_payload(raw)
        if payload:
            items.append(payload)
    items.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    start = (page - 1) * per_page
    end = start + per_page
    items = items[start:end]
    return ok({"items": items, "total": len(ids), "page": page, "per_page": per_page})


@router.get("/imports/{job_id}")
async def get_import_job(job_id: str):
    raw = await state.redis.get(f"import_job:{job_id}")
    payload = _read_job_payload(raw)
    if not payload:
        return err("NOT_FOUND", "import job not found")
    return ok(payload)


@router.post("/imports/{job_id}/cancel")
async def cancel_import_job(job_id: str):
    raw = await state.redis.get(f"import_job:{job_id}")
    payload = _read_job_payload(raw)
    if not payload:
        return err("NOT_FOUND", "import job not found")

    if payload.get("status") in {"completed", "failed", "cancelled"}:
        return ok(payload)

    updated = await _update_job(job_id, cancel_requested=True)
    return ok(updated)


@router.delete("/imports/{job_id}")
async def delete_import_job(job_id: str):
    raw = await state.redis.get(f"import_job:{job_id}")
    job = _read_job_payload(raw)
    collection_name = _job_collection_name(job)
    if _normalize_import_mode((job or {}).get("mode")) != "code":
        _remove_points_by_field("job_id", job_id, collection_name=collection_name)
    object_names = await _delete_import_document_records(job_id, collection_name=collection_name)
    object_names.update(await asyncio.to_thread(_list_import_object_names_for_job, job_id))
    if object_names:
        await asyncio.to_thread(_remove_import_objects, object_names)
    await state.redis.delete(f"import_job:{job_id}")
    await state.redis.srem(IMPORT_INDEX_KEY, job_id)
    return ok({"deleted": job_id})

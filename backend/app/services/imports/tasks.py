import asyncio
import hashlib
import io
from pathlib import Path
from typing import Any, Callable, Optional

try:
    from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct, SparseVector
except Exception:  # pragma: no cover - optional dependency in lightweight tests
    FieldCondition = Filter = MatchValue = PointStruct = SparseVector = object

from ... import config
from ...core.document_store import DocumentStoreService
from ...deps import state
from ...services.imports.service import FilesService
from ...utils.file_indexing import language_from_name
from ...utils.ids import new_id
from ...utils.time import now_iso
from ..tools.workspace_sync import resolve_import_code_target_path
from .documents import extract_document_sections
from .errors import classify_upload_error
from .jobs import is_cancel_requested, read_job_payload, update_job
from .paths import (
    extensions_for_mode,
    normalize_import_mode,
    resolve_project_name,
    resolve_import_path,
    safe_project_path,
    sanitize_project,
)
from .sync import sync_svn_repo, sync_tfs_repo


_EMBED_ENCODE_LOCK = asyncio.Lock()
IMPORT_MINIO_PUT_TIMEOUT_SECONDS = 120
IMPORT_SECTION_EXTRACT_TIMEOUT_SECONDS = 180
IMPORT_QDRANT_UPSERT_TIMEOUT_SECONDS = 120
IMPORT_MAX_CHUNKS_PER_FILE = 4000


def embedding_batch_size(chunk_count: int) -> int:
    configured = max(1, int(config.EMBEDDING_BATCH_SIZE or 8))
    return min(configured, max(1, int(chunk_count)))


async def encode_chunks(chunks: list[str], *, state_obj=state):
    batch_size = embedding_batch_size(len(chunks))
    async with _EMBED_ENCODE_LOCK:
        return await asyncio.to_thread(
            state_obj.embed_model.encode,
            chunks,
            batch_size=batch_size,
            max_length=8192,
            return_dense=True,
            return_sparse=True,
        )


def build_sparse_vector(entry):
    if isinstance(entry, dict):
        return SparseVector(indices=[int(i) for i in entry.keys()], values=[float(v) for v in entry.values()])
    if hasattr(entry, "indices") and hasattr(entry, "values"):
        indices = entry.indices.tolist() if hasattr(entry.indices, "tolist") else list(entry.indices)
        values = entry.values.tolist() if hasattr(entry.values, "tolist") else list(entry.values)
        return SparseVector(indices=indices, values=values)
    return None


def job_collection_name(job: Optional[dict]) -> str:
    if isinstance(job, dict):
        raw = str(job.get("collection") or "").strip()
        if raw:
            return raw
    return config.RAG_DEFAULT_COLLECTION


def import_job_collection_for_mode(mode: str) -> str:
    return "metadata_only" if normalize_import_mode(mode) == "code" else "documents"


def remove_document_points(document_id: str, collection_name: Optional[str] = None, *, state_obj=state):
    kwargs = {"collection_name": collection_name or config.RAG_DEFAULT_COLLECTION}
    try:
        kwargs["points_selector"] = Filter(must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))])
    except Exception:
        pass
    state_obj.search_svc.qdrant.delete(**kwargs)


def remove_points_by_field(field: str, value: str, collection_name: Optional[str] = None, *, state_obj=state):
    kwargs = {"collection_name": collection_name or config.RAG_DEFAULT_COLLECTION}
    try:
        kwargs["points_selector"] = Filter(must=[FieldCondition(key=field, match=MatchValue(value=value))])
    except Exception:
        pass
    state_obj.search_svc.qdrant.delete(**kwargs)


def is_import_job_object_name(object_name: str, job_id: str) -> bool:
    return bool(object_name) and f"/{job_id}/" in object_name


def list_import_object_names_for_job(job_id: str, *, state_obj=state) -> set[str]:
    object_names: set[str] = set()
    try:
        for obj in state_obj.minio.list_objects(config.MINIO_BUCKET, prefix="imports/", recursive=True):
            name = str(getattr(obj, "object_name", "") or "")
            if is_import_job_object_name(name, job_id):
                object_names.add(name)
    except Exception:
        return object_names
    return object_names


def remove_import_objects(object_names: set[str], *, state_obj=state):
    for object_name in object_names:
        if not object_name:
            continue
        try:
            state_obj.minio.remove_object(config.MINIO_BUCKET, object_name)
        except Exception:
            continue


async def delete_import_document_records(
    job_id: str,
    collection_name: Optional[str] = None,
    *,
    state_obj=state,
    document_store_cls=DocumentStoreService,
    resolve_import_code_target_path_fn=resolve_import_code_target_path,
) -> set[str]:
    doc_store = document_store_cls(state_obj.redis)
    doc_ids = list(await state_obj.redis.smembers(doc_store.doc_index_key))
    object_names: set[str] = set()

    for doc_id in doc_ids:
        doc = await doc_store.get_document(doc_id)
        if not doc:
            continue
        current_revision = await doc_store.get_current_revision(doc_id)
        if not is_import_job_object_name(str((current_revision or {}).get("object_name") or ""), job_id):
            continue

        revisions = await doc_store.list_revisions(doc_id, limit=5000)
        for rev in revisions:
            obj_name = str(rev.get("object_name") or "")
            if obj_name:
                object_names.add(obj_name)

        is_import_code = str(doc.get("source_type") or "").strip() == "import_code"
        if is_import_code and current_revision:
            target_path = resolve_import_code_target_path_fn(doc, current_revision, config.IMPORT_CODE_ROOT)
            if target_path is not None:
                try:
                    if target_path.exists() and target_path.is_file():
                        target_path.unlink()
                except Exception:
                    pass

        if not is_import_code:
            remove_document_points(doc_id, collection_name=collection_name, state_obj=state_obj)
        await doc_store.delete_document(doc_id)

    return object_names


async def run_import_repo_task(
    job_id: str,
    *,
    state_obj=state,
    update_job_fn=update_job,
    read_job_payload_fn=read_job_payload,
):
    raw = await state_obj.redis.get(f"import_job:{job_id}")
    job = read_job_payload_fn(raw)
    if not job:
        return

    try:
        mode = (job.get("mode") or "docs").strip()
        source = (job.get("source") or "").strip()
        project = sanitize_project(job.get("project"))
        if not project:
            await update_job_fn(job_id, status="failed", error_message="invalid project", finished_at=now_iso())
            return

        root_dir = config.IMPORT_DOCS_ROOT if mode == "docs" else config.IMPORT_CODE_ROOT
        target_dir = safe_project_path(root_dir, project)
        target_dir.mkdir(parents=True, exist_ok=True)

        await update_job_fn(
            job_id,
            status="running",
            started_at=now_iso(),
            path=str(target_dir),
            sync_path=str(target_dir),
            total_files=0,
            processed_files=0,
            total_chunks=0,
            embedded_chunks=0,
            sync_status="running",
            svn_password=None,
            tfs_sync_command=None,
        )

        if source == "tfs":
            ok_sync, sync_error = await sync_tfs_repo(job, target_dir)
        elif source == "svn":
            ok_sync, sync_error = await sync_svn_repo(job, target_dir)
        else:
            ok_sync, sync_error = False, f"unsupported source: {source}"

        if not ok_sync:
            await update_job_fn(job_id, status="failed", sync_status="failed", error_message=sync_error, finished_at=now_iso())
            return

        await update_job_fn(job_id, sync_status="completed")
        await run_import_path_task(job_id, state_obj=state_obj, update_job_fn=update_job_fn, read_job_payload_fn=read_job_payload_fn)
    except Exception as exc:
        await update_job_fn(job_id, status="failed", sync_status="failed", error_message=str(exc), finished_at=now_iso())


async def run_import_path_task(
    job_id: str,
    *,
    state_obj=state,
    document_store_cls=DocumentStoreService,
    extract_document_sections_fn: Callable[[str, bytes], list[dict]] = extract_document_sections,
    encode_chunks_fn: Callable[[list[str]], Any] = encode_chunks,
    update_job_fn=update_job,
    is_cancel_requested_fn=is_cancel_requested,
    classify_upload_error_fn=classify_upload_error,
    remove_document_points_fn=remove_document_points,
    read_job_payload_fn=read_job_payload,
    point_struct_cls: type = PointStruct,
):
    response = None
    try:
        raw = await state_obj.redis.get(f"import_job:{job_id}")
        job = read_job_payload_fn(raw)
        if not job:
            return

        normalized_mode = normalize_import_mode(job.get("mode", "docs"))
        root_dir = config.IMPORT_CODE_ROOT if normalized_mode == "code" else config.IMPORT_DOCS_ROOT
        try:
            root_path = resolve_import_path(root_dir, job["path"])
        except ValueError:
            await update_job_fn(job_id, status="failed", error_message="path is outside configured import root", finished_at=now_iso())
            return
        if not root_path.exists() or not root_path.is_dir():
            await update_job_fn(job_id, status="failed", error_message="path not found", finished_at=now_iso())
            return

        explicit_project = sanitize_project(job.get("project"))
        is_code_mode = normalized_mode == "code"
        allowed_extensions = extensions_for_mode(normalized_mode)
        files = [p for p in root_path.rglob("*") if p.is_file() and p.suffix.lower() in allowed_extensions]

        await update_job_fn(
            job_id,
            status="running",
            started_at=now_iso(),
            total_files=len(files),
            processed_files=0,
            total_chunks=0,
            embedded_chunks=0,
        )

        processed = 0
        total_chunks = 0
        embedded_chunks = 0
        collection = job_collection_name(job)
        doc_store = document_store_cls(state_obj.redis)

        for file_path in files:
            if await is_cancel_requested_fn(job_id):
                await update_job_fn(job_id, status="cancelled", finished_at=now_iso())
                return
            try:
                raw_bytes = file_path.read_bytes()
                rel = str(file_path.relative_to(root_path)).replace("\\", "/")
                project = resolve_project_name(root_path, file_path, explicit_project)
                source_key = f"path::{str(file_path.resolve())}"
                content_hash = hashlib.sha256(raw_bytes).hexdigest()
                obj_name = f"imports/{project}/{job_id}/{rel}"

                await asyncio.wait_for(
                    asyncio.to_thread(
                        state_obj.minio.put_object,
                        config.MINIO_BUCKET,
                        obj_name,
                        io.BytesIO(raw_bytes),
                        length=len(raw_bytes),
                        content_type="application/octet-stream",
                    ),
                    timeout=IMPORT_MINIO_PUT_TIMEOUT_SECONDS,
                )

                sections = []
                chunks = []
                if not is_code_mode:
                    sections = await asyncio.wait_for(
                        asyncio.to_thread(extract_document_sections_fn, file_path.name, raw_bytes),
                        timeout=IMPORT_SECTION_EXTRACT_TIMEOUT_SECONDS,
                    )
                    chunks = [s["text"] for s in sections]
                    if len(chunks) > IMPORT_MAX_CHUNKS_PER_FILE:
                        sections = sections[:IMPORT_MAX_CHUNKS_PER_FILE]
                        chunks = chunks[:IMPORT_MAX_CHUNKS_PER_FILE]
                    total_chunks += len(chunks)

                doc = await doc_store.get_or_create_document(
                    source_key=source_key,
                    source_type="import_code" if is_code_mode else "import",
                    title=rel,
                    project=project,
                )
                doc_id = doc["document_id"]
                current_rev = await doc_store.get_current_revision(doc_id)
                if current_rev and current_rev.get("content_hash") == content_hash:
                    processed += 1
                    if processed % 5 == 0 or processed == len(files):
                        await update_job_fn(job_id, processed_files=processed, total_chunks=total_chunks, embedded_chunks=embedded_chunks)
                    continue

                revision = await doc_store.create_revision(
                    doc_id=doc_id,
                    content_hash=content_hash,
                    object_name=obj_name,
                    source_file=rel,
                )
                revision_id = revision["revision_id"]

                if current_rev:
                    await asyncio.to_thread(remove_document_points_fn, doc_id)

                if is_code_mode:
                    await doc_store.update_revision_status(revision_id, "indexed", chunk_count=0)
                    await doc_store.activate_revision(doc_id, revision_id, status="indexed")
                elif chunks:
                    language = language_from_name(str(file_path.name))
                    batch_size = embedding_batch_size(len(chunks))
                    for start_idx in range(0, len(chunks), batch_size):
                        end_idx = min(len(chunks), start_idx + batch_size)
                        batch_chunks = chunks[start_idx:end_idx]
                        encoded = await encode_chunks_fn(batch_chunks)
                        dense_vecs = encoded["dense_vecs"]
                        sparse_raw = encoded.get("lexical_weights") or encoded.get("sparse_vecs")

                        points = []
                        for local_idx, chunk in enumerate(batch_chunks):
                            chunk_index = start_idx + local_idx
                            sparse_vec = build_sparse_vector(sparse_raw[local_idx]) if sparse_raw is not None else None
                            vectors = {"dense": dense_vecs[local_idx].tolist()}
                            if sparse_vec is not None:
                                vectors["sparse"] = sparse_vec

                            points.append(
                                point_struct_cls(
                                    id=new_id(),
                                    vector=vectors,
                                    payload={
                                        "file_path": str(file_path),
                                        "source_file": rel,
                                        "language": language,
                                        "project": project,
                                        "module": project,
                                        "text": chunk,
                                        "heading_path": sections[chunk_index].get("heading_path", "root"),
                                        "page_number": sections[chunk_index].get("page_number"),
                                        "total_pages": sections[chunk_index].get("total_pages"),
                                        "chunk_index": chunk_index,
                                        "type": "imported_doc",
                                        "source_kind": "document",
                                        "document_id": doc_id,
                                        "revision_id": revision_id,
                                        "content_hash": content_hash,
                                        "acl_todo": True,
                                        "job_id": job_id,
                                        "object_name": obj_name,
                                    },
                                )
                            )

                        await asyncio.wait_for(
                            asyncio.to_thread(state_obj.search_svc.qdrant.upsert, collection_name=collection, points=points),
                            timeout=IMPORT_QDRANT_UPSERT_TIMEOUT_SECONDS,
                        )
                        embedded_chunks += len(points)
                        await update_job_fn(job_id, processed_files=processed, total_chunks=total_chunks, embedded_chunks=embedded_chunks)
                    await doc_store.update_revision_status(revision_id, "indexed", chunk_count=len(chunks))
                    await doc_store.activate_revision(doc_id, revision_id, status="indexed")
                else:
                    await doc_store.update_revision_status(revision_id, "indexed", chunk_count=0)
                    await doc_store.activate_revision(doc_id, revision_id, status="indexed")

            except Exception as exc:
                error_code, _user_msg = classify_upload_error_fn(exc)
                await update_job_fn(job_id, error_code=error_code, error_message=str(exc))

            processed += 1
            if processed % 5 == 0 or processed == len(files):
                await update_job_fn(job_id, processed_files=processed, total_chunks=total_chunks, embedded_chunks=embedded_chunks)

        await update_job_fn(
            job_id,
            status="completed",
            processed_files=processed,
            total_chunks=total_chunks,
            embedded_chunks=embedded_chunks,
            finished_at=now_iso(),
        )
    except Exception as exc:
        error_code, _user_msg = classify_upload_error_fn(exc)
        await update_job_fn(job_id, status="failed", error_code=error_code, error_message=str(exc), finished_at=now_iso())
    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass


async def run_index_file_task(
    file_id: str,
    *,
    state_obj=state,
    files_service_cls=FilesService,
    document_store_cls=DocumentStoreService,
    extract_document_sections_fn: Callable[[str, bytes], list[dict]] = extract_document_sections,
    encode_chunks_fn: Callable[[list[str]], Any] = encode_chunks,
    remove_document_points_fn=remove_document_points,
    point_struct_cls: type = PointStruct,
):
    svc = files_service_cls(state_obj.redis, state_obj.minio, config.MINIO_BUCKET)
    await svc.update_status(file_id, "indexing")
    doc_store = document_store_cls(state_obj.redis)
    response = None
    try:
        meta = await svc.get(file_id)
        if not meta:
            await svc.update_status(file_id, "failed", error_message="file metadata not found")
            return

        obj_name = meta.get("object_name")
        if not obj_name:
            await svc.update_status(file_id, "failed", error_message="object name missing")
            return

        response = await asyncio.to_thread(state_obj.minio.get_object, config.MINIO_BUCKET, obj_name)
        raw = await asyncio.to_thread(response.read)
        await svc.touch_heartbeat(file_id)

        filename = meta.get("filename", "")
        sections = await asyncio.to_thread(extract_document_sections_fn, filename, raw)
        await svc.touch_heartbeat(file_id)

        normalized_project = sanitize_project(meta.get("project")) or "uploads"
        source_key = f"upload::{file_id}"
        content_hash = hashlib.sha256(raw).hexdigest()
        doc = await doc_store.get_or_create_document(
            source_key=source_key,
            source_type="upload",
            title=filename or file_id,
            project=normalized_project,
        )
        doc_id = doc["document_id"]
        current_rev = await doc_store.get_current_revision(doc_id)
        if current_rev and current_rev.get("content_hash") == content_hash:
            await svc.update_status(file_id, "indexed", chunk_count=int(current_rev.get("chunk_count") or 0))
            return

        revision = await doc_store.create_revision(
            doc_id=doc_id,
            content_hash=content_hash,
            object_name=obj_name,
            source_file=filename or file_id,
        )
        revision_id = revision["revision_id"]

        if current_rev:
            await asyncio.to_thread(remove_document_points_fn, doc_id)

        chunks = [s["text"] for s in sections]
        if not chunks:
            await doc_store.update_revision_status(revision_id, "indexed", chunk_count=0)
            await doc_store.activate_revision(doc_id, revision_id, status="indexed")
            await svc.update_status(file_id, "indexed", chunk_count=0)
            return

        language = language_from_name(filename)
        collection_raw = meta.get("collection") if isinstance(meta, dict) else None
        collection = str(collection_raw or config.RAG_DEFAULT_COLLECTION).strip() or config.RAG_DEFAULT_COLLECTION
        project = normalized_project
        batch_size = embedding_batch_size(len(chunks))
        for start_idx in range(0, len(chunks), batch_size):
            await svc.touch_heartbeat(file_id)
            end_idx = min(len(chunks), start_idx + batch_size)
            batch_chunks = chunks[start_idx:end_idx]
            encoded = await encode_chunks_fn(batch_chunks)
            dense_vecs = encoded["dense_vecs"]
            sparse_raw = encoded.get("lexical_weights") or encoded.get("sparse_vecs")

            points = []
            for local_idx, chunk in enumerate(batch_chunks):
                chunk_index = start_idx + local_idx
                sparse_vec = build_sparse_vector(sparse_raw[local_idx]) if sparse_raw is not None else None
                vector_payload = {"dense": dense_vecs[local_idx].tolist()}
                if sparse_vec is not None:
                    vector_payload["sparse"] = sparse_vec

                points.append(
                    point_struct_cls(
                        id=new_id(),
                        vector=vector_payload,
                        payload={
                            "file_path": filename,
                            "source_file": filename,
                            "language": language,
                            "project": project,
                            "module": project,
                            "text": chunk,
                            "heading_path": sections[chunk_index].get("heading_path", "root"),
                            "page_number": sections[chunk_index].get("page_number"),
                            "total_pages": sections[chunk_index].get("total_pages"),
                            "chunk_index": chunk_index,
                            "type": "uploaded_doc",
                            "source_kind": "document",
                            "document_id": doc_id,
                            "revision_id": revision_id,
                            "content_hash": content_hash,
                            "acl_todo": True,
                            "file_id": file_id,
                        },
                    )
                )

            await asyncio.to_thread(state_obj.search_svc.qdrant.upsert, collection_name=collection, points=points)
        await doc_store.update_revision_status(revision_id, "indexed", chunk_count=len(chunks))
        await doc_store.activate_revision(doc_id, revision_id, status="indexed")
        await svc.update_status(file_id, "indexed", chunk_count=len(chunks))
    except Exception as exc:
        if "revision_id" in locals():
            await doc_store.update_revision_status(revision_id, "failed", error_message=str(exc))
        await svc.update_status(file_id, "failed", error_message=str(exc))
    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass

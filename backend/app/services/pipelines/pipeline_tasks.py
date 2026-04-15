import html
import json
import re
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import redis
from FlagEmbedding import BGEM3FlagModel
from minio import Minio
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from ... import config
from ...utils.encoding import TEXT_ENCODING_FALLBACKS_LATIN_FIRST, read_text_with_fallback


def _chunk_doc(content: str, file_path: str) -> List[Dict[str, Any]]:
    if "<html" in content.lower() or "<body" in content.lower():
        cleaned = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", content)
        cleaned = re.sub(r"(?is)<!--.*?-->", " ", cleaned)
        cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)
        content = html.unescape(cleaned)

    content = re.sub(r"\s+", " ", content).strip()
    if not content:
        return []

    chunk_size = 1000
    overlap = 200
    title = Path(file_path).stem
    chunks: List[Dict[str, Any]] = []
    start = 0
    idx = 0
    while start < len(content):
        end = min(len(content), start + chunk_size)
        if end < len(content):
            sentence_end = content.find(". ", end, min(len(content), end + 100))
            if sentence_end != -1:
                end = sentence_end + 1
        text = content[start:end].strip()
        if text:
            chunks.append(
                {
                    "text": text,
                    "metadata": {
                        "file_path": file_path,
                        "title": title,
                        "type": "doc",
                        "chunk_index": idx,
                    },
                }
            )
            idx += 1
        next_start = end - overlap
        start = next_start if next_start > start else end
    return chunks


def _load_embedding_model(model_name: str) -> BGEM3FlagModel:
    return BGEM3FlagModel(
        model_name,
        use_fp16=bool(config.EMBEDDING_USE_FP16),
        device=str(config.EMBEDDING_DEVICE or "cpu"),
    )


def _resolve_dense_vector_size(model: BGEM3FlagModel) -> int:
    probe = model.encode(["vector_size_probe"], batch_size=1, max_length=8192, return_dense=True, return_sparse=True)
    return len(probe["dense_vecs"][0])


def run_embed_docs_task(payload: Dict[str, Any], log: Callable[[str], None]) -> Dict[str, Any]:
    docs_dir = Path(str(payload.get("docs_dir") or "")).resolve()
    qdrant_url = str(payload.get("qdrant_url") or "http://localhost:6333")
    model_name = str(payload.get("model") or "BAAI/bge-m3")
    batch_size = max(1, int(payload.get("batch_size") or 32))
    force_reindex = bool(payload.get("force_reindex", False))

    if not docs_dir.exists() or not docs_dir.is_dir():
        raise RuntimeError(f"docs_dir must exist: {docs_dir}")

    log(f"[embed] load model={model_name}")
    model = _load_embedding_model(model_name)
    qdrant = QdrantClient(url=qdrant_url)

    vector_size = _resolve_dense_vector_size(model)

    collection = "documents"
    try:
        qdrant.get_collection(collection)
        log(f"[embed] collection exists: {collection}")
    except Exception:
        qdrant.create_collection(
            collection_name=collection,
            vectors_config={"dense": VectorParams(size=vector_size, distance=Distance.COSINE)},
            sparse_vectors_config={"sparse": SparseVectorParams(index=SparseIndexParams())},
        )
        log(f"[embed] collection created: {collection}")

    files: List[Path] = []
    for ext in ("*.html", "*.htm", "*.txt", "*.md"):
        files.extend(docs_dir.rglob(ext))
    log(f"[embed] found docs={len(files)}")

    chunks: List[Dict[str, Any]] = []
    for fpath in files:
        content = read_text_with_fallback(fpath, TEXT_ENCODING_FALLBACKS_LATIN_FIRST)
        if not content:
            continue
        chunks.extend(_chunk_doc(content, str(fpath)))

    total_chunks = len(chunks)
    log(f"[embed] chunks={total_chunks}")

    stored = 0
    for i in range(0, total_chunks, batch_size):
        batch = chunks[i : i + batch_size]
        id_pairs = []
        for chunk in batch:
            pid = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{chunk['metadata']['file_path']}_{chunk['metadata']['chunk_index']}",
                )
            )
            id_pairs.append((chunk, pid))

        if not force_reindex and id_pairs:
            try:
                hits = qdrant.retrieve(collection_name=collection, ids=[pid for _, pid in id_pairs], with_payload=False, with_vectors=False)
                existing = {h.id for h in hits}
                id_pairs = [(c, pid) for c, pid in id_pairs if pid not in existing]
            except Exception:
                pass
        if not id_pairs:
            continue

        texts = [c["text"] for c, _ in id_pairs]
        encoded = model.encode(texts, batch_size=batch_size, max_length=8192, return_dense=True, return_sparse=True)
        dense_vecs = encoded["dense_vecs"]
        sparse_vecs = encoded.get("sparse_vecs", [])

        points = []
        for idx, ((chunk, pid), dense_vec) in enumerate(zip(id_pairs, dense_vecs)):
            vectors: Dict[str, Any] = {"dense": dense_vec.tolist()}
            if sparse_vecs:
                sv = sparse_vecs[idx]
                if isinstance(sv, dict) and "indices" in sv and "values" in sv:
                    sparse = SparseVector(indices=sv["indices"], values=sv["values"])
                    if sparse.values:
                        vectors["sparse"] = sparse
            points.append(PointStruct(id=pid, vector=vectors, payload={"text": chunk["text"], **chunk["metadata"]}))

        qdrant.upsert(collection_name=collection, points=points)
        stored += len(points)
        if (i // batch_size) % 10 == 0:
            log(f"[embed] progress {min(i + batch_size, total_chunks)}/{total_chunks}")

    log(f"[embed] done stored={stored}")
    return {"files": len(files), "chunks": total_chunks, "stored": stored, "collection": collection}


def run_verify_embeddings_task(payload: Dict[str, Any], log: Callable[[str], None]) -> Dict[str, Any]:
    qdrant_url = str(payload.get("qdrant_url") or "http://localhost:6333")
    model_name = str(payload.get("model") or "BAAI/bge-m3")
    top_k = max(1, int(payload.get("top_k") or 3))
    query = str(payload.get("query") or "").strip()
    collection = str(payload.get("collection") or "documents")

    qdrant = QdrantClient(url=qdrant_url)
    info = qdrant.get_collection(collection)
    stats = {
        "collection": collection,
        "points": int(info.points_count or 0),
    }
    log(f"[verify] collection={collection} points={stats['points']}")

    samples: List[Dict[str, Any]] = []
    if query:
        queries = [query]
    else:
        queries = ["installation guide", "API reference", "getting started"]

    model = BGEM3FlagModel(model_name, use_fp16=bool(config.EMBEDDING_USE_FP16), device=str(config.EMBEDDING_DEVICE or "cpu"))
    for q in queries:
        out = model.encode([q], batch_size=1, max_length=8192, return_dense=True, return_sparse=True)
        dense_vec = out["dense_vecs"][0].tolist()
        response = qdrant.query_points(
            collection_name=collection,
            query=dense_vec,
            using="dense",
            limit=top_k,
            with_payload=True,
        )
        points = getattr(response, "points", []) or []
        row = {
            "query": q,
            "hits": [
                {
                    "score": float(getattr(p, "score", 0.0) or 0.0),
                    "file_path": (getattr(p, "payload", {}) or {}).get("file_path"),
                }
                for p in points
            ],
        }
        samples.append(row)
        log(f"[verify] query='{q}' hits={len(row['hits'])}")

    return {"stats": stats, "samples": samples}


def run_reset_evidence_task(payload: Dict[str, Any], log: Callable[[str], None]) -> Dict[str, Any]:
    skip_minio = bool(payload.get("skip_minio", False))
    keep_documents_only = bool(payload.get("keep_documents_only", True))

    qdrant = QdrantClient(url=config.QDRANT_URL)
    deleted = []
    managed_collections = {config.EVIDENCE_DEFAULT_COLLECTION, "metadata_only"}
    for collection_name in sorted(name for name in managed_collections if str(name or "").strip()):
        try:
            qdrant.get_collection(collection_name)
        except Exception:
            continue
        qdrant.delete_collection(collection_name)
        deleted.append(collection_name)
        log(f"[reset] qdrant delete {collection_name}")

    if keep_documents_only:
        model = _load_embedding_model(config.EMBEDDING_MODEL)
        vector_size = _resolve_dense_vector_size(model)
        qdrant.create_collection(
            collection_name=config.EVIDENCE_DEFAULT_COLLECTION,
            vectors_config={"dense": VectorParams(size=vector_size, distance=Distance.COSINE)},
            sparse_vectors_config={"sparse": SparseVectorParams(index=SparseIndexParams())},
        )
        log(f"[reset] qdrant create {config.EVIDENCE_DEFAULT_COLLECTION}")

    r = redis.Redis.from_url(config.REDIS_URL)
    removed_docs = 0
    removed_revisions = 0
    removed_files = 0

    doc_ids = list(r.smembers("doc:index") or [])
    for raw_doc_id in doc_ids:
        doc_id = raw_doc_id.decode() if isinstance(raw_doc_id, bytes) else str(raw_doc_id)
        raw_doc = r.get(f"doc:{doc_id}")
        doc = json.loads(raw_doc) if raw_doc else {}
        source_key = str(doc.get("source_key") or "").strip()
        rev_ids = list(r.lrange(f"doc_rev:index:{doc_id}", 0, -1) or [])
        for raw_rev_id in rev_ids:
            rev_id = raw_rev_id.decode() if isinstance(raw_rev_id, bytes) else str(raw_rev_id)
            r.delete(f"doc_rev:{rev_id}")
            removed_revisions += 1
        r.delete(f"doc_rev:index:{doc_id}")
        r.delete(f"doc:{doc_id}")
        if source_key:
            r.delete(f"doc:source:{source_key}")
        removed_docs += 1
    if doc_ids:
        r.delete("doc:index")
        log(f"[reset] redis cleared documents={removed_docs} revisions={removed_revisions}")

    file_ids = list(r.smembers("file:index") or [])
    for raw_file_id in file_ids:
        file_id = raw_file_id.decode() if isinstance(raw_file_id, bytes) else str(raw_file_id)
        r.delete(f"file:{file_id}")
        removed_files += 1
    if file_ids:
        r.delete("file:index")
        log(f"[reset] redis cleared file metadata={removed_files}")

    removed_objects = 0
    if not skip_minio:
        minio = Minio(
            config.MINIO_ENDPOINT,
            access_key=config.MINIO_ACCESS_KEY,
            secret_key=config.MINIO_SECRET_KEY,
            secure=False,
        )
        bucket = config.MINIO_BUCKET
        if minio.bucket_exists(bucket):
            objs = list(minio.list_objects(bucket, recursive=True))
            for obj in objs:
                minio.remove_object(bucket, obj.object_name)
            removed_objects = len(objs)
            log(f"[reset] minio removed={removed_objects}")
        else:
            log(f"[reset] minio bucket missing={bucket}")
    else:
        log("[reset] minio skipped")

    return {
        "deleted_collections": deleted,
        "recreated_collection": config.EVIDENCE_DEFAULT_COLLECTION if keep_documents_only else None,
        "redis_cleared": {
            "documents": removed_docs,
            "revisions": removed_revisions,
            "file_metadata": removed_files,
        },
        "minio_removed_objects": removed_objects,
    }

import io
import json
from datetime import datetime, timezone
from typing import Optional

from ... import config
from ...utils.ids import new_id
from ...utils.time import now_iso


class FilesService:
    def __init__(self, redis, minio, bucket: str):
        self.redis = redis
        self.minio = minio
        self.bucket = bucket
        self.index_key = "file:index"

    def _ensure_bucket(self):
        if not self.minio.bucket_exists(self.bucket):
            self.minio.make_bucket(self.bucket)

    def _parse_iso(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            dt = datetime.fromisoformat(value)
        except Exception:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def _coerce_stale_indexing(self, payload: dict) -> bool:
        if payload.get("status") != "indexing":
            return False
        stale_seconds = max(0, int(getattr(config, "FILE_INDEXING_STALE_SECONDS", 0) or 0))
        if stale_seconds <= 0:
            return False
        started = self._parse_iso(payload.get("last_heartbeat_at") or payload.get("indexing_started_at") or payload.get("created_at"))
        if started is None:
            return False
        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        if elapsed < stale_seconds:
            return False
        payload["status"] = "failed"
        payload["error_message"] = "Indexing exceeded time limit. Please retry upload."
        payload["last_heartbeat_at"] = now_iso()
        return True

    async def list(self, page: int, per_page: int):
        ids = list(await self.redis.smembers(self.index_key))
        records = []
        for fid in ids:
            raw = await self.redis.get(f"file:{fid}")
            if raw:
                payload = json.loads(raw)
                if self._coerce_stale_indexing(payload):
                    await self.redis.set(f"file:{fid}", json.dumps(payload))
                records.append(payload)

        records.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        start = (page - 1) * per_page
        end = start + per_page
        items = records[start:end]
        return {"items": items, "total": len(records), "page": page, "per_page": per_page}

    async def get(self, fid: str):
        raw = await self.redis.get(f"file:{fid}")
        if not raw:
            return None
        payload = json.loads(raw)
        if self._coerce_stale_indexing(payload):
            await self.redis.set(f"file:{fid}", json.dumps(payload))
        return payload

    async def create(self, filename: str, content_type: str, data: bytes, collection: str = "documents", project: str = "uploads"):
        fid = new_id()
        obj_name = f"{fid}/{filename}"
        self._ensure_bucket()
        self.minio.put_object(
            self.bucket,
            obj_name,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        payload = {
            "file_id": fid,
            "filename": filename,
            "size_bytes": len(data),
            "content_type": content_type,
            "status": "queued",
            "created_at": now_iso(),
            "indexed_at": None,
            "chunk_count": None,
            "error_message": None,
            "collection": "documents" if collection != "documents" else collection,
            "project": project or "uploads",
            "object_name": obj_name,
        }
        await self.redis.set(f"file:{fid}", json.dumps(payload))
        await self.redis.sadd(self.index_key, fid)
        return payload

    async def update_status(self, fid: str, status: str, chunk_count: Optional[int] = None, error_message: Optional[str] = None):
        raw = await self.redis.get(f"file:{fid}")
        if not raw:
            return None
        payload = json.loads(raw)
        payload["status"] = status
        if status == "indexing":
            payload.setdefault("indexing_started_at", now_iso())
            payload["last_heartbeat_at"] = now_iso()
        if status == "indexed":
            payload["indexed_at"] = now_iso()
            payload["chunk_count"] = chunk_count or 0
            payload["last_heartbeat_at"] = now_iso()
        if status == "failed":
            payload["last_heartbeat_at"] = now_iso()
        if error_message:
            payload["error_message"] = error_message
        await self.redis.set(f"file:{fid}", json.dumps(payload))
        return payload

    async def touch_heartbeat(self, fid: str):
        raw = await self.redis.get(f"file:{fid}")
        if not raw:
            return None
        payload = json.loads(raw)
        if payload.get("status") == "indexing":
            payload["last_heartbeat_at"] = now_iso()
            await self.redis.set(f"file:{fid}", json.dumps(payload))
        return payload

    async def delete(self, fid: str):
        raw = await self.redis.get(f"file:{fid}")
        if raw:
            payload = json.loads(raw)
            obj = payload.get("object_name")
            if obj:
                self._ensure_bucket()
                self.minio.remove_object(self.bucket, obj)
        await self.redis.delete(f"file:{fid}")
        await self.redis.srem(self.index_key, fid)
        return True

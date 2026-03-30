import json
from typing import Optional

from ..utils.ids import new_id
from ..utils.time import now_iso


class DocumentStoreService:
    def __init__(self, redis):
        self.redis = redis
        self.doc_index_key = "doc:index"

    def _doc_key(self, doc_id: str) -> str:
        return f"doc:{doc_id}"

    def _source_key(self, source_key: str) -> str:
        return f"doc:source:{source_key}"

    def _rev_key(self, revision_id: str) -> str:
        return f"doc_rev:{revision_id}"

    def _rev_index_key(self, doc_id: str) -> str:
        return f"doc_rev:index:{doc_id}"

    async def get_or_create_document(
        self,
        source_key: str,
        source_type: str,
        title: str,
        project: str,
    ) -> dict:
        mapped = await self.redis.get(self._source_key(source_key))
        now = now_iso()
        if mapped:
            raw = await self.redis.get(self._doc_key(mapped))
            if raw:
                payload = json.loads(raw)
                payload["title"] = title or payload.get("title") or "untitled"
                payload["project"] = project or payload.get("project") or "unknown"
                payload["updated_at"] = now
                await self.redis.set(self._doc_key(mapped), json.dumps(payload))
                return payload

        doc_id = new_id()
        payload = {
            "document_id": doc_id,
            "source_key": source_key,
            "source_type": source_type,
            "title": title or "untitled",
            "project": project or "unknown",
            "status": "created",
            "current_revision_id": None,
            "revision_count": 0,
            "created_at": now,
            "updated_at": now,
            "last_ingested_at": None,
            # TODO(security): ACL principal list 계산/동기화
            "acl_todo": True,
        }
        await self.redis.set(self._doc_key(doc_id), json.dumps(payload))
        await self.redis.set(self._source_key(source_key), doc_id)
        await self.redis.sadd(self.doc_index_key, doc_id)
        return payload

    async def get_document(self, doc_id: str) -> Optional[dict]:
        raw = await self.redis.get(self._doc_key(doc_id))
        return json.loads(raw) if raw else None

    async def get_document_by_source_key(self, source_key: str) -> Optional[dict]:
        doc_id = await self.redis.get(self._source_key(source_key))
        if not doc_id:
            return None
        return await self.get_document(doc_id)

    async def get_current_revision(self, doc_id: str) -> Optional[dict]:
        doc = await self.get_document(doc_id)
        if not doc:
            return None
        rev_id = doc.get("current_revision_id")
        if not rev_id:
            return None
        raw = await self.redis.get(self._rev_key(rev_id))
        return json.loads(raw) if raw else None

    async def create_revision(
        self,
        doc_id: str,
        content_hash: str,
        object_name: str,
        source_file: str,
    ) -> dict:
        rev_id = new_id()
        payload = {
            "revision_id": rev_id,
            "document_id": doc_id,
            "content_hash": content_hash,
            "object_name": object_name,
            "source_file": source_file,
            "status": "queued",
            "chunk_count": 0,
            "created_at": now_iso(),
            "indexed_at": None,
            "error_message": None,
        }
        await self.redis.set(self._rev_key(rev_id), json.dumps(payload))
        await self.redis.lpush(self._rev_index_key(doc_id), rev_id)
        return payload

    async def update_revision_status(
        self,
        revision_id: str,
        status: str,
        chunk_count: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Optional[dict]:
        raw = await self.redis.get(self._rev_key(revision_id))
        if not raw:
            return None
        payload = json.loads(raw)
        payload["status"] = status
        if chunk_count is not None:
            payload["chunk_count"] = int(chunk_count)
        if error_message:
            payload["error_message"] = error_message
        if status == "indexed":
            payload["indexed_at"] = now_iso()
        await self.redis.set(self._rev_key(revision_id), json.dumps(payload))
        return payload

    async def activate_revision(self, doc_id: str, revision_id: str, status: str = "indexed") -> Optional[dict]:
        doc = await self.get_document(doc_id)
        if not doc:
            return None
        doc["current_revision_id"] = revision_id
        doc["status"] = status
        doc["revision_count"] = int(doc.get("revision_count") or 0) + 1
        doc["last_ingested_at"] = now_iso()
        doc["updated_at"] = now_iso()
        await self.redis.set(self._doc_key(doc_id), json.dumps(doc))
        return doc

    async def list_documents(self, page: int, per_page: int) -> dict:
        ids = list(await self.redis.smembers(self.doc_index_key))
        ids.sort()
        start = (page - 1) * per_page
        end = start + per_page
        items = []
        for doc_id in ids[start:end]:
            raw = await self.redis.get(self._doc_key(doc_id))
            if raw:
                items.append(json.loads(raw))
        return {"items": items, "total": len(ids), "page": page, "per_page": per_page}

    async def list_revisions(self, doc_id: str, limit: int = 50) -> list[dict]:
        rev_ids = await self.redis.lrange(self._rev_index_key(doc_id), 0, max(0, limit - 1))
        out = []
        for rid in rev_ids:
            raw = await self.redis.get(self._rev_key(rid))
            if raw:
                out.append(json.loads(raw))
        return out

    async def delete_document(self, doc_id: str) -> bool:
        doc = await self.get_document(doc_id)
        if not doc:
            return False

        rev_ids = await self.redis.lrange(self._rev_index_key(doc_id), 0, -1)
        if rev_ids:
            rev_keys = [self._rev_key(rid) for rid in rev_ids]
            await self.redis.delete(*rev_keys)

        await self.redis.delete(self._rev_index_key(doc_id))
        await self.redis.delete(self._doc_key(doc_id))
        await self.redis.srem(self.doc_index_key, doc_id)

        source_key = doc.get("source_key")
        if source_key:
            await self.redis.delete(self._source_key(source_key))
        return True

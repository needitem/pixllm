import json
from ...utils.ids import new_id
from ...utils.time import now_iso


class KnowledgeService:
    def __init__(self, redis):
        self.redis = redis
        self.index_key = "kb:index"

    async def list(self, page: int, per_page: int):
        ids = list(await self.redis.smembers(self.index_key))
        ids.sort()
        start = (page - 1) * per_page
        end = start + per_page
        items = []
        for kid in ids[start:end]:
            raw = await self.redis.get(f"kb:{kid}")
            if raw:
                items.append(json.loads(raw))
        return {"items": items, "total": len(ids), "page": page, "per_page": per_page}

    async def get(self, kid: str):
        raw = await self.redis.get(f"kb:{kid}")
        return json.loads(raw) if raw else None

    async def create(self, data: dict):
        kid = new_id()
        payload = {
            "id": kid,
            "name": data["name"],
            "description": data.get("description"),
            "collection": data.get("collection", "documents"),
            "files": data.get("files", []),
            "file_count": len(data.get("files", [])),
            "created_at": now_iso(),
        }
        await self.redis.set(f"kb:{kid}", json.dumps(payload))
        await self.redis.sadd(self.index_key, kid)
        return payload

    async def update(self, kid: str, data: dict):
        raw = await self.redis.get(f"kb:{kid}")
        if not raw:
            return None
        payload = json.loads(raw)
        for k, v in data.items():
            if v is not None:
                payload[k] = v
        payload["file_count"] = len(payload.get("files", []))
        await self.redis.set(f"kb:{kid}", json.dumps(payload))
        return payload

    async def delete(self, kid: str):
        await self.redis.delete(f"kb:{kid}")
        await self.redis.srem(self.index_key, kid)
        return True

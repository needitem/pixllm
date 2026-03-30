import json
from ...utils.ids import new_id
from ...utils.time import now_iso


class PromptsService:
    def __init__(self, redis):
        self.redis = redis
        self.index_key = "prompt:index"

    async def list(self, page: int, per_page: int):
        ids = list(await self.redis.smembers(self.index_key))
        ids.sort()
        start = (page - 1) * per_page
        end = start + per_page
        items = []
        for pid in ids[start:end]:
            raw = await self.redis.get(f"prompt:{pid}")
            if raw:
                items.append(json.loads(raw))
        return {"items": items, "total": len(ids), "page": page, "per_page": per_page}

    async def get(self, pid: str):
        raw = await self.redis.get(f"prompt:{pid}")
        return json.loads(raw) if raw else None

    async def create(self, data: dict):
        pid = new_id()
        payload = {
            "id": pid,
            "title": data["title"],
            "content": data["content"],
            "variables": data.get("variables", []),
            "tags": data.get("tags", []),
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        await self.redis.set(f"prompt:{pid}", json.dumps(payload))
        await self.redis.sadd(self.index_key, pid)
        return payload

    async def update(self, pid: str, data: dict):
        raw = await self.redis.get(f"prompt:{pid}")
        if not raw:
            return None
        payload = json.loads(raw)
        for k, v in data.items():
            if v is not None:
                payload[k] = v
        payload["updated_at"] = now_iso()
        await self.redis.set(f"prompt:{pid}", json.dumps(payload))
        return payload

    async def delete(self, pid: str):
        await self.redis.delete(f"prompt:{pid}")
        await self.redis.srem(self.index_key, pid)
        return True

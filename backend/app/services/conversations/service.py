import json
from typing import List, Optional

from ...utils.time import now_iso
from ...utils.ids import new_id
from ... import config


class ConversationsService:
    def __init__(self, redis):
        self.redis = redis

    async def list(self, page: int, per_page: int):
        keys = await self.redis.keys("conversation:*")
        keys.sort()
        start = (page - 1) * per_page
        end = start + per_page
        items = []
        for k in keys[start:end]:
            data = json.loads(await self.redis.get(k))
            items.append({
                "id": data["id"],
                "title": data.get("title", ""),
                "model": data.get("model", ""),
                "message_count": len(data.get("messages", [])),
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
            })
        return {"items": items, "total": len(keys), "page": page, "per_page": per_page}

    async def get(self, conv_id: str):
        raw = await self.redis.get(f"conversation:{conv_id}")
        if not raw:
            return None
        return json.loads(raw)

    async def delete(self, conv_id: str):
        await self.redis.delete(f"conversation:{conv_id}")
        return True

    async def append_message(self, conv_id: Optional[str], model: str, role: str, content: str, sources=None):
        if not conv_id:
            conv_id = new_id()
        key = f"conversation:{conv_id}"
        raw = await self.redis.get(key)
        if raw:
            data = json.loads(raw)
        else:
            data = {
                "id": conv_id,
                "title": content[:30],
                "model": model,
                "messages": [],
                "created_at": now_iso(),
                "updated_at": now_iso(),
            }
        data["messages"].append({
            "role": role,
            "content": content,
            "timestamp": now_iso(),
            "sources": sources or [],
        })
        # enforce max history
        data["messages"] = data["messages"][-config.MAX_CONVERSATION_MESSAGES:]
        data["updated_at"] = now_iso()
        await self.redis.set(key, json.dumps(data))
        return conv_id

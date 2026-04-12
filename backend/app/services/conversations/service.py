import json
from typing import Any, Dict, List, Optional

from ...utils.time import now_iso
from ...utils.ids import new_id
from ... import config


class ConversationsService:
    def __init__(self, redis):
        self.redis = redis

    @staticmethod
    def _conversation_key(conv_id: str) -> str:
        return f"conversation:{str(conv_id or '').strip()}"

    @staticmethod
    def _session_key(session_id: str) -> str:
        return f"conversation_session:{str(session_id or '').strip()}"

    @staticmethod
    def _normalize_message(
        role: str,
        content: str,
        *,
        timestamp: Optional[str] = None,
        sources: Optional[List[dict]] = None,
    ) -> dict:
        return {
            "role": str(role or "").strip(),
            "content": str(content or ""),
            "timestamp": str(timestamp or now_iso()),
            "sources": list(sources or []),
        }

    @staticmethod
    def _normalize_messages(messages: Optional[List[Dict[str, Any]]]) -> List[dict]:
        normalized: List[dict] = []
        for item in list(messages or []):
            role = str((item or {}).get("role") or "").strip()
            content = str((item or {}).get("content") or "")
            if not role:
                continue
            normalized.append(
                ConversationsService._normalize_message(
                    role,
                    content,
                    timestamp=(item or {}).get("timestamp"),
                    sources=(item or {}).get("sources"),
                )
            )
        return normalized[-config.MAX_CONVERSATION_MESSAGES:]

    @staticmethod
    def _title_from_messages(messages: Optional[List[Dict[str, Any]]], fallback: str = "") -> str:
        for item in list(messages or []):
            role = str((item or {}).get("role") or "").strip().lower()
            content = str((item or {}).get("content") or "").strip()
            if role == "user" and content:
                return content[:30]
        return str(fallback or "").strip()[:30]

    async def _save(self, data: Dict[str, Any]) -> dict:
        session_id = str(data.get("session_id") or "").strip()
        key = self._conversation_key(str(data.get("id") or ""))
        await self.redis.set(key, json.dumps(data))
        if session_id:
            await self.redis.set(self._session_key(session_id), str(data.get("id") or "").strip())
        return data

    async def list(self, page: int, per_page: int, session_id: str = ""):
        keys = await self.redis.keys("conversation:*")
        keys.sort()
        items = []
        target_session_id = str(session_id or "").strip()
        for k in keys:
            data = json.loads(await self.redis.get(k))
            if target_session_id and str(data.get("session_id") or "").strip() != target_session_id:
                continue
            items.append({
                "id": data["id"],
                "title": data.get("title", ""),
                "model": data.get("model", ""),
                "session_id": data.get("session_id", ""),
                "message_count": len(data.get("messages", [])),
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
            })
        total = len(items)
        items.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        start = (page - 1) * per_page
        end = start + per_page
        return {"items": items[start:end], "total": total, "page": page, "per_page": per_page}

    async def get(self, conv_id: str):
        raw = await self.redis.get(self._conversation_key(conv_id))
        if not raw:
            return None
        return json.loads(raw)

    async def get_by_session(self, session_id: str):
        normalized_session_id = str(session_id or "").strip()
        if not normalized_session_id:
            return None
        conversation_id = await self.redis.get(self._session_key(normalized_session_id))
        if not conversation_id:
            return None
        return await self.get(str(conversation_id))

    async def delete(self, conv_id: str):
        data = await self.get(conv_id)
        if data:
            session_id = str(data.get("session_id") or "").strip()
            if session_id:
                current = await self.redis.get(self._session_key(session_id))
                if str(current or "").strip() == str(conv_id or "").strip():
                    await self.redis.delete(self._session_key(session_id))
        await self.redis.delete(self._conversation_key(conv_id))
        return True

    async def ensure_conversation(
        self,
        *,
        conv_id: Optional[str],
        session_id: Optional[str],
        model: str,
        title: str = "",
    ) -> dict:
        normalized_conv_id = str(conv_id or "").strip()
        normalized_session_id = str(session_id or "").strip()
        if not normalized_conv_id and normalized_session_id:
            normalized_conv_id = str(
                await self.redis.get(self._session_key(normalized_session_id)) or ""
            ).strip()

        if normalized_conv_id:
            existing = await self.get(normalized_conv_id)
            if existing:
                previous_session_id = str(existing.get("session_id") or "").strip()
                if normalized_session_id and previous_session_id != normalized_session_id:
                    if previous_session_id:
                        current = await self.redis.get(self._session_key(previous_session_id))
                        if str(current or "").strip() == normalized_conv_id:
                            await self.redis.delete(self._session_key(previous_session_id))
                    existing["session_id"] = normalized_session_id
                if model:
                    existing["model"] = model
                if title and not str(existing.get("title") or "").strip():
                    existing["title"] = str(title or "").strip()[:30]
                existing["updated_at"] = now_iso()
                return await self._save(existing)

        conversation_id = normalized_conv_id or new_id()
        payload = {
            "id": conversation_id,
            "title": str(title or "").strip()[:30],
            "model": str(model or "").strip(),
            "session_id": normalized_session_id,
            "messages": [],
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        return await self._save(payload)

    async def replace_messages(
        self,
        *,
        conv_id: str,
        session_id: Optional[str],
        model: str,
        messages: List[Dict[str, Any]],
        title: str = "",
    ) -> dict:
        data = await self.ensure_conversation(
            conv_id=conv_id,
            session_id=session_id,
            model=model,
            title=title,
        )
        normalized_messages = self._normalize_messages(messages)
        derived_title = self._title_from_messages(normalized_messages, fallback=title)
        data["messages"] = normalized_messages
        data["model"] = str(model or data.get("model") or "").strip()
        data["session_id"] = str(session_id or data.get("session_id") or "").strip()
        data["title"] = derived_title or str(data.get("title") or "").strip()
        data["updated_at"] = now_iso()
        return await self._save(data)

    async def append_message(
        self,
        conv_id: Optional[str],
        model: str,
        role: str,
        content: str,
        sources=None,
        session_id: Optional[str] = None,
    ) -> dict:
        data = await self.ensure_conversation(
            conv_id=conv_id,
            session_id=session_id,
            model=model,
            title=content[:30],
        )
        data["messages"].append(
            self._normalize_message(role, content, timestamp=now_iso(), sources=sources)
        )
        data["messages"] = self._normalize_messages(data.get("messages") or [])
        data["title"] = self._title_from_messages(data["messages"], fallback=str(data.get("title") or ""))
        data["model"] = str(model or data.get("model") or "").strip()
        data["updated_at"] = now_iso()
        return await self._save(data)

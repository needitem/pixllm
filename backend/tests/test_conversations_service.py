import fnmatch
import os
import sys
import unittest


BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.services.conversations.history import merge_conversation_messages  # noqa: E402
from app.services.conversations.service import ConversationsService  # noqa: E402


class FakeRedis:
    def __init__(self):
        self.store = {}

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value):
        self.store[key] = value
        return True

    async def delete(self, key):
        self.store.pop(key, None)
        return True

    async def keys(self, pattern):
        return sorted(key for key in self.store if fnmatch.fnmatch(key, pattern))


class ConversationHistoryTests(unittest.TestCase):
    def test_merge_conversation_messages_deduplicates_full_history_overlap(self):
        stored = [
            {"role": "system", "content": "You are concise."},
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ]
        request = [
            {"role": "system", "content": "You are concise."},
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
            {"role": "user", "content": "continue"},
        ]

        merged = merge_conversation_messages(stored, request)

        self.assertEqual(
            merged,
            [
                {"role": "system", "content": "You are concise."},
                {"role": "user", "content": "hello"},
                {"role": "assistant", "content": "hi"},
                {"role": "user", "content": "continue"},
            ],
        )


class ConversationsServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.redis = FakeRedis()
        self.service = ConversationsService(self.redis)

    async def test_session_id_reuses_active_conversation(self):
        created = await self.service.ensure_conversation(
            conv_id=None,
            session_id="session-1",
            model="demo-model",
            title="hello world",
        )
        await self.service.replace_messages(
            conv_id=created["id"],
            session_id="session-1",
            model="demo-model",
            messages=[{"role": "user", "content": "hello world"}],
        )

        resolved = await self.service.ensure_conversation(
            conv_id=None,
            session_id="session-1",
            model="demo-model",
        )

        self.assertEqual(resolved["id"], created["id"])

        updated = await self.service.append_message(
            created["id"],
            "demo-model",
            "assistant",
            "response",
            session_id="session-1",
        )

        self.assertEqual(updated["session_id"], "session-1")
        self.assertEqual(len(updated["messages"]), 2)
        self.assertEqual(updated["messages"][0]["content"], "hello world")
        self.assertEqual(updated["messages"][1]["content"], "response")

        by_session = await self.service.get_by_session("session-1")
        self.assertIsNotNone(by_session)
        self.assertEqual(by_session["id"], created["id"])

    async def test_list_filters_by_session_id(self):
        first = await self.service.ensure_conversation(
            conv_id=None,
            session_id="session-a",
            model="demo-model",
            title="first",
        )
        second = await self.service.ensure_conversation(
            conv_id=None,
            session_id="session-b",
            model="demo-model",
            title="second",
        )
        await self.service.replace_messages(
            conv_id=first["id"],
            session_id="session-a",
            model="demo-model",
            messages=[{"role": "user", "content": "first"}],
        )
        await self.service.replace_messages(
            conv_id=second["id"],
            session_id="session-b",
            model="demo-model",
            messages=[{"role": "user", "content": "second"}],
        )

        filtered = await self.service.list(page=1, per_page=20, session_id="session-b")

        self.assertEqual(filtered["total"], 1)
        self.assertEqual(len(filtered["items"]), 1)
        self.assertEqual(filtered["items"][0]["id"], second["id"])


if __name__ == "__main__":
    unittest.main()

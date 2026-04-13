import asyncio
import os
import sys
import unittest


BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.services.execution.runs import ExecutionRunsService  # noqa: E402


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.sets = {}

    async def get(self, key):
        return self.values.get(key)

    async def set(self, key, value):
        self.values[key] = value
        return True

    async def delete(self, key):
        removed = 0
        if key in self.values:
            self.values.pop(key, None)
            removed += 1
        if key in self.sets:
            self.sets.pop(key, None)
            removed += 1
        return removed

    async def sadd(self, key, *values):
        bucket = self.sets.setdefault(key, set())
        before = len(bucket)
        for value in values:
            bucket.add(str(value))
        return len(bucket) - before

    async def smembers(self, key):
        return set(self.sets.get(key, set()))


class ExecutionRunsServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.redis = FakeRedis()
        self.service = ExecutionRunsService(self.redis)

    async def test_resume_run_resets_requested_tail_only(self):
        run = await self.service.create_run(
            session_id="session-1",
            conversation_id="conv-1",
            model="demo-model",
            user_message="hello",
        )

        await self.service.upsert_task(
            run["run_id"],
            "plan",
            title="Plan",
            status="completed",
            owner_agent="planner",
        )
        await self.service.upsert_step(
            run["run_id"],
            "plan",
            "plan-outline",
            title="Outline",
            kind="phase",
            status="completed",
            owner_agent="planner",
        )
        await self.service.upsert_task(
            run["run_id"],
            "answer",
            title="Answer",
            status="completed",
            owner_agent="presenter",
        )
        await self.service.upsert_step(
            run["run_id"],
            "answer",
            "answer-draft",
            title="Draft",
            kind="phase",
            status="completed",
            owner_agent="presenter",
        )
        await self.service.update_run(run["run_id"], status="completed")

        resumed = await self.service.resume_run(run["run_id"], from_task_key="answer")

        self.assertEqual(resumed["status"], "running")
        self.assertEqual(resumed["cancel_requested"], False)
        self.assertIsNone(resumed["finished_at"])

        tasks = {task["task_key"]: task for task in resumed["tasks"]}
        self.assertEqual(tasks["plan"]["status"], "completed")
        self.assertEqual(tasks["answer"]["status"], "pending")
        self.assertIsNone(tasks["answer"]["finished_at"])
        self.assertEqual(tasks["answer"]["steps"][0]["status"], "pending")

    async def test_create_and_resolve_approval_persists_reviewer_metadata(self):
        run = await self.service.create_run(
            session_id="session-2",
            conversation_id=None,
            model="demo-model",
            user_message="needs approval",
        )

        approval = await self.service.create_approval(
            run["run_id"],
            approval_type="execution_plan",
            title="Approval required",
            reason="risk gate",
            owner_agent="planner",
            metadata={"risk_class": "moderate"},
        )
        resolved = await self.service.update_approval(
            run["run_id"],
            approval["approval_id"],
            status="approved",
            reviewer="desktop",
            note="looks good",
        )

        self.assertEqual(resolved["status"], "approved")
        self.assertEqual(resolved["metadata"]["reviewer"], "desktop")
        self.assertEqual(resolved["metadata"]["note"], "looks good")
        self.assertEqual(resolved["metadata"]["risk_class"], "moderate")

    async def test_list_orders_runs_by_created_at_descending(self):
        first = await self.service.create_run(
            session_id="session-a",
            conversation_id=None,
            model="demo-model",
            user_message="first",
        )
        await asyncio.sleep(0.002)
        second = await self.service.create_run(
            session_id="session-b",
            conversation_id=None,
            model="demo-model",
            user_message="second",
        )

        data = await self.service.list(page=1, per_page=10)

        self.assertEqual(data["total"], 2)
        self.assertEqual(data["items"][0]["run_id"], second["run_id"])
        self.assertEqual(data["items"][1]["run_id"], first["run_id"])


if __name__ == "__main__":
    unittest.main()

import asyncio
import json
from typing import Any, Dict, List, Optional

try:
    from redis.exceptions import WatchError
except Exception:  # pragma: no cover - lightweight test doubles may omit redis
    class WatchError(Exception):
        pass

from ...utils.ids import new_id
from ...utils.time import now_iso


class ExecutionRunsService:
    _TERMINAL_STATUSES = {"completed", "failed", "cancelled"}

    def __init__(self, redis):
        self.redis = redis
        self.index_key = "run:index"
        self._locks: Dict[str, asyncio.Lock] = {}

    def _run_key(self, run_id: str) -> str:
        return f"run:{run_id}"

    def _run_lock(self, run_id: str) -> asyncio.Lock:
        lock = self._locks.get(run_id)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[run_id] = lock
        return lock

    @staticmethod
    def _decode_payload(raw: Any) -> Optional[dict]:
        if raw in (None, ""):
            return None
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        return json.loads(raw)

    @staticmethod
    def _encode_payload(payload: dict) -> str:
        return json.dumps(payload, ensure_ascii=False, default=str)

    @classmethod
    def _is_terminal_status(cls, status: Any) -> bool:
        return str(status or "").strip().lower() in cls._TERMINAL_STATUSES

    @staticmethod
    def _merge_metadata(existing: Optional[Dict[str, Any]], updates: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        merged = dict(existing or {})
        merged.update(dict(updates or {}))
        return merged

    @staticmethod
    def _ensure_finished_at(record: dict, status: Any, field: str = "finished_at") -> None:
        if ExecutionRunsService._is_terminal_status(status):
            record[field] = now_iso()

    def _ensure_task(
        self,
        payload: dict,
        task_key: str,
        *,
        title: str,
        status: str,
        owner_agent: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> tuple[list[dict], dict, bool]:
        tasks = list(payload.get("tasks") or [])
        task = next((row for row in tasks if str(row.get("task_key") or "") == task_key), None)
        created = False
        if task is None:
            timestamp = now_iso()
            task = {
                "task_id": new_id(),
                "task_key": task_key,
                "title": title,
                "status": status,
                "owner_agent": owner_agent,
                "created_at": timestamp,
                "started_at": timestamp,
                "finished_at": None,
                "steps": [],
                "metadata": dict(metadata or {}),
            }
            tasks.append(task)
            created = True
        return tasks, task, created

    async def _load(self, run_id: str) -> Optional[dict]:
        raw = await self.redis.get(self._run_key(run_id))
        return self._decode_payload(raw)

    async def _save(self, payload: dict) -> dict:
        payload["updated_at"] = now_iso()
        await self.redis.set(self._run_key(payload["run_id"]), self._encode_payload(payload))
        await self.redis.sadd(self.index_key, payload["run_id"])
        return payload

    def _save_via_pipe(self, pipe, payload: dict) -> dict:
        payload["updated_at"] = now_iso()
        pipe.set(self._run_key(payload["run_id"]), self._encode_payload(payload))
        pipe.sadd(self.index_key, payload["run_id"])
        return payload

    async def _mutate(self, run_id: str, mutate) -> Optional[dict]:
        if callable(getattr(self.redis, "pipeline", None)):
            while True:
                async with self.redis.pipeline(transaction=True) as pipe:
                    try:
                        await pipe.watch(self._run_key(run_id))
                        payload = self._decode_payload(await pipe.get(self._run_key(run_id)))
                        if payload is None:
                            return None
                        updated = mutate(payload) or payload
                        pipe.multi()
                        updated = self._save_via_pipe(pipe, updated)
                        await pipe.execute()
                        return updated
                    except WatchError:
                        continue
                    finally:
                        try:
                            await pipe.reset()
                        except Exception:
                            pass

        async with self._run_lock(run_id):
            payload = await self._load(run_id)
            if payload is None:
                return None
            updated = mutate(payload) or payload
            return await self._save(updated)

    async def create_run(
        self,
        *,
        session_id: str,
        conversation_id: Optional[str],
        model: str,
        user_message: str,
        response_type: str = "",
        owner_agent: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> dict:
        timestamp = now_iso()
        payload = {
            "run_id": new_id(),
            "session_id": str(session_id or "").strip(),
            "conversation_id": str(conversation_id or "").strip() or None,
            "model": str(model or "").strip(),
            "user_message": str(user_message or ""),
            "response_type": str(response_type or "").strip(),
            "owner_agent": str(owner_agent or "").strip(),
            "status": "running",
            "created_at": timestamp,
            "updated_at": timestamp,
            "started_at": timestamp,
            "finished_at": None,
            "cancel_requested": False,
            "tasks": [],
            "artifacts": [],
            "agents": [],
            "handoffs": [],
            "approvals": [],
            "metadata": self._merge_metadata(None, metadata),
        }
        return await self._save(payload)

    async def get(self, run_id: str) -> Optional[dict]:
        return await self._load(run_id)

    async def list(self, page: int, per_page: int) -> dict:
        ids = list(await self.redis.smembers(self.index_key))
        rows: List[dict] = []
        for run_id in ids:
            payload = await self._load(str(run_id))
            if payload:
                rows.append(payload)
        rows.sort(key=lambda row: str(row.get("created_at") or ""), reverse=True)
        start = (max(1, int(page)) - 1) * max(1, int(per_page))
        end = start + max(1, int(per_page))
        return {
            "items": rows[start:end],
            "total": len(rows),
            "page": max(1, int(page)),
            "per_page": max(1, int(per_page)),
        }

    async def update_run(self, run_id: str, **patch: Any) -> Optional[dict]:
        def mutate(payload: dict) -> dict:
            next_patch = dict(patch)
            if "metadata" in next_patch and isinstance(next_patch["metadata"], dict):
                payload["metadata"] = self._merge_metadata(payload.get("metadata"), next_patch.pop("metadata"))

            for key, value in next_patch.items():
                payload[key] = value

            if self._is_terminal_status(payload.get("status")) and not payload.get("finished_at"):
                payload["finished_at"] = now_iso()
            return payload

        return await self._mutate(run_id, mutate)

    async def upsert_task(
        self,
        run_id: str,
        task_key: str,
        *,
        title: str,
        status: str,
        owner_agent: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[dict]:
        holder: Dict[str, dict] = {}

        def mutate(payload: dict) -> dict:
            tasks, task, created = self._ensure_task(
                payload,
                task_key,
                title=title,
                status=status,
                owner_agent=owner_agent,
                metadata=metadata,
            )
            if not created:
                task["title"] = title or task.get("title") or task_key
                existing_status = str(task.get("status") or "").strip().lower()
                incoming_status = str(status or "").strip().lower()
                task["status"] = (
                    existing_status
                    if incoming_status == "pending" and existing_status in {"running", *self._TERMINAL_STATUSES}
                    else status
                )
                task["owner_agent"] = owner_agent or task.get("owner_agent") or ""
                task["metadata"] = self._merge_metadata(task.get("metadata"), metadata)
                if not task.get("started_at"):
                    task["started_at"] = now_iso()
            self._ensure_finished_at(task, task.get("status"))
            payload["tasks"] = tasks
            holder["task"] = dict(task)
            return payload

        saved = await self._mutate(run_id, mutate)
        if not saved:
            return None
        return holder.get("task")

    async def upsert_step(
        self,
        run_id: str,
        task_key: str,
        step_key: str,
        *,
        title: str,
        kind: str,
        status: str,
        owner_agent: str = "",
        input_data: Any = None,
        output_preview: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[dict]:
        holder: Dict[str, dict] = {}

        def mutate(payload: dict) -> dict:
            tasks, task, _ = self._ensure_task(
                payload,
                task_key,
                title=task_key,
                status="running",
                owner_agent=owner_agent,
            )
            steps = list(task.get("steps") or [])
            step = next((row for row in steps if str(row.get("step_key") or "") == step_key), None)
            if step is None:
                timestamp = now_iso()
                step = {
                    "step_id": new_id(),
                    "step_key": step_key,
                    "title": title,
                    "kind": kind,
                    "status": status,
                    "owner_agent": owner_agent,
                    "created_at": timestamp,
                    "started_at": timestamp,
                    "finished_at": None,
                    "input": input_data,
                    "output_preview": output_preview,
                    "metadata": dict(metadata or {}),
                }
                steps.append(step)
            else:
                step["title"] = title or step.get("title") or step_key
                step["kind"] = kind or step.get("kind") or ""
                step["status"] = status
                step["owner_agent"] = owner_agent or step.get("owner_agent") or ""
                if input_data is not None:
                    step["input"] = input_data
                if output_preview:
                    step["output_preview"] = output_preview
                step["metadata"] = self._merge_metadata(step.get("metadata"), metadata)
                if not step.get("started_at"):
                    step["started_at"] = now_iso()

            self._ensure_finished_at(step, status)

            task["steps"] = steps
            payload["tasks"] = tasks
            holder["step"] = dict(step)
            return payload

        saved = await self._mutate(run_id, mutate)
        if not saved:
            return None
        return holder.get("step")

    async def append_step(
        self,
        run_id: str,
        task_key: str,
        *,
        title: str,
        kind: str,
        status: str,
        owner_agent: str = "",
        input_data: Any = None,
        output_preview: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[dict]:
        unique_key = f"{task_key}:{kind}:{new_id()}"
        return await self.upsert_step(
            run_id,
            task_key,
            unique_key,
            title=title,
            kind=kind,
            status=status,
            owner_agent=owner_agent,
            input_data=input_data,
            output_preview=output_preview,
            metadata=metadata,
        )

    async def add_artifact(
        self,
        run_id: str,
        *,
        artifact_type: str,
        title: str,
        content: Any,
        owner_agent: str = "",
        task_key: Optional[str] = None,
        step_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[dict]:
        holder: Dict[str, dict] = {}

        def mutate(payload: dict) -> dict:
            artifact = {
                "artifact_id": new_id(),
                "type": artifact_type,
                "title": title,
                "content": content,
                "owner_agent": owner_agent,
                "task_key": task_key,
                "step_key": step_key,
                "created_at": now_iso(),
                "metadata": self._merge_metadata(None, metadata),
            }
            payload["artifacts"] = [*(payload.get("artifacts") or []), artifact]
            holder["artifact"] = dict(artifact)
            return payload

        saved = await self._mutate(run_id, mutate)
        if not saved:
            return None
        return holder.get("artifact")

    async def list_approvals(self, run_id: str) -> List[dict]:
        payload = await self._load(run_id)
        if not payload:
            return []
        return list(payload.get("approvals") or [])

    async def get_latest_approval(self, run_id: str, approval_type: str = "") -> Optional[dict]:
        approvals = await self.list_approvals(run_id)
        rows = [
            row
            for row in approvals
            if not approval_type or str(row.get("type") or "").strip().lower() == str(approval_type or "").strip().lower()
        ]
        if not rows:
            return None
        rows.sort(key=lambda row: str(row.get("created_at") or ""), reverse=True)
        return rows[0]

    async def get_latest_artifact(self, run_id: str, artifact_type: str = "", task_key: str = "") -> Optional[dict]:
        payload = await self._load(run_id)
        if not payload:
            return None
        rows = [
            row
            for row in list(payload.get("artifacts") or [])
            if (not artifact_type or str(row.get("type") or "").strip().lower() == str(artifact_type or "").strip().lower())
            and (not task_key or str(row.get("task_key") or "").strip().lower() == str(task_key or "").strip().lower())
        ]
        if not rows:
            return None
        rows.sort(key=lambda row: str(row.get("created_at") or ""), reverse=True)
        return rows[0]

    async def set_agents(self, run_id: str, agents: List[Dict[str, Any]]) -> Optional[dict]:
        return await self._mutate(
            run_id,
            lambda payload: {
                **payload,
                "agents": list(agents or []),
            },
        )

    async def add_handoff(
        self,
        run_id: str,
        *,
        from_agent: str,
        to_agent: str,
        reason: str,
        payload: Optional[Dict[str, Any]] = None,
        task_key: Optional[str] = None,
        step_key: Optional[str] = None,
    ) -> Optional[dict]:
        holder: Dict[str, dict] = {}

        def mutate(run: dict) -> dict:
            item = {
                "handoff_id": new_id(),
                "from_agent": str(from_agent or "").strip(),
                "to_agent": str(to_agent or "").strip(),
                "reason": str(reason or "").strip(),
                "payload": dict(payload or {}),
                "task_key": task_key,
                "step_key": step_key,
                "created_at": now_iso(),
            }
            run["handoffs"] = [*(run.get("handoffs") or []), item]
            holder["handoff"] = dict(item)
            return run

        saved = await self._mutate(run_id, mutate)
        if not saved:
            return None
        return holder.get("handoff")

    async def create_approval(
        self,
        run_id: str,
        *,
        approval_type: str,
        title: str,
        reason: str,
        owner_agent: str = "",
        task_key: Optional[str] = None,
        step_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[dict]:
        holder: Dict[str, dict] = {}

        def mutate(payload: dict) -> dict:
            approval = {
                "approval_id": new_id(),
                "type": approval_type,
                "title": title,
                "reason": reason,
                "status": "pending",
                "owner_agent": owner_agent,
                "task_key": task_key,
                "step_key": step_key,
                "created_at": now_iso(),
                "resolved_at": None,
                "metadata": self._merge_metadata(None, metadata),
            }
            payload["approvals"] = [*(payload.get("approvals") or []), approval]
            holder["approval"] = dict(approval)
            return payload

        saved = await self._mutate(run_id, mutate)
        if not saved:
            return None
        return holder.get("approval")

    async def update_approval(
        self,
        run_id: str,
        approval_id: str,
        *,
        status: str,
        reviewer: str = "",
        note: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[dict]:
        holder: Dict[str, Optional[dict]] = {"approval": None}

        def mutate(payload: dict) -> dict:
            approvals = list(payload.get("approvals") or [])
            approval = next((row for row in approvals if str(row.get("approval_id") or "") == approval_id), None)
            if approval is None:
                holder["approval"] = None
                return payload
            approval["status"] = str(status or approval.get("status") or "").strip().lower() or approval.get("status")
            approval["resolved_at"] = now_iso()
            merged = self._merge_metadata(approval.get("metadata"))
            if reviewer:
                merged["reviewer"] = reviewer
            if note:
                merged["note"] = note
            merged.update(dict(metadata or {}))
            approval["metadata"] = merged
            payload["approvals"] = approvals
            holder["approval"] = dict(approval)
            return payload

        saved = await self._mutate(run_id, mutate)
        if not saved:
            return None
        return holder.get("approval")

    async def request_cancel(self, run_id: str, reason: str = "") -> Optional[dict]:
        def mutate(payload: dict) -> dict:
            payload["cancel_requested"] = True
            payload["status"] = "cancelling" if str(payload.get("status") or "").lower() == "running" else payload.get("status")
            meta = dict(payload.get("metadata") or {})
            if reason:
                meta["cancel_reason"] = reason
            meta["cancel_requested_at"] = now_iso()
            payload["metadata"] = meta
            return payload

        return await self._mutate(run_id, mutate)

    async def is_cancel_requested(self, run_id: str) -> bool:
        payload = await self._load(run_id)
        if not payload:
            return False
        return bool(payload.get("cancel_requested"))

    async def resume_run(self, run_id: str, from_task_key: str = "", from_step_key: str = "") -> Optional[dict]:
        def mutate(payload: dict) -> dict:
            payload["cancel_requested"] = False
            payload["status"] = "running"
            payload["finished_at"] = None
            meta = dict(payload.get("metadata") or {})
            meta["resume_count"] = int(meta.get("resume_count") or 0) + 1
            if from_task_key:
                meta["resume_from_task_key"] = from_task_key
            if from_step_key:
                meta["resume_from_step_key"] = from_step_key
            meta["resumed_at"] = now_iso()
            payload["metadata"] = meta
            reset_from = str(from_task_key or "").strip().lower()
            if reset_from:
                reached_reset = False
                for task in list(payload.get("tasks") or []):
                    current_task_key = str(task.get("task_key") or "").strip().lower()
                    if current_task_key == reset_from:
                        reached_reset = True
                    if not reached_reset:
                        continue
                    task["status"] = "pending"
                    task["finished_at"] = None
                    reached_step_reset = not from_step_key or current_task_key != reset_from
                    for step in list(task.get("steps") or []):
                        current_step_key = str(step.get("step_key") or "").strip().lower()
                        if not reached_step_reset and current_step_key == str(from_step_key).strip().lower():
                            reached_step_reset = True
                        if not reached_step_reset:
                            continue
                        step["status"] = "pending"
                        step["finished_at"] = None
            return payload

        return await self._mutate(run_id, mutate)

    async def seed_tasks(
        self,
        run_id: str,
        tasks: List[Dict[str, Any]],
    ) -> None:
        for task in list(tasks or []):
            task_key = str(task.get("task_key") or "").strip()
            if not task_key:
                continue
            await self.upsert_task(
                run_id,
                task_key,
                title=str(task.get("title") or task_key),
                status=str(task.get("status") or "pending"),
                owner_agent=str(task.get("owner_agent") or ""),
                metadata={
                    "depends_on": list(task.get("depends_on") or []),
                    "task_family": task.get("task_family"),
                    "execution_mode": task.get("execution_mode"),
                },
            )

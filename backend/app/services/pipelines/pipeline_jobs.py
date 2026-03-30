import json
import os
import socket
import threading
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional

import redis

from ... import config


_INDEX_KEY = "pipeline_job:index"
_KEY_PREFIX = "pipeline_job:"
_LOCAL_LOCK = threading.Lock()
_MAX_LOG_LINES = 500
_PROCESS_OWNER = f"{socket.gethostname()}:{os.getpid()}"
JobAction = Callable[[Dict[str, Any], Callable[[str], None]], Dict[str, Any] | None]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _trim_logs(lines: List[str]) -> List[str]:
    if len(lines) <= _MAX_LOG_LINES:
        return lines
    return lines[-_MAX_LOG_LINES:]


def _job_key(job_id: str) -> str:
    return f"{_KEY_PREFIX}{job_id}"


@lru_cache(maxsize=1)
def _get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(config.REDIS_URL, decode_responses=True)


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _encode_payload(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str)


def _decode_payload(raw: Any) -> Dict[str, Any]:
    if raw in (None, ""):
        return {}
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    return json.loads(raw)


def _save_job(client: redis.Redis, payload: Dict[str, Any]) -> Dict[str, Any]:
    payload["updated_at"] = _utc_now_iso()
    client.set(_job_key(payload["job_id"]), _encode_payload(payload))
    client.sadd(_INDEX_KEY, payload["job_id"])
    return dict(payload)


def _coerce_stale_job(client: redis.Redis, payload: Dict[str, Any]) -> Dict[str, Any]:
    status = str(payload.get("status") or "").strip().lower()
    stale_seconds = max(0, int(getattr(config, "PIPELINE_JOB_STALE_SECONDS", 0) or 0))
    if status not in {"queued", "running"} or stale_seconds <= 0:
        return payload

    heartbeat = _parse_iso(
        str(payload.get("last_heartbeat_at") or "").strip()
        or str(payload.get("started_at") or "").strip()
        or str(payload.get("created_at") or "").strip()
    )
    if heartbeat is None:
        return payload

    elapsed = (datetime.now(timezone.utc) - heartbeat).total_seconds()
    if elapsed < stale_seconds:
        return payload

    payload["status"] = "failed"
    payload["return_code"] = -1
    payload["completed_at"] = payload.get("completed_at") or _utc_now_iso()
    payload["error_message"] = "Pipeline job heartbeat expired. Please retry."
    payload["last_heartbeat_at"] = _utc_now_iso()
    return _save_job(client, payload)


def _load_job(client: redis.Redis, job_id: str, *, coerce_stale: bool = True) -> Dict[str, Any]:
    payload = _decode_payload(client.get(_job_key(job_id)))
    if not payload:
        return {}
    if coerce_stale:
        return _coerce_stale_job(client, payload)
    return payload


def _mutate_job(client: redis.Redis, job_id: str, mutate: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
    if hasattr(client, "pipeline"):
        while True:
            try:
                with client.pipeline() as pipe:
                    pipe.watch(_job_key(job_id))
                    payload = _decode_payload(pipe.get(_job_key(job_id)))
                    if not payload:
                        pipe.unwatch()
                        return {}
                    updated = mutate(payload) or payload
                    updated_at = _utc_now_iso()
                    pipe.multi()
                    pipe.set(_job_key(job_id), _encode_payload({**updated, "updated_at": updated_at}))
                    pipe.sadd(_INDEX_KEY, job_id)
                    pipe.execute()
                    updated["updated_at"] = updated_at
                    return dict(updated)
            except redis.WatchError:
                continue

    with _LOCAL_LOCK:
        payload = _load_job(client, job_id, coerce_stale=False)
        if not payload:
            return {}
        updated = mutate(payload) or payload
        return _save_job(client, updated)


def _touch_job(client: redis.Redis, job_id: str) -> Dict[str, Any]:
    return _mutate_job(
        client,
        job_id,
        lambda payload: {
            **payload,
            "last_heartbeat_at": _utc_now_iso(),
        },
    )


def _set_job_status(
    client: redis.Redis,
    job_id: str,
    *,
    status: str,
    return_code: Optional[int] = None,
    result: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
) -> Dict[str, Any]:
    now = _utc_now_iso()

    def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
        payload["status"] = status
        payload["last_heartbeat_at"] = now
        if status == "running":
            payload["started_at"] = payload.get("started_at") or now
        if status in {"succeeded", "failed", "cancelled"}:
            payload["completed_at"] = now
        if return_code is not None:
            payload["return_code"] = return_code
        if result is not None:
            payload["result"] = result
        if error_message is not None:
            payload["error_message"] = error_message
        return payload

    return _mutate_job(client, job_id, mutate)


def _append_log(client: redis.Redis, job_id: str, line: str) -> Dict[str, Any]:
    text = str(line)
    now = _utc_now_iso()

    def mutate(payload: Dict[str, Any]) -> Dict[str, Any]:
        current = list(payload.get("log_lines") or [])
        current.append(text)
        payload["log_lines"] = _trim_logs(current)
        payload["last_heartbeat_at"] = now
        return payload

    return _mutate_job(client, job_id, mutate)


def _heartbeat_loop(client: redis.Redis, job_id: str, stop_event: threading.Event) -> None:
    interval = max(1, int(getattr(config, "PIPELINE_JOB_HEARTBEAT_SECONDS", 10) or 10))
    while not stop_event.wait(interval):
        payload = _touch_job(client, job_id)
        if not payload or str(payload.get("status") or "").strip().lower() not in {"queued", "running"}:
            return


def _runner(job_id: str, action: JobAction, payload: Dict[str, Any]) -> None:
    client = _get_redis_client()
    stop_event = threading.Event()
    heartbeat_thread = threading.Thread(
        target=_heartbeat_loop,
        args=(client, job_id, stop_event),
        daemon=True,
    )

    def append_log(line: str) -> None:
        _append_log(client, job_id, line)

    _set_job_status(client, job_id, status="running")
    heartbeat_thread.start()

    try:
        result = action(payload, append_log) or {}
        _set_job_status(client, job_id, status="succeeded", return_code=0, result=result, error_message=None)
    except Exception as exc:
        append_log(f"[pipeline-error] {exc}")
        _set_job_status(
            client,
            job_id,
            status="failed",
            return_code=-1,
            result={},
            error_message=str(exc),
        )
    finally:
        stop_event.set()
        heartbeat_thread.join(timeout=1)


def start_job(name: str, action: JobAction, payload: Dict[str, Any]) -> Dict[str, Any]:
    job_id = str(uuid.uuid4())
    client = _get_redis_client()
    now = _utc_now_iso()
    _save_job(
        client,
        {
            "job_id": job_id,
            "name": name,
            "status": "queued",
            "payload": payload,
            "created_at": now,
            "updated_at": now,
            "started_at": None,
            "completed_at": None,
            "return_code": None,
            "log_lines": [],
            "result": None,
            "error_message": None,
            "last_heartbeat_at": now,
            "owner_id": _PROCESS_OWNER,
        },
    )

    thread = threading.Thread(
        target=_runner,
        args=(job_id, action, payload),
        daemon=True,
    )
    thread.start()
    return get_job(job_id)


def get_job(job_id: str) -> Dict[str, Any]:
    client = _get_redis_client()
    return _load_job(client, job_id)


def list_jobs(limit: int = 50) -> List[Dict[str, Any]]:
    client = _get_redis_client()
    capped = max(1, min(int(limit), 500))
    rows = []
    for job_id in list(client.smembers(_INDEX_KEY)):
        row = _load_job(client, str(job_id))
        if row:
            rows.append(row)
    rows.sort(key=lambda x: str(x.get("created_at") or ""), reverse=True)
    return [dict(r) for r in rows[:capped]]

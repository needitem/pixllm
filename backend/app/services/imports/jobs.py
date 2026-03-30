import json
from typing import Optional

from ...deps import state


IMPORT_INDEX_KEY = "import_job:index"
LOCAL_FOLDER_SESSION_KEY_PREFIX = "import_local_session:"
LOCAL_FOLDER_SESSION_TTL_SECONDS = 60 * 60 * 6


def read_job_payload(raw: Optional[str]) -> Optional[dict]:
    if not raw:
        return None
    return json.loads(raw)


async def save_job(job: dict):
    await state.redis.set(f"import_job:{job['job_id']}", json.dumps(job))
    await state.redis.sadd(IMPORT_INDEX_KEY, job["job_id"])


async def update_job(job_id: str, **patch):
    raw = await state.redis.get(f"import_job:{job_id}")
    payload = read_job_payload(raw)
    if not payload:
        return None
    payload.update(patch)
    await save_job(payload)
    return payload


async def is_cancel_requested(job_id: str) -> bool:
    raw = await state.redis.get(f"import_job:{job_id}")
    payload = read_job_payload(raw)
    if not payload:
        return False
    return bool(payload.get("cancel_requested", False))


def local_folder_session_key(session_id: str) -> str:
    return f"{LOCAL_FOLDER_SESSION_KEY_PREFIX}{session_id}"


async def get_local_folder_session(session_id: str) -> Optional[dict]:
    raw = await state.redis.get(local_folder_session_key(session_id))
    return read_job_payload(raw)


async def save_local_folder_session(session: dict):
    await state.redis.set(
        local_folder_session_key(session["session_id"]),
        json.dumps(session),
        ex=LOCAL_FOLDER_SESSION_TTL_SECONDS,
    )

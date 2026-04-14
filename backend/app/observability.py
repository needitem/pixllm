import json
import logging
import re
from datetime import datetime, timezone
from uuid import uuid4


REQUEST_ID_HEADER = "X-Request-ID"
_REQUEST_ID_RE = re.compile(r"[^A-Za-z0-9._:-]+")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_request_id(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return uuid4().hex
    normalized = _REQUEST_ID_RE.sub("-", raw).strip("-")
    if not normalized:
        return uuid4().hex
    return normalized[:128]


def request_id_from_request(request) -> str:
    headers = getattr(request, "headers", {}) or {}
    return normalize_request_id(
        headers.get(REQUEST_ID_HEADER)
        or headers.get(REQUEST_ID_HEADER.lower())
        or headers.get("x-request-id")
        or ""
    )


def request_id_headers(request) -> dict[str, str]:
    request_id = str(getattr(getattr(request, "state", None), "request_id", "") or "").strip()
    if not request_id:
        return {}
    return {REQUEST_ID_HEADER: request_id}


def configure_logger(name: str = "pixllm.api") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def _request_url_parts(request) -> tuple[str, str]:
    url = getattr(request, "url", None)
    if url is None:
        return "", ""
    path = str(getattr(url, "path", "") or "")
    query = str(getattr(url, "query", "") or "")
    return path, query


def _request_client_ip(request) -> str:
    client = getattr(request, "client", None)
    host = getattr(client, "host", "") if client is not None else ""
    return str(host or "")


def _request_headers_value(request, key: str) -> str:
    headers = getattr(request, "headers", {}) or {}
    return str(headers.get(key) or headers.get(key.lower()) or "")


def build_request_log(
    request,
    *,
    status_code: int,
    duration_ms: float,
    api_session: dict | None = None,
) -> dict:
    path, query = _request_url_parts(request)
    request_id = str(getattr(getattr(request, "state", None), "request_id", "") or "").strip()
    return {
        "event": "http_request",
        "timestamp": now_iso(),
        "request_id": request_id,
        "method": str(getattr(request, "method", "") or ""),
        "path": path,
        "query": query,
        "status_code": int(status_code),
        "duration_ms": round(float(duration_ms), 2),
        "client_ip": _request_client_ip(request),
        "user_agent": _request_headers_value(request, "user-agent"),
        "api_session_kind": str((api_session or {}).get("kind") or ""),
    }


def log_event(logger: logging.Logger, event: str, **fields) -> None:
    payload = {
        "event": str(event or "").strip() or "event",
        "timestamp": now_iso(),
        **fields,
    }
    logger.info(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def log_request(
    logger: logging.Logger,
    request,
    *,
    status_code: int,
    duration_ms: float,
    api_session: dict | None = None,
) -> None:
    logger.info(
        json.dumps(
            build_request_log(
                request,
                status_code=status_code,
                duration_ms=duration_ms,
                api_session=api_session,
            ),
            ensure_ascii=False,
            sort_keys=True,
        )
    )


def log_exception(logger: logging.Logger, request, exc: Exception) -> None:
    path, query = _request_url_parts(request)
    payload = {
        "event": "http_exception",
        "timestamp": now_iso(),
        "request_id": str(getattr(getattr(request, "state", None), "request_id", "") or "").strip(),
        "method": str(getattr(request, "method", "") or ""),
        "path": path,
        "query": query,
        "error_type": exc.__class__.__name__,
        "error_message": str(exc),
    }
    logger.exception(json.dumps(payload, ensure_ascii=False, sort_keys=True))

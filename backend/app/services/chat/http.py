from typing import Any, Dict

from fastapi import HTTPException
from fastapi.responses import JSONResponse


def raise_http_error(status_code: int, code: str, message: str, **extra: Any) -> None:
    detail: Dict[str, Any] = {"code": code, "message": message}
    for key, value in extra.items():
        if value is not None:
            detail[key] = value
    raise HTTPException(status_code=status_code, detail=detail)


def intent_failure_to_api_error(intent_resolution: Dict[str, Any]) -> Dict[str, Any] | None:
    source = str(intent_resolution.get("source") or "").strip().lower()
    if source != "intent_classification_failed":
        return None

    failure_reason = str(intent_resolution.get("failure_reason") or "").strip().lower()
    if failure_reason == "low_confidence":
        return {
            "status_code": 422,
            "code": "INTENT_CLASSIFICATION_LOW_CONFIDENCE",
            "message": "Intent classification confidence is below the required threshold.",
            "failure_reason": failure_reason,
        }
    if failure_reason in {"llm_unavailable", "llm_error"}:
        return {
            "status_code": 503,
            "code": "INTENT_CLASSIFIER_UNAVAILABLE",
            "message": "Intent classifier is currently unavailable.",
            "failure_reason": failure_reason,
        }
    return {
        "status_code": 503,
        "code": "INTENT_CLASSIFIER_INVALID_OUTPUT",
        "message": "Intent classifier returned invalid output.",
        "failure_reason": failure_reason or "invalid_output",
    }


def http_exception_to_json_response(exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict):
        body: Dict[str, Any] = {
            "code": str(detail.get("code") or "API_ERROR"),
            "message": str(detail.get("message") or "Request failed"),
        }
        for key in ("failure_reason", "run_id", "stage", "timeout_sec", "evidence_gate", "approval_id", "approval_type"):
            if detail.get(key) is not None:
                body[key] = detail.get(key)
        return JSONResponse(status_code=exc.status_code, content=body)
    fallback_code = "SERVICE_UNAVAILABLE" if int(exc.status_code) >= 500 else "BAD_REQUEST"
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": fallback_code, "message": str(detail or "Request failed")},
    )


def http_exception_to_error_payload(exc: HTTPException) -> Dict[str, Any]:
    detail = exc.detail
    if isinstance(detail, dict):
        payload: Dict[str, Any] = {
            "code": str(detail.get("code") or "API_ERROR"),
            "message": str(detail.get("message") or "Request failed"),
        }
        for key in ("failure_reason", "run_id", "stage", "timeout_sec", "evidence_gate", "approval_id", "approval_type"):
            if detail.get(key) is not None:
                payload[key] = detail.get(key)
        return payload
    fallback_code = "SERVICE_UNAVAILABLE" if int(exc.status_code) >= 500 else "BAD_REQUEST"
    return {"code": fallback_code, "message": str(detail or "Request failed")}

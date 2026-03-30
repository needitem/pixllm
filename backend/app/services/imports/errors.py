import asyncio


UPLOAD_ERROR_PAYLOAD_TOO_LARGE = (
    "PAYLOAD_TOO_LARGE",
    "파일 크기가 서버 제한을 초과합니다. 파일을 분할하거나 관리자에게 문의해 주세요.",
)
UPLOAD_ERROR_SERVER_ERROR = (
    "SERVER_ERROR",
    "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
)
UPLOAD_ERROR_CONNECTION_ABORTED = (
    "CONNECTION_ABORTED",
    "업로드 중 연결이 끊겼습니다. 네트워크 상태를 확인하고 다시 시도해 주세요.",
)
UPLOAD_ERROR_PERMISSION_DENIED = (
    "PERMISSION_DENIED",
    "파일 접근 권한이 없습니다. 관리자에게 문의해 주세요.",
)
UPLOAD_ERROR_TIMEOUT = (
    "UPLOAD_TIMEOUT",
    "업로드 처리 시간이 초과되었습니다. 파일 크기를 줄이거나 나중에 다시 시도해 주세요.",
)
UPLOAD_ERROR_UNKNOWN = (
    "UNKNOWN_ERROR",
    "업로드 처리 중 오류가 발생했습니다.",
)


def classify_upload_error(exc: BaseException) -> tuple[str, str]:
    msg_lower = str(exc).lower()

    if isinstance(exc, asyncio.TimeoutError):
        return UPLOAD_ERROR_TIMEOUT

    if isinstance(exc, PermissionError):
        return UPLOAD_ERROR_PERMISSION_DENIED
    if any(k in msg_lower for k in ("access denied", "accessdenied", "permission denied", "forbidden")):
        return UPLOAD_ERROR_PERMISSION_DENIED

    if any(k in msg_lower for k in ("connection aborted", "connection reset", "econnaborted", "broken pipe", "network error")):
        return UPLOAD_ERROR_CONNECTION_ABORTED

    if any(k in msg_lower for k in ("payload too large", "request entity too large", "content length", "max body", "too large")):
        return UPLOAD_ERROR_PAYLOAD_TOO_LARGE

    if any(k in msg_lower for k in ("internal server error", "bad gateway", "service unavailable", "500", "502", "503", "504")):
        return UPLOAD_ERROR_SERVER_ERROR

    return UPLOAD_ERROR_UNKNOWN


def format_svn_sync_error(stderr: str, svn_url: str, svn_username: str | None) -> str:
    message = (stderr or "unknown error").strip()
    lower = message.lower()

    if "can't get password" in lower:
        return f"SVN authentication required for '{svn_url}'. Provide svn_username and svn_password. detail: {message}"
    if "authentication error from server" in lower:
        account = svn_username or "<empty>"
        return f"SVN authentication failed for '{svn_url}' (username={account}). Check svn_username and svn_password. detail: {message}"
    if "e170013" in lower and "unable to connect" in lower:
        return f"SVN connection failed for '{svn_url}'. Check URL, network route, and svn daemon access. detail: {message}"
    return message

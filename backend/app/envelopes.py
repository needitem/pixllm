"""API 응답 봉투(envelope) 규약 모듈.

모든 엔드포인트는 성공/실패와 무관하게 동일한 형태의 JSON을 반환한다:
    {"ok": bool, "data": ..., "error": {"code": ..., "message": ...} | null}
프런트엔드가 HTTP 상태 코드를 일일이 분기하지 않고 `ok` 필드만 보면 되도록 하기 위한 규약이다.
"""

from typing import Any, Dict


def ok(data: Any) -> Dict[str, Any]:
    """성공 응답 봉투를 만든다. 실제 결과는 `data` 필드에 담긴다."""
    return {"ok": True, "data": data, "error": None}


def err(code: str, message: str) -> Dict[str, Any]:
    """실패 응답 봉투를 만든다.

    `code`는 프로그램이 분기할 수 있는 기계용 식별자(예: "NOT_FOUND"),
    `message`는 사람이 읽을 설명이다.
    """
    return {"ok": False, "data": None, "error": {"code": code, "message": message}}


class ApiError(Exception):
    """서비스 코드에서 던지는 표준 API 예외.

    어디서 raise하든 main.py의 예외 처리기가 잡아서
    `err(code, message)` 봉투 + `status_code` HTTP 응답으로 변환해 준다.
    즉, 서비스 레이어는 HTTP를 몰라도 이 예외만 던지면 된다.
    """

    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code

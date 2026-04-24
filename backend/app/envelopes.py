from typing import Any, Dict


def ok(data: Any) -> Dict[str, Any]:
    return {"ok": True, "data": data, "error": None}


def err(code: str, message: str) -> Dict[str, Any]:
    return {"ok": False, "data": None, "error": {"code": code, "message": message}}


class ApiError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


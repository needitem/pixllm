from fastapi import APIRouter, Depends

from ..deps import get_code_tools
from ..envelopes import ok


router = APIRouter()


@router.get("/tools/status")
def tools_status(code_tools=Depends(get_code_tools)):
    status = code_tools.status() if code_tools is not None else {
        "enabled": False,
        "rg_available": False,
        "roots_configured": [],
        "roots_available": [],
        "roots_missing": [],
    }
    return ok({
        "code_tools": status,
    })

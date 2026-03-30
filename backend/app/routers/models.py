import json
import urllib.request
from fastapi import APIRouter

from ..envelopes import ok, err
from .. import config


router = APIRouter()


@router.get("/models")
def models():
    try:
        with urllib.request.urlopen(f"{config.VLLM_URL}/v1/models", timeout=5) as r:
            data = json.load(r)
        return ok(data)
    except Exception:
        return err("LLM_UNAVAILABLE", "vLLM unavailable")

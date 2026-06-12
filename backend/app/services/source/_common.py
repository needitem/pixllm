"""소스 서비스/에이전트 공용 유틸리티.

service.py와 agent.py가 각자 따로 정의해 쓰던 동일 로직의 헬퍼들을
한곳으로 모은 모듈이다. 두 파일은 여기서 import해 같은 구현을 공유한다.
(과거에는 양쪽에 _to_text / _normalized_token(=_identifier_key) /
 _clip(=_clip_text) 등이 중복 정의돼 있었다.)
"""

import json
from typing import Any


def to_text(value: Any) -> str:
    """임의 값을 안전하게 문자열로 바꾸고 양끝 공백을 제거한다. None은 빈 문자열이 된다."""
    return str(value or "").strip()


def normalized_token(value: Any) -> str:
    """영숫자만 남기고 소문자로 정규화한 비교용 키를 만든다.

    예: "Get_Pixel Value" → "getpixelvalue". 대소문자·구두점 차이를 무시한
    부분 문자열 매칭(검색 점수 계산, 식별자 대조)의 기반이 된다.
    """
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


def clip(value: Any, limit: int = 4000) -> str:
    """텍스트를 limit 문자 이내로 절단하고, 잘렸으면 끝에 "...[truncated]" 표식을 붙인다."""
    text = str(value or "")
    if len(text) <= limit:
        return text
    return f"{text[: max(0, limit - 15)]}\n...[truncated]"


def safe_int(value: Any, default: int, low: int, high: int) -> int:
    """값을 int로 파싱하되 실패하면 default를 쓰고, [low, high] 범위로 클램프한다.

    LLM이 채운 도구 인자나 외부 API 파라미터처럼 신뢰할 수 없는 숫자를
    안전한 범위로 정규화할 때 사용한다.
    """
    try:
        parsed = int(value)
    except Exception:
        parsed = default
    return max(low, min(parsed, high))


def json_for_model(payload: Any) -> str:
    """payload를 공백 없는 최소 JSON 문자열로 직렬화한다. (한글 보존, 토큰 절약)"""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

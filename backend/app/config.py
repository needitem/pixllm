"""백엔드 전역 설정 모듈.

모든 설정값을 환경 변수에서 읽되, 없으면 기본값을 쓴다.
다른 모듈은 `from ... import config` 후 `config.RAW_SOURCE_ROOT`처럼 상수로 접근한다.
서버 기동 시점에 한 번만 평가되므로, 환경 변수를 바꾸면 재시작이 필요하다.
"""

import os
from pathlib import Path


def env(name: str, default: str) -> str:
    """환경 변수 `name`을 읽어 반환한다. 미설정이거나 빈 문자열이면 `default`를 쓴다.

    `os.getenv`만 쓰면 "빈 문자열로 설정된" 변수가 그대로 통과되므로,
    빈 값도 기본값으로 대체하기 위해 별도 헬퍼로 분리했다.
    """
    value = os.getenv(name)
    return value if value not in (None, "") else default


# FastAPI 앱 타이틀 (헬스체크 응답의 service 필드에도 사용)
APP_NAME = env("PIXLLM_APP_NAME", "PIXLLM Source API")
# 모든 라우터 앞에 붙는 URL 접두사 (예: /api/v1/source/...)
API_PREFIX = env("PIXLLM_API_PREFIX", "/api/v1")
# 소스 인덱스 등 데이터 파일을 두는 최상위 디렉터리 (backend/ 기준 상대 경로)
SOURCE_DATA_DIR = env("PIXLLM_SOURCE_DATA_DIR", ".profiles")
# 런타임 산출물(.runtime/methods_index.json 등)을 두는 디렉터리
SOURCE_RUNTIME_DIR = env("SOURCE_RUNTIME_DIR", str(Path(SOURCE_DATA_DIR) / "source"))
# 소스 질의응답 에이전트가 호출할 LLM 서버 (vLLM, OpenAI 호환 API)의 기본 주소
LLM_BASE_URL = env("PIXLLM_LLM_BASE_URL", "http://192.168.2.212:8000/v1")
# 에이전트가 기본으로 사용할 모델 이름
DEFAULT_MODEL = env("PIXLLM_DEFAULT_MODEL", "Qwen/Qwen3.6-27B")
# 워크플로 재작성(rewrite) 전용 LLM 서버 주소와 모델 (현재 별도 기능에서 사용)
REWRITE_LLM_BASE_URL = env("PIXLLM_REWRITE_LLM_BASE_URL", "http://192.168.2.238:8002/v1")
REWRITE_MODEL = env("PIXLLM_REWRITE_MODEL", "workflow-rewrite-qwen")

# backend/ 디렉터리의 절대 경로 (이 파일 위치 기준으로 계산)
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SOURCE_DATA_ROOT = _BACKEND_ROOT / SOURCE_DATA_DIR
# 인덱싱 대상인 원본 C++/CLI SDK 소스 트리의 루트.
# 모든 검색/읽기 API는 이 디렉터리 안의 파일만 접근할 수 있다.
RAW_SOURCE_ROOT = env(
    "RAW_SOURCE_ROOT",
    str((_SOURCE_DATA_ROOT / "raw_source" / "source").resolve()),
)

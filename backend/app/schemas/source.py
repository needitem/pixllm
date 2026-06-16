"""소스 API 요청 본문 스키마 모음.

routers/source.py의 각 POST 엔드포인트가 받는 JSON 본문을 pydantic 모델로 정의한다.
검증 실패 시 main.py의 핸들러가 422 VALIDATION_ERROR 봉투로 응답한다.
모델 이름은 "Source<엔드포인트>Request" 규칙을 따른다.
"""

from typing import Optional

from pydantic import BaseModel

from .. import config


class SourceListRequest(BaseModel):
    """POST /source/ls 요청: 디렉터리 목록 조회."""

    # 조회할 Source/ 하위 경로. 비우면 루트.
    path: Optional[str] = None
    # 하위 디렉터리 재귀 깊이 (0이면 바로 아래만)
    depth: int = 1
    # 최대 반환 항목 수
    limit: int = 80


class SourceGlobRequest(BaseModel):
    """POST /source/glob 요청: 글롭 패턴 파일 찾기."""

    # Source/ 기준 글롭 패턴 (예: **/*Layer*.h)
    pattern: str = "**/*"
    limit: int = 80


class SourceGrepRequest(BaseModel):
    """POST /source/grep 요청: 소스 전문 검색."""

    # 검색어 (regex=True면 정규식으로 해석)
    pattern: str
    # 검색 대상 파일을 제한하는 글롭 (예: **/*.h)
    path_glob: Optional[str] = None
    regex: bool = False
    case_sensitive: bool = False
    limit: int = 20
    # 매치 줄 앞뒤로 함께 보여줄 컨텍스트 줄 수
    context: int = 1


class SourceSymbolSearchRequest(BaseModel):
    """POST /source/symbols 요청: 메서드 인덱스 심볼 검색."""

    query: str
    limit: int = 10


class SourceTypeGraphRequest(BaseModel):
    """POST /source/type-graph 요청: 타입/멤버 관계 그래프 조회."""

    query: str
    limit: int = 12


class SourceUsagesRequest(BaseModel):
    """POST /source/usages 요청: 실제 코드 사용처 검색."""

    query: str
    limit: int = 12


class SourceSearchRequest(BaseModel):
    """POST /source/search 요청: 심볼+grep 통합 검색."""

    query: Optional[str] = None
    limit: int = 12
    # True면 매치 스니펫을 content 필드에도 포함
    include_content: bool = False
    # 검색 종류 강제: "symbol"/"method"(심볼만), "file"/"source_file"(파일명만), None(통합)
    kind: Optional[str] = None


class SourceReadRequest(BaseModel):
    """POST /source/read 요청: 소스 파일 구간 읽기."""

    # "Source/..." 파일 경로 또는 ".runtime/methods_index.json#Qualified.Symbol" 심볼 경로
    path: str
    # 줄 범위 (생략하면 파일 앞부분 기본 분량)
    start_line: Optional[int] = None
    end_line: Optional[int] = None


class SourceAnswerRequest(BaseModel):
    """POST /source/answer 요청: LLM 에이전트 소스 질의응답."""

    # 사용자 질문 (자연어)
    prompt: str
    # 사용할 모델/LLM 서버 주소. 생략하면 config 기본값.
    model: Optional[str] = None
    llm_base_url: Optional[str] = None
    # 클라이언트 측 대화 추적용 ID (응답에 그대로 반환됨)
    session_id: Optional[str] = None
    # 모델 응답 1회당 최대 생성 토큰 수
    max_tokens: int = config.DEFAULT_MAX_TOKENS
    # 에이전트 루프의 최대 LLM 호출 횟수 (도구 호출 스텝 상한)
    max_llm_calls: int = config.DEFAULT_MAX_LLM_CALLS
    # Qwen 계열의 thinking(사고 과정) 모드 활성화 여부
    enable_thinking: bool = False

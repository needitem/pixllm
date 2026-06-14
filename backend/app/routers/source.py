"""소스 탐색 API 라우터.

C++/CLI SDK 소스 트리에 대한 검색/읽기와 LLM 질의응답 엔드포인트를 제공한다.
이 파일은 얇은 어댑터일 뿐이고, 실제 로직은 전부 services/source/ 아래에 있다:
- service.py : 인덱스 빌드, ls/glob/grep, 심볼 검색, 타입 그래프, 파일 읽기
- agent.py   : LLM tool-calling 에이전트 (/source/answer)

요청 본문 스키마는 schemas/source.py의 pydantic 모델로 검증된다.

여기에 노출하는 엔드포인트는 데스크톱 클라이언트가 실제로 호출하는 4개뿐이다:
- /context : 소스 개요
- /search  : 통합 검색 (UI 검색창)
- /read    : 파일 구간 읽기
- /answer  : LLM 에이전트 질의응답
ls/glob/grep/symbols/type-graph/usages 같은 세부 탐색은 에이전트가 service.py
함수를 in-process로 직접 호출하므로 별도 HTTP 라우트를 두지 않는다.
"""

from fastapi import APIRouter
from starlette.concurrency import run_in_threadpool

from ..envelopes import err, ok
from ..schemas.source import (
    SourceAnswerRequest,
    SourceReadRequest,
    SourceSearchRequest,
)
from ..services.source import agent as source_agent
from ..services.source import service as source_service


router = APIRouter(prefix="/source")


@router.post("/context")
async def source_overview():
    """소스 개요 조회: 소스 루트 경로, 파일/메서드 수, 모듈별 요약을 반환한다."""
    return ok(source_service.get_context())


@router.post("/search")
async def search_source(payload: SourceSearchRequest):
    """통합 검색: kind에 따라 심볼 검색·파일 글롭·grep을 조합한 결과를 반환한다."""
    return ok(
        source_service.search_source(
            query=payload.query or "",
            limit=payload.limit,
            include_content=payload.include_content,
            kind=payload.kind,
        )
    )


@router.post("/answer")
async def answer_source(payload: SourceAnswerRequest):
    """소스 질의응답: LLM 에이전트가 소스 탐색 도구를 반복 호출해 근거 기반 답변을 만든다.

    answer_source_question은 LLM 서버를 동기(blocking) HTTP로 호출하므로,
    이벤트 루프가 멈추지 않도록 run_in_threadpool로 워커 스레드에서 실행한다.
    """
    return ok(
        await run_in_threadpool(
            source_agent.answer_source_question,
            prompt=payload.prompt,
            model=payload.model,
            llm_base_url=payload.llm_base_url,
            session_id=payload.session_id,
            max_tokens=payload.max_tokens,
            max_llm_calls=payload.max_llm_calls,
            enable_thinking=payload.enable_thinking,
        )
    )


@router.post("/read")
async def read_source(payload: SourceReadRequest):
    """소스 파일 구간 읽기: Source/ 경로의 지정 줄 범위(또는 인덱스 심볼)를 줄 번호와 함께 반환한다."""
    item = source_service.read_source(
        payload.path,
        start_line=payload.start_line,
        end_line=payload.end_line,
    )
    if not item:
        return err("NOT_FOUND", "source path not found")
    return ok(item)

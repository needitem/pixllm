"""소스 탐색 API 라우터.

C++/CLI SDK 소스 트리에 대한 검색/읽기/그래프 조회와 LLM 질의응답 엔드포인트를 제공한다.
이 파일은 얇은 어댑터일 뿐이고, 실제 로직은 전부 services/source/ 아래에 있다:
- service.py : 인덱스 빌드, ls/glob/grep, 심볼 검색, 타입 그래프, 파일 읽기
- agent.py   : LLM tool-calling 에이전트 (/source/answer)

요청 본문 스키마는 schemas/source.py의 pydantic 모델로 검증된다.
"""

from fastapi import APIRouter
from starlette.concurrency import run_in_threadpool

from ..envelopes import err, ok
from ..schemas.source import (
    SourceAnswerRequest,
    SourceGlobRequest,
    SourceGrepRequest,
    SourceListRequest,
    SourceReadRequest,
    SourceSearchRequest,
    SourceSymbolSearchRequest,
    SourceTypeGraphRequest,
    SourceUsagesRequest,
)
from ..services.source import agent as source_agent
from ..services.source import service as source_service


router = APIRouter(prefix="/source")


@router.get("")
async def source_overview_get():
    """소스 개요 조회(GET): 소스 루트 경로, 파일/메서드 수, 모듈별 요약을 반환한다."""
    return ok(source_service.get_context())


@router.post("/context")
async def source_overview():
    """소스 개요 조회(POST): 위 GET과 동일. POST만 쓰는 클라이언트를 위한 별칭."""
    return ok(source_service.get_context())


@router.post("/index/rebuild")
async def rebuild_source_index():
    """메서드 인덱스와 소스 매니페스트를 처음부터 다시 생성해 저장한다.

    원본 소스 트리가 갱신됐을 때 수동으로 호출하는 관리용 엔드포인트.
    """
    return ok(source_service.rebuild_index())


@router.post("/ls")
async def list_source(payload: SourceListRequest):
    """디렉터리 목록 조회: 주어진 Source/ 경로 아래의 디렉터리·소스 파일을 depth 깊이까지 나열한다."""
    return ok(
        source_service.list_source(
            payload.path or "",
            depth=payload.depth,
            limit=payload.limit,
        )
    )


@router.post("/glob")
async def glob_source(payload: SourceGlobRequest):
    """글롭 패턴(예: **/*Layer*.h)으로 소스 파일을 찾는다."""
    return ok(source_service.glob_source(payload.pattern, limit=payload.limit))


@router.post("/grep")
async def grep_source(payload: SourceGrepRequest):
    """소스 전문(full-text) 검색: 부분 문자열 또는 정규식으로 줄 단위 매치와 주변 컨텍스트를 반환한다."""
    return ok(
        source_service.grep_source(
            payload.pattern,
            path_glob=payload.path_glob or "",
            regex=payload.regex,
            case_sensitive=payload.case_sensitive,
            limit=payload.limit,
            context=payload.context,
        )
    )


@router.post("/symbols")
async def search_source_symbols(payload: SourceSymbolSearchRequest):
    """심볼(메서드/프로퍼티) 검색: 메서드 인덱스에서 이름·선언·요약 매칭으로 찾는다."""
    return ok(source_service.symbol_search(payload.query, limit=payload.limit))


@router.post("/type-graph")
async def source_type_graph(payload: SourceTypeGraphRequest):
    """타입 그래프 조회: 질의와 관련된 타입들, 상속 관계, 멤버 연산, 타입 간 변환 경로를 반환한다."""
    return ok(source_service.type_graph(payload.query, limit=payload.limit))


@router.post("/usages")
async def source_usages(payload: SourceUsagesRequest):
    """실제 사용처 검색: 주석이 아닌 코드 줄에서 해당 타입/메서드가 쓰인 위치를 찾는다."""
    return ok(source_service.source_usages(payload.query, limit=payload.limit))


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

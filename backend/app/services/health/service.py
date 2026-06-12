"""헬스체크 응답 생성 서비스.

routers/health.py의 세 엔드포인트(live/health/ready)가 반환할 페이로드를 만든다.
점검 대상은 두 가지 컴포넌트다:
- raw_source_store : 원본 C++/CLI 소스 트리 디렉터리가 존재하고 소스 파일이 있는지
- source_index     : 메서드 인덱스(methods_index.json)와 매니페스트가 생성돼 있는지
"""

from datetime import datetime, timezone

from ... import config
from ..source.service import methods_index_file, source_manifest_file, source_root


def _timestamp() -> str:
    """현재 시각을 UTC ISO-8601 문자열로 반환한다 (응답의 checked_at 필드용)."""
    return datetime.now(timezone.utc).isoformat()


def _raw_source_stats() -> dict:
    """원본 소스 저장소와 인덱스 파일의 현재 상태를 한 번에 수집한다.

    소스 루트 아래를 재귀 순회하며 C++/C# 소스 확장자 파일 수를 세고,
    인덱스/매니페스트 파일의 경로와 존재 여부를 함께 담아 반환한다.
    build_health_response가 컴포넌트별 상태 판정에 사용한다.
    """
    root = source_root()
    source_file_count = 0
    if root.exists() and root.is_dir():
        source_file_count = sum(
            1
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".h", ".hpp", ".cpp", ".cxx", ".cc", ".cs"}
        )
    return {
        "root_path": str(root),
        "present": root.exists() and root.is_dir(),
        "source_file_count": source_file_count,
        "methods_index_path": methods_index_file().as_posix(),
        "methods_index_present": methods_index_file().exists(),
        "source_manifest_path": source_manifest_file().as_posix(),
        "source_manifest_present": source_manifest_file().exists(),
    }


def build_liveness_response() -> dict:
    """liveness 응답: 프로세스가 살아서 응답할 수 있다는 사실만 보고한다 (항상 ok)."""
    return {
        "status": "ok",
        "service": config.APP_NAME,
        "checked_at": _timestamp(),
    }


async def build_health_response() -> dict:
    """상세 헬스 응답: 소스 저장소가 없으면 전체 status를 "degraded"로 낮춘다.

    인덱스가 없는 경우는 첫 검색 때 자동 생성되므로 오류가 아닌 "missing"으로만 표시한다.
    """
    raw_source = _raw_source_stats()
    return {
        "status": "ok" if raw_source["present"] else "degraded",
        "service": config.APP_NAME,
        "checked_at": _timestamp(),
        "components": {
            "raw_source_store": {
                "status": "ok" if raw_source["present"] else "error",
                "root_path": raw_source["root_path"],
                "source_file_count": raw_source["source_file_count"],
            },
            "source_index": {
                "status": "ok" if raw_source["methods_index_present"] else "missing",
                "methods_index_path": raw_source["methods_index_path"],
                "source_manifest_path": raw_source["source_manifest_path"],
                "source_manifest_present": raw_source["source_manifest_present"],
            },
        },
    }


async def build_readiness_response() -> dict:
    """readiness 응답: 상세 헬스 결과에 `ready` 불리언(전체 status가 ok인지)을 추가한다."""
    payload = await build_health_response()
    return {
        **payload,
        "ready": payload["status"] == "ok",
    }

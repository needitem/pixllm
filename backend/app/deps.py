"""앱 수명주기(lifespan) 훅 모듈.

main.py의 lifespan 컨텍스트가 서버 시작 시 `init_state()`,
종료 시 `close_state()`를 호출한다.
DB 커넥션 풀 같은 전역 자원이 생기면 여기에서 열고 닫는다.
"""

from pathlib import Path

from . import config


async def init_state():
    """서버 시작 시 1회 실행되는 초기화 훅.

    원본 소스 루트 디렉터리가 없으면 만들어 두어,
    이후 검색/인덱싱 코드가 "디렉터리 없음" 오류 없이 동작하게 한다.
    """
    Path(config.RAW_SOURCE_ROOT).mkdir(parents=True, exist_ok=True)


async def close_state():
    """서버 종료 시 1회 실행되는 정리 훅. 현재는 정리할 전역 자원이 없다."""
    return None

"""애플리케이션 로깅 설정 모듈.

'pixllm' 네임스페이스 로거를 한 번만 구성한다 (레벨/포맷은 config의 환경변수 기반).
백엔드 어디서든 get_logger("<이름>")으로 "pixllm.<이름>" 하위 로거를 받아 쓴다.
"""

import logging

from . import config

# configure_logging이 중복 실행되지 않도록 막는 1회 가드 플래그
_CONFIGURED = False


def configure_logging() -> None:
    """'pixllm' 루트 로거에 레벨과 StreamHandler를 1회만 설정한다.

    - 레벨: config.LOG_LEVEL (잘못된 값이면 INFO로 폴백)
    - 핸들러: 이미 있으면 추가하지 않음 (reload 시 중복 출력 방지)
    - propagate=False: 상위 root 로거로 전파하지 않아 uvicorn 핸들러와 중복되지 않게 함
    """
    global _CONFIGURED
    if _CONFIGURED:
        return
    level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logger = logging.getLogger("pixllm")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(config.LOG_FORMAT))
        logger.addHandler(handler)
    logger.propagate = False
    _CONFIGURED = True


def get_logger(name: str = "") -> logging.Logger:
    """"pixllm.<name>" 하위 로거를 반환한다. 최초 호출 시 설정을 보장한다."""
    configure_logging()
    return logging.getLogger(f"pixllm.{name}" if name else "pixllm")

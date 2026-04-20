from pathlib import Path

from . import config


async def init_state():
    Path(config.RAW_SOURCE_ROOT).mkdir(parents=True, exist_ok=True)


async def close_state():
    return None

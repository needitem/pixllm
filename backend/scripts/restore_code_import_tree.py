#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import config
from app.deps import close_state, init_state, state
from app.services.tools.workspace_sync import restore_import_code_workspace


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Restore imported code files from MinIO into the configured code import root."
    )
    parser.add_argument("--project", default="", help="Optional project name, for example: nxdl")
    parser.add_argument("--overwrite", action="store_true", help="Rewrite files even if they already exist")
    return parser.parse_args()


async def _main() -> int:
    args = parse_args()
    await init_state()
    try:
        result = await restore_import_code_workspace(
            state.redis,
            state.minio,
            config.MINIO_BUCKET,
            config.IMPORT_CODE_ROOT,
            project=(args.project or None),
            overwrite=bool(args.overwrite),
        )
        print(json.dumps(result, ensure_ascii=False))
        return 0
    finally:
        await close_state()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))

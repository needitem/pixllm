import asyncio
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from ... import config
from ...core.policy import SecurityPolicy
from .support import clamp_int


def _run_svn(args: List[str], cwd: Path) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            [config.SVN_BIN, *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        return completed.returncode, completed.stdout, completed.stderr
    except FileNotFoundError as exc:
        return 127, "", f"svn not found: {exc}"


def _parse_status_lines(output: str, *, path_filter: Optional[str], limit: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    filter_norm = str(path_filter or "").strip().replace("\\", "/").lower()
    max_rows = clamp_int(limit, 1, 500)

    for raw in str(output or "").splitlines():
        if len(raw) < 8:
            continue
        status = raw[:7]
        path = raw[8:].strip().replace("\\", "/")
        if not path:
            continue
        if filter_norm and filter_norm not in path.lower():
            continue
        rows.append(
            {
                "path": path,
                "status": status,
            }
        )
        if len(rows) >= max_rows:
            break
    return rows


async def svn_info(redis, code_tools, workspace_path: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    gate = await SecurityPolicy.check_search_gate(redis, session_id)
    if not gate["allow"]:
        return {"workspace_path": workspace_path, "found": False, "reason": gate["reason"]}

    workspace_root = SecurityPolicy.execute_code_tools_boundary(code_tools, workspace_path)
    if workspace_root is None:
        return {"workspace_path": workspace_path, "found": False, "reason": "workspace_not_found"}

    rc, stdout, stderr = await asyncio.to_thread(_run_svn, ["info"], workspace_root)
    if rc != 0:
        return {"workspace_path": workspace_path, "found": False, "reason": "svn_info_failed", "stderr": stderr[-1000:]}

    payload: Dict[str, Any] = {"workspace_path": workspace_path, "found": True, "root": str(workspace_root)}
    for line in stdout.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        payload[key.strip().lower().replace(" ", "_")] = value.strip()
    return payload


async def svn_status(
    redis,
    code_tools,
    workspace_path: str,
    path_filter: Optional[str],
    limit: int,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    gate = await SecurityPolicy.check_search_gate(redis, session_id)
    if not gate["allow"]:
        return {"workspace_path": workspace_path, "entries": [], "reason": gate["reason"]}

    workspace_root = SecurityPolicy.execute_code_tools_boundary(code_tools, workspace_path)
    if workspace_root is None:
        return {"workspace_path": workspace_path, "entries": [], "reason": "workspace_not_found"}

    rc, stdout, stderr = await asyncio.to_thread(_run_svn, ["status"], workspace_root)
    if rc != 0:
        return {"workspace_path": workspace_path, "entries": [], "reason": "svn_status_failed", "stderr": stderr[-1000:]}

    entries = _parse_status_lines(stdout, path_filter=path_filter, limit=limit)
    return {"workspace_path": workspace_path, "entries": entries, "truncated": len(entries) >= clamp_int(limit, 1, 500)}


async def svn_diff(
    redis,
    code_tools,
    workspace_path: str,
    path_filter: Optional[str],
    max_chars: int,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    gate = await SecurityPolicy.check_search_gate(redis, session_id)
    if not gate["allow"]:
        return {"workspace_path": workspace_path, "diff": "", "reason": gate["reason"]}

    workspace_root = SecurityPolicy.execute_code_tools_boundary(code_tools, workspace_path)
    if workspace_root is None:
        return {"workspace_path": workspace_path, "diff": "", "reason": "workspace_not_found"}

    args = ["diff"]
    if path_filter:
        args.append(path_filter)
    rc, stdout, stderr = await asyncio.to_thread(_run_svn, args, workspace_root)
    if rc not in {0, 1}:
        return {"workspace_path": workspace_path, "diff": "", "reason": "svn_diff_failed", "stderr": stderr[-1000:]}

    capped = clamp_int(max_chars, 200, 20000)
    diff_text = stdout[:capped]
    return {"workspace_path": workspace_path, "diff": diff_text, "truncated": len(stdout) > capped}

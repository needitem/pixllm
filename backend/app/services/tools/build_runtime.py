import asyncio
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from ... import config
from ...core.policy import SecurityPolicy
from .code_runtime import iter_code_roots
from .support import clamp_int, is_subpath



def _safe_workspace_relative_path(workspace_root: Path, raw_path: Optional[str]) -> Optional[Path]:
    if not raw_path:
        return None
    raw_candidate = Path(str(raw_path))
    if raw_candidate.is_absolute():
        candidate = raw_candidate.resolve()
        if not is_subpath(candidate, workspace_root):
            raise ValueError("path escapes workspace root")
        return candidate
    candidate = (workspace_root / str(raw_path).replace("\\", "/")).resolve()
    if not is_subpath(candidate, workspace_root):
        raise ValueError("path escapes workspace root")
    return candidate


def _build_command(
    *,
    tool: str,
    workspace_root: Path,
    project_or_solution: Optional[str],
    target: Optional[str],
    configuration: Optional[str],
    args: List[str],
) -> tuple[List[str], Path]:
    normalized_tool = str(tool or "").strip().lower()
    normalized_args = [str(arg) for arg in list(args or [])]
    target_value = str(target or "").strip()
    config_value = str(configuration or "").strip()
    project_path = _safe_workspace_relative_path(workspace_root, project_or_solution)

    if normalized_tool == "msbuild":
        if project_path is None:
            raise ValueError("project_or_solution is required for msbuild")
        command = [config.MSBUILD_BIN, str(project_path)]
        if target_value:
            command.append(f"/t:{target_value}")
        if config_value:
            command.append(f"/p:Configuration={config_value}")
        command.extend(normalized_args)
        return command, workspace_root

    if normalized_tool == "dotnet":
        command = [config.DOTNET_BIN, "build"]
        if project_path is not None:
            command.append(str(project_path))
        if config_value:
            command.extend(["-c", config_value])
        if target_value:
            command.append(f"-t:{target_value}")
        command.extend(normalized_args)
        return command, workspace_root

    if normalized_tool == "cmake":
        build_dir = project_path if project_path is not None else workspace_root
        command = [config.CMAKE_BIN, "--build", str(build_dir)]
        if target_value:
            command.extend(["--target", target_value])
        if config_value:
            command.extend(["--config", config_value])
        command.extend(normalized_args)
        return command, workspace_root

    if normalized_tool == "ninja":
        command = [config.NINJA_BIN]
        if target_value:
            command.append(target_value)
        command.extend(normalized_args)
        return command, project_path or workspace_root

    if normalized_tool == "custom":
        if project_path is None:
            raise ValueError("project_or_solution is required for custom build")
        command = [str(project_path), *normalized_args]
        return command, workspace_root

    raise ValueError(f"unsupported build tool: {normalized_tool}")


def _run_build_subprocess(command: List[str], cwd: Path, timeout_sec: int) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


async def run_build(
    redis,
    code_tools,
    *,
    workspace_path: str,
    tool: str,
    project_or_solution: Optional[str],
    target: Optional[str],
    configuration: Optional[str],
    args: List[str],
    timeout_sec: int,
    max_chars: int,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    gate = await SecurityPolicy.check_search_gate(redis, session_id)
    if not gate["allow"]:
        return {"workspace_path": workspace_path, "tool": tool, "ok": False, "reason": gate["reason"]}

    workspace_root = SecurityPolicy.execute_code_tools_boundary(code_tools, workspace_path)
    if workspace_root is None:
        return {"workspace_path": workspace_path, "tool": tool, "ok": False, "reason": "workspace_not_found"}

    try:
        command, cwd = _build_command(
            tool=tool,
            workspace_root=workspace_root,
            project_or_solution=project_or_solution,
            target=target,
            configuration=configuration,
            args=args,
        )
    except ValueError as exc:
        return {"workspace_path": workspace_path, "tool": tool, "ok": False, "reason": "invalid_request", "message": str(exc)}

    capped_timeout = clamp_int(timeout_sec, 1, 3600)
    capped_chars = clamp_int(max_chars, 500, 40000)

    try:
        rc, stdout, stderr = await asyncio.to_thread(_run_build_subprocess, command, cwd, capped_timeout)
    except subprocess.TimeoutExpired:
        return {
            "workspace_path": workspace_path,
            "tool": tool,
            "ok": False,
            "reason": "timeout",
            "command": command,
            "cwd": str(cwd),
            "timeout_sec": capped_timeout,
        }
    except FileNotFoundError as exc:
        return {
            "workspace_path": workspace_path,
            "tool": tool,
            "ok": False,
            "reason": "command_not_found",
            "command": command,
            "cwd": str(cwd),
            "message": str(exc),
        }

    stdout_text = (stdout or "")[:capped_chars]
    stderr_text = (stderr or "")[:capped_chars]
    return {
        "workspace_path": workspace_path,
        "tool": tool,
        "ok": rc == 0,
        "return_code": rc,
        "command": command,
        "cwd": str(cwd),
        "stdout": stdout_text,
        "stderr": stderr_text,
        "stdout_truncated": len(stdout or "") > capped_chars,
        "stderr_truncated": len(stderr or "") > capped_chars,
        "timeout_sec": capped_timeout,
    }

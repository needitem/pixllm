import asyncio
import shlex
import subprocess
from pathlib import Path
from typing import Optional

from ... import config
from .errors import format_svn_sync_error
from .paths import normalize_svn_revision


def run_subprocess(args: list[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=3600,
            check=False,
        )
        return completed.returncode, completed.stdout[-4000:], completed.stderr[-4000:]
    except FileNotFoundError as exc:
        cmd = args[0] if args else "<unknown>"
        return 127, "", f"command not found: {cmd} ({exc})"


def render_tfs_command(template: str, project: str, tfs_path: str, target_dir: Path) -> list[str]:
    rendered = template.format(project=project, tfs_path=tfs_path, target_dir=str(target_dir)).strip()
    if not rendered:
        raise ValueError("empty TFS sync command")
    return shlex.split(rendered)


def build_svn_auth_args(job: dict) -> list[str]:
    auth_args: list[str] = [
        "--non-interactive",
        "--trust-server-cert-failures=unknown-ca,cn-mismatch,expired,other",
        "--no-auth-cache",
    ]
    username = (job.get("svn_username") or "").strip()
    password = job.get("svn_password") or ""
    if username:
        auth_args.extend(["--username", username])
    if password:
        auth_args.extend(["--password", password])
    revision = normalize_svn_revision(job.get("svn_revision"))
    auth_args.extend(["-r", revision])
    return auth_args


async def sync_tfs_repo(job: dict, target_dir: Path) -> tuple[bool, Optional[str]]:
    template = (job.get("tfs_sync_command") or "").strip() or config.TFS_DOCS_SYNC_COMMAND
    if not template:
        return False, "TFS_DOCS_SYNC_COMMAND is not configured"
    command = render_tfs_command(template, job.get("project") or "", job.get("tfs_path") or "", target_dir)
    rc, _stdout, stderr = await asyncio.to_thread(run_subprocess, command, target_dir)
    if rc != 0:
        return False, f"tfs sync failed(exit={rc}): {stderr or 'unknown error'}"
    return True, None


async def sync_svn_repo(job: dict, target_dir: Path) -> tuple[bool, Optional[str]]:
    svn_url = (job.get("svn_url") or "").strip()
    if not svn_url:
        return False, "svn_url is required"
    svn_username = (job.get("svn_username") or "").strip() or None

    auth_args = build_svn_auth_args(job)
    target_has_wc = (target_dir / ".svn").exists()

    if target_has_wc:
        cleanup_cmd = [config.SVN_BIN, "cleanup", str(target_dir)]
        cleanup_rc, _cleanup_out, cleanup_err = await asyncio.to_thread(run_subprocess, cleanup_cmd)
        if cleanup_rc != 0:
            return False, f"svn cleanup failed(exit={cleanup_rc}): {cleanup_err or 'unknown error'}"

    if bool(job.get("svn_export")):
        cmd = [config.SVN_BIN, "export", "--force", *auth_args, svn_url, str(target_dir)]
    elif target_has_wc:
        cmd = [config.SVN_BIN, "update", *auth_args, str(target_dir)]
    else:
        cmd = [config.SVN_BIN, "checkout", *auth_args, svn_url, str(target_dir)]

    rc, _stdout, stderr = await asyncio.to_thread(run_subprocess, cmd)
    if rc != 0:
        formatted = format_svn_sync_error(stderr or "unknown error", svn_url, svn_username)
        return False, f"svn sync failed(exit={rc}): {formatted}"
    return True, None

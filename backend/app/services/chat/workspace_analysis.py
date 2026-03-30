from typing import Any, Dict, Optional

from ..tools.svn_runtime import svn_diff, svn_info, svn_status


async def collect_workspace_snapshot(
    *,
    redis,
    code_tools,
    workspace_path: str,
    session_id: Optional[str],
    path_filter: Optional[str],
    max_diff_chars: int = 4000,
) -> Dict[str, Any]:
    info_result = await svn_info(redis, code_tools, workspace_path, session_id)
    status_result = await svn_status(redis, code_tools, workspace_path, path_filter, 100, session_id)
    diff_result = await svn_diff(redis, code_tools, workspace_path, path_filter, max_diff_chars, session_id)

    return {
        "workspace_path": workspace_path,
        "info": info_result,
        "status": status_result,
        "diff": diff_result,
        "changed_file_count": len(list(status_result.get("entries") or [])),
    }

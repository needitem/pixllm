import asyncio
import mimetypes
import re
import shutil
from pathlib import Path, PurePosixPath
from typing import Optional
from urllib.parse import quote

from fastapi.responses import FileResponse, StreamingResponse

from ... import config
from ...deps import state
from ..tools.code_runtime import resolve_code_root


SUPPORTED_DOC_EXTENSIONS = (".html", ".htm", ".md", ".txt", ".rst", ".adoc", ".pdf")
SUPPORTED_CODE_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".cpp",
    ".cc",
    ".cxx",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".java",
    ".go",
    ".rs",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".css",
)


def extensions_for_mode(mode: str) -> tuple[str, ...]:
    return SUPPORTED_CODE_EXTENSIONS if str(mode or "").strip().lower() == "code" else SUPPORTED_DOC_EXTENSIONS


def normalize_import_mode(mode: Optional[str]) -> str:
    return "code" if str(mode or "").strip().lower() == "code" else "docs"


def sanitize_project(raw: Optional[str]) -> Optional[str]:
    if raw is None:
        return None
    value = raw.strip()
    if not value:
        return None
    value = value.replace("\\", "/").rstrip("/")
    value = value.split("/")[-1]
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-").lower()
    return value or None


def normalize_svn_revision(raw: Optional[str]) -> str:
    value = (raw or "").strip()
    return value or "HEAD"


def resolve_project_name(root_path: Path, file_path: Path, explicit_project: Optional[str]) -> str:
    if explicit_project:
        return explicit_project

    root_name = sanitize_project(root_path.name)
    dynamic_roots = {"workspace_host", "docs_host", "workspace", "docs", "repos", "data"}
    try:
        rel_parts = file_path.relative_to(root_path).parts
    except Exception:
        rel_parts = ()

    if root_name and root_name.lower() not in dynamic_roots:
        return root_name
    if rel_parts:
        top = sanitize_project(rel_parts[0])
        if top:
            return top
    return root_name or "imports"


def safe_project_path(root_dir: str, project: str) -> Path:
    base = Path(root_dir).resolve()
    target = (base / project).resolve()
    if base == target:
        return target
    if base not in target.parents:
        raise ValueError("invalid project path")
    return target


def resolve_import_path(root_dir: str, requested_path: str) -> Path:
    base = Path(root_dir).resolve()
    raw = str(requested_path or "").strip()
    if not raw:
        raise ValueError("path is required")

    candidate = Path(raw)
    if candidate.is_absolute():
        target = candidate.resolve()
    else:
        normalized = PurePosixPath(raw.replace("\\", "/"))
        if normalized.is_absolute() or any(part in {"", ".", ".."} for part in normalized.parts):
            raise ValueError("invalid import path")
        target = (base / Path(*normalized.parts)).resolve()

    if target == base or base not in target.parents:
        raise ValueError("import path must stay within configured import root")
    return target


def safe_upload_relative_path(raw_filename: str) -> tuple[str, Path]:
    normalized = (raw_filename or "").replace("\\", "/").strip()
    if not normalized:
        raise ValueError("invalid upload filename")

    posix_path = PurePosixPath(normalized)
    parts = posix_path.parts
    if not parts or posix_path.is_absolute() or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("invalid upload path")

    root_name = sanitize_project(parts[0]) or "local_folder"
    relative_tail = Path(posix_path.name) if len(parts) == 1 else Path(*parts[1:])
    return root_name, relative_tail


def is_subpath(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False


def guess_media_type(filename: str) -> str:
    guessed, _encoding = mimetypes.guess_type(str(filename or ""))
    return guessed or "application/octet-stream"


def build_content_disposition(filename: str) -> str:
    safe_name = Path(str(filename or "source")).name or "source"
    return f"attachment; filename*=UTF-8''{quote(safe_name)}"


def iter_minio_object(response):
    try:
        while True:
            chunk = response.read(64 * 1024)
            if not chunk:
                break
            yield chunk
    finally:
        try:
            response.close()
        except Exception:
            pass
        try:
            response.release_conn()
        except Exception:
            pass


def source_file_response(path: Path, filename: str, download: bool):
    media_type = guess_media_type(filename or path.name)
    headers = {}
    if download:
        headers["Content-Disposition"] = build_content_disposition(filename or path.name)
    return FileResponse(path=str(path), media_type=media_type, headers=headers)


async def source_object_response(object_name: str, filename: str, download: bool):
    response = await asyncio.to_thread(state.minio.get_object, config.MINIO_BUCKET, object_name)
    headers = {}
    if download:
        headers["Content-Disposition"] = build_content_disposition(filename)
    return StreamingResponse(
        iter_minio_object(response),
        media_type=guess_media_type(filename),
        headers=headers,
    )


def resolve_source_workspace_path(module: Optional[str], source_file: Optional[str]) -> Optional[Path]:
    if not module or not source_file:
        return None

    code_tools = getattr(state, "code_tools", None)
    allowed_roots = []
    for root_dir in (config.IMPORT_CODE_ROOT,):
        try:
            allowed_roots.append(Path(root_dir).resolve())
        except Exception:
            continue
    if code_tools is not None:
        allowed_roots.extend(Path(root).resolve() for root in getattr(code_tools, "configured_roots", []))

    if not allowed_roots:
        return None

    rel_path = Path(str(source_file).replace("\\", "/"))
    candidate = None
    try:
        candidate = (Path(config.IMPORT_CODE_ROOT) / str(module).strip() / rel_path).resolve()
    except Exception:
        candidate = None

    if code_tools is not None and module:
        code_root = resolve_code_root(code_tools, str(module).strip())
        if code_root:
            try:
                candidate = (code_root / rel_path).resolve()
            except Exception:
                pass

    if candidate is None or not candidate.exists() or not candidate.is_file():
        return None
    if not any(is_subpath(candidate, root) for root in allowed_roots):
        return None
    return candidate


def copy_upload_stream_to_path(file_obj, dest_path: Path) -> None:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        file_obj.seek(0)
    except Exception:
        pass
    with dest_path.open("wb") as target:
        shutil.copyfileobj(file_obj, target)

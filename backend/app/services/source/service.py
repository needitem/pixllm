import json
import re
import time
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ... import config
from .methods_index import _read_source_text, build_methods_index_from_raw_source


SOURCE_EXTENSIONS = {".h", ".hpp", ".cpp", ".cxx", ".cc", ".cs"}
METHODS_INDEX_RELATIVE_PATH = ".runtime/methods_index.json"
SOURCE_MANIFEST_RELATIVE_PATH = ".runtime/source_manifest.json"
MAX_READ_CHARS = 12000
MAX_GREP_PATTERN_LENGTH = 200

_INDEX_CACHE: Dict[str, Any] = {"mtime": 0.0, "records": []}


def source_root() -> Path:
    return Path(config.RAW_SOURCE_ROOT)


def runtime_root() -> Path:
    root = Path(config.SOURCE_RUNTIME_DIR)
    if not root.is_absolute():
        root = Path(__file__).resolve().parents[3] / root
    return root


def methods_index_file() -> Path:
    return runtime_root() / PurePosixPath(METHODS_INDEX_RELATIVE_PATH).as_posix()


def source_manifest_file() -> Path:
    return runtime_root() / PurePosixPath(SOURCE_MANIFEST_RELATIVE_PATH).as_posix()


def _to_text(value: Any) -> str:
    return str(value or "").strip()


def compact_token(value: Any) -> str:
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


def _clip_text(value: Any, limit: int = MAX_READ_CHARS) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return f"{text[: max(0, limit - 15)]}\n...[truncated]"


def _safe_limit(value: Any, *, default: int = 50, high: int = 500) -> int:
    try:
        parsed = int(value)
    except Exception:
        parsed = default
    return max(1, min(parsed, high))


def _is_source_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SOURCE_EXTENSIONS


def _iter_source_files() -> Iterable[Path]:
    root = source_root()
    if not root.exists() or not root.is_dir():
        return []
    return (path for path in sorted(root.rglob("*")) if _is_source_file(path))


def _source_path(path: Path) -> str:
    return f"Source/{path.relative_to(source_root().resolve()).as_posix()}"


def _source_file_for_path(path_value: str) -> Optional[Path]:
    normalized = _to_text(path_value).replace("\\", "/")
    if "#" in normalized:
        normalized = normalized.split("#", 1)[0]
    if normalized.startswith("Source/"):
        normalized = normalized[len("Source/") :]
    if not normalized or normalized.startswith("/") or normalized == ".." or normalized.startswith("../"):
        return None
    root = source_root().resolve()
    target = (root / PurePosixPath(normalized).as_posix()).resolve()
    if target != root and root not in target.parents:
        return None
    return target


def _source_dir_for_path(path_value: str) -> Optional[Path]:
    normalized = _to_text(path_value).replace("\\", "/")
    if normalized.startswith("Source/"):
        normalized = normalized[len("Source/") :]
    root = source_root().resolve()
    target = (root / PurePosixPath(normalized or ".").as_posix()).resolve()
    if target != root and root not in target.parents:
        return None
    return target


def _read_lines(path: Path) -> List[str]:
    try:
        return _read_source_text(path).splitlines()
    except Exception:
        return []


def _load_json_file(path: Path, default_value: Any) -> Any:
    if not path.exists():
        return default_value
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default_value


def _build_source_manifest(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    root = source_root()
    files = [path for path in sorted(root.rglob("*")) if _is_source_file(path)]
    modules: Dict[str, Dict[str, Any]] = {}
    for path in files:
        rel = path.relative_to(root).as_posix()
        module = rel.split("/", 1)[0]
        item = modules.setdefault(
            module,
            {
                "module": module,
                "file_count": 0,
                "header_count": 0,
                "implementation_count": 0,
                "source_paths": [],
            },
        )
        item["file_count"] += 1
        item["header_count"] += 1 if path.suffix.lower() in {".h", ".hpp"} else 0
        item["implementation_count"] += 1 if path.suffix.lower() in {".cpp", ".cxx", ".cc", ".cs"} else 0
        item["source_paths"].append(f"Source/{rel}")

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "raw_source_root": root.as_posix(),
        "file_count": len(files),
        "method_count": len(records),
        "modules": sorted(modules.values(), key=lambda item: str(item.get("module") or "")),
    }


def rebuild_index() -> Dict[str, Any]:
    records = build_methods_index_from_raw_source(source_root())
    manifest = _build_source_manifest(records)
    methods_path = methods_index_file()
    manifest_path = source_manifest_file()
    methods_path.parent.mkdir(parents=True, exist_ok=True)
    methods_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    _INDEX_CACHE["mtime"] = methods_path.stat().st_mtime if methods_path.exists() else time.time()
    _INDEX_CACHE["records"] = records
    return {
        "methods_index_path": methods_path.as_posix(),
        "source_manifest_path": manifest_path.as_posix(),
        "method_count": len(records),
        "file_count": int(manifest.get("file_count") or 0),
        "raw_source_root": source_root().as_posix(),
    }


def load_methods_index() -> List[Dict[str, Any]]:
    path = methods_index_file()
    if not path.exists():
        rebuild_index()
    try:
        mtime = path.stat().st_mtime
    except Exception:
        mtime = 0.0
    if _INDEX_CACHE.get("records") and float(_INDEX_CACHE.get("mtime") or 0.0) == mtime:
        return list(_INDEX_CACHE.get("records") or [])
    records = _load_json_file(path, [])
    if not isinstance(records, list):
        records = []
    _INDEX_CACHE["mtime"] = mtime
    _INDEX_CACHE["records"] = [item for item in records if isinstance(item, dict)]
    return list(_INDEX_CACHE["records"])


def get_context() -> Dict[str, Any]:
    manifest = _load_json_file(source_manifest_file(), {})
    if not manifest:
        rebuild_index()
        manifest = _load_json_file(source_manifest_file(), {})
    return {
        "source": {
            "id": "raw",
            "root_path": source_root().as_posix(),
            "runtime_path": runtime_root().as_posix(),
            "method_count": int(manifest.get("method_count") or 0),
            "file_count": int(manifest.get("file_count") or 0),
            "generated_at": _to_text(manifest.get("generated_at")),
        },
        "modules": manifest.get("modules") if isinstance(manifest.get("modules"), list) else [],
    }


def list_source(path: str = "", *, depth: int = 1, limit: int = 200) -> Dict[str, Any]:
    root = _source_dir_for_path(path)
    if not root or not root.exists() or not root.is_dir():
        return {"ok": False, "error": "source_directory_not_found", "path": _to_text(path), "items": []}

    safe_depth = max(0, min(int(depth or 0), 8))
    safe_limit = _safe_limit(limit, default=200, high=1000)
    base_depth = len(root.relative_to(source_root().resolve()).parts) if root != source_root().resolve() else 0
    items: List[Dict[str, Any]] = []
    for child in sorted(root.rglob("*") if safe_depth else root.iterdir()):
        if child == root:
            continue
        rel_depth = len(child.relative_to(source_root().resolve()).parts) - base_depth
        if rel_depth > safe_depth + 1:
            continue
        if child.is_dir():
            kind = "directory"
        elif _is_source_file(child):
            kind = "source_file"
        else:
            continue
        items.append(
            {
                "path": _source_path(child) if child.is_file() else f"Source/{child.relative_to(source_root().resolve()).as_posix()}",
                "kind": kind,
                "size": child.stat().st_size if child.is_file() else 0,
            }
        )
        if len(items) >= safe_limit:
            break
    return {"ok": True, "path": _to_text(path) or "Source/", "total": len(items), "items": items}


def glob_source(pattern: str = "**/*", *, limit: int = 200) -> Dict[str, Any]:
    normalized_pattern = _to_text(pattern) or "**/*"
    if normalized_pattern.startswith("Source/"):
        normalized_pattern = normalized_pattern[len("Source/") :]
    safe_limit = _safe_limit(limit, default=200, high=1000)
    matches: List[Dict[str, Any]] = []
    for path in _iter_source_files():
        rel = path.relative_to(source_root().resolve()).as_posix()
        if fnmatch(rel, normalized_pattern) or fnmatch(f"Source/{rel}", normalized_pattern):
            matches.append({"path": f"Source/{rel}", "kind": "source_file", "size": path.stat().st_size})
            if len(matches) >= safe_limit:
                break
    return {"ok": True, "pattern": pattern, "total": len(matches), "matches": matches}


def _path_matches(path: Path, path_glob: str) -> bool:
    normalized = _to_text(path_glob)
    if not normalized:
        return True
    if normalized.startswith("Source/"):
        normalized = normalized[len("Source/") :]
    rel = path.relative_to(source_root().resolve()).as_posix()
    return fnmatch(rel, normalized) or fnmatch(f"Source/{rel}", normalized)


def grep_source(
    pattern: str,
    *,
    path_glob: str = "",
    regex: bool = False,
    case_sensitive: bool = False,
    limit: int = 50,
    context: int = 2,
) -> Dict[str, Any]:
    raw_pattern = _to_text(pattern)
    if not raw_pattern:
        return {"ok": False, "error": "pattern_required", "matches": []}
    if len(raw_pattern) > MAX_GREP_PATTERN_LENGTH:
        return {"ok": False, "error": "pattern_too_long", "matches": []}

    flags = 0 if case_sensitive else re.IGNORECASE
    compiled = None
    if regex:
        try:
            compiled = re.compile(raw_pattern, flags)
        except re.error as exc:
            return {"ok": False, "error": f"invalid_regex: {exc}", "matches": []}

    safe_limit = _safe_limit(limit, default=50, high=500)
    safe_context = max(0, min(int(context or 0), 8))
    needle = raw_pattern if case_sensitive else raw_pattern.lower()
    matches: List[Dict[str, Any]] = []
    for path in _iter_source_files():
        if not _path_matches(path, path_glob):
            continue
        lines = _read_lines(path)
        for idx, line in enumerate(lines):
            haystack = line if case_sensitive else line.lower()
            found = bool(compiled.search(line) if compiled else needle in haystack)
            if not found:
                continue
            start = max(0, idx - safe_context)
            end = min(len(lines), idx + safe_context + 1)
            snippet = "\n".join(f"{line_no + 1}: {lines[line_no]}" for line_no in range(start, end))
            matches.append(
                {
                    "path": _source_path(path),
                    "line": idx + 1,
                    "line_text": line,
                    "line_range": f"{start + 1}-{end}",
                    "snippet": _clip_text(snippet, 2000),
                }
            )
            if len(matches) >= safe_limit:
                return {
                    "ok": True,
                    "pattern": raw_pattern,
                    "path_glob": path_glob,
                    "total": len(matches),
                    "matches": matches,
                }
    return {"ok": True, "pattern": raw_pattern, "path_glob": path_glob, "total": len(matches), "matches": matches}


def _method_payload(record: Dict[str, Any], *, score: int = 0) -> Dict[str, Any]:
    refs = [
        {
            "path": _to_text(item.get("path")),
            "line_range": _to_text(item.get("line_range")),
        }
        for item in (record.get("source_refs") if isinstance(record.get("source_refs"), list) else [])
        if isinstance(item, dict) and _to_text(item.get("path"))
    ]
    return {
        "symbol": _to_text(record.get("qualified_symbol")),
        "qualified_type": _to_text(record.get("qualified_type")),
        "type_name": _to_text(record.get("type_name")),
        "member_name": _to_text(record.get("member_name")),
        "declaration": _to_text(record.get("declaration")),
        "kind": "symbol",
        "path": f"{METHODS_INDEX_RELATIVE_PATH}#{_to_text(record.get('qualified_symbol'))}",
        "source_refs": refs,
        "score": score,
    }


def _symbol_score(record: Dict[str, Any], query: str) -> int:
    compact_query = compact_token(query)
    if not compact_query:
        return 0
    identity = "\n".join(
        _to_text(record.get(key))
        for key in ("qualified_symbol", "qualified_type", "type_name", "member_name", "declaration", "text")
    )
    compact_identity = compact_token(identity)
    score = 0
    if compact_query in compact_token(record.get("qualified_symbol")):
        score += 80
    if compact_query in compact_token(record.get("declaration")):
        score += 50
    if compact_query in compact_identity:
        score += 20
    for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{1,}", query):
        compact = compact_token(token)
        if compact and compact in compact_identity:
            score += 5
    return score


def symbol_search(query: str, *, limit: int = 20) -> Dict[str, Any]:
    normalized_query = _to_text(query)
    safe_limit = _safe_limit(limit, default=20, high=100)
    ranked: List[Tuple[int, Dict[str, Any]]] = []
    for record in load_methods_index():
        score = _symbol_score(record, normalized_query)
        if normalized_query and score <= 0:
            continue
        ranked.append((score, record))
    ranked.sort(key=lambda item: (-item[0], _to_text(item[1].get("qualified_symbol"))))
    results = [_method_payload(record, score=score) for score, record in ranked[:safe_limit]]
    return {"ok": True, "query": normalized_query, "total": len(results), "results": results}


def read_source(path: str, *, start_line: Optional[int] = None, end_line: Optional[int] = None) -> Optional[Dict[str, Any]]:
    path_value = _to_text(path)
    if path_value.startswith(METHODS_INDEX_RELATIVE_PATH) and "#" in path_value:
        symbol = path_value.split("#", 1)[1].strip()
        for record in load_methods_index():
            if _to_text(record.get("qualified_symbol")) == symbol:
                return {"ok": True, "source_id": "raw", **_method_payload(record)}
        return None

    target = _source_file_for_path(path_value)
    if not target or not target.exists() or not target.is_file():
        return None
    lines = _read_lines(target)
    if start_line is None:
        start_index = 0
        end_index = len(lines)
    else:
        start_index = max(0, int(start_line or 1) - 1)
        end_index = min(len(lines), max(start_index + 1, int(end_line or start_index + 200)))
    content = "\n".join(f"{idx + 1}: {lines[idx]}" for idx in range(start_index, end_index))
    rel = target.relative_to(source_root().resolve()).as_posix()
    return {
        "ok": True,
        "source_id": "raw",
        "path": f"Source/{rel}",
        "title": rel,
        "kind": "source_file",
        "line_range": f"{start_index + 1}-{end_index}",
        "content": _clip_text(content, MAX_READ_CHARS),
    }


def search_source(
    *,
    query: str,
    limit: int = 12,
    include_content: bool = False,
    kind: Optional[str] = None,
) -> Dict[str, Any]:
    normalized_kind = _to_text(kind).lower()
    safe_limit = _safe_limit(limit, default=12, high=100)
    if normalized_kind in {"method", "symbol"}:
        result = symbol_search(query, limit=safe_limit)
        return {"source_id": "raw", "query": _to_text(query), "total": result["total"], "results": result["results"]}
    if normalized_kind in {"file", "source_file"}:
        result = glob_source(query or "**/*", limit=safe_limit)
        return {"source_id": "raw", "query": _to_text(query), "total": result["total"], "results": result["matches"]}

    symbols = symbol_search(query, limit=max(1, safe_limit // 2))["results"]
    matches = grep_source(query, limit=max(1, safe_limit - len(symbols)), context=1)["matches"] if _to_text(query) else []
    results: List[Dict[str, Any]] = [*symbols]
    for item in matches:
        result_item = {
            "path": item["path"],
            "title": item["path"],
            "kind": "source_span",
            "line_range": item["line_range"],
            "excerpt": item["snippet"],
        }
        if include_content:
            result_item["content"] = item["snippet"]
        results.append(result_item)
    return {"source_id": "raw", "query": _to_text(query), "total": len(results), "results": results[:safe_limit]}


__all__ = [
    "get_context",
    "glob_source",
    "grep_source",
    "list_source",
    "methods_index_file",
    "read_source",
    "rebuild_index",
    "runtime_root",
    "search_source",
    "source_manifest_file",
    "source_root",
    "symbol_search",
]

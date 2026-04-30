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
MAX_READ_CHARS = 6000
DEFAULT_READ_LINES = 120
MAX_READ_LINES = 180
MAX_GREP_PATTERN_LENGTH = 200
TYPE_GRAPH_RESULT_CHARS = 15000
_NAMESPACE_DECL_RE = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_]*)\b")

_INDEX_CACHE: Dict[str, Any] = {"mtime": 0.0, "records": []}
_ENUM_CACHE: Dict[str, List[str]] = {}
_TYPE_CACHE: Dict[str, Any] = {"root": "", "records": []}
_LINE_CACHE: Dict[str, Tuple[float, List[str]]] = {}
_NORMALIZED_LINE_CACHE: Dict[str, Tuple[float, List[str]]] = {}


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


def _normalized_token(value: Any) -> str:
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
    cache_key = path.resolve().as_posix()
    try:
        mtime = path.stat().st_mtime
    except Exception:
        mtime = 0.0
    cached = _LINE_CACHE.get(cache_key)
    if cached and cached[0] == mtime:
        return list(cached[1])
    try:
        lines = _read_source_text(path).splitlines()
    except Exception:
        return []
    _LINE_CACHE[cache_key] = (mtime, lines)
    return list(lines)


def _read_normalized_lines(path: Path) -> List[str]:
    cache_key = path.resolve().as_posix()
    try:
        mtime = path.stat().st_mtime
    except Exception:
        mtime = 0.0
    cached = _NORMALIZED_LINE_CACHE.get(cache_key)
    if cached and cached[0] == mtime:
        return list(cached[1])
    normalized = [_normalized_token(line) for line in _read_lines(path)]
    _NORMALIZED_LINE_CACHE[cache_key] = (mtime, normalized)
    return list(normalized)


def _source_context(lines: List[str], *, start_index: int, end_index: int) -> Dict[str, Any]:
    namespaces: List[Dict[str, Any]] = []
    seen_namespaces = set()
    for idx, line in enumerate(lines[:end_index]):
        match = re.match(r"\s*namespace\s+([A-Za-z_][A-Za-z0-9_]*)\b", line)
        if not match:
            continue
        name = match.group(1)
        if name in seen_namespaces:
            continue
        namespaces.append({"name": name, "line": idx + 1, "text": line.strip()})
        seen_namespaces.add(name)

    declarations: List[Dict[str, Any]] = []
    declaration_pattern = re.compile(
        r"^\s*(?:(?:public|private|protected|internal)\s+)*(?:(?:ref|value)\s+)?"
        r"(?:class|struct|interface|enum(?:\s+class)?)\s+[A-Za-z_][A-Za-z0-9_]*\b"
    )
    for idx in range(0, end_index):
        line = lines[idx]
        if declaration_pattern.match(line):
            declarations.append({"line": idx + 1, "text": line.strip()})

    return {
        "namespace_path": ".".join(item["name"] for item in namespaces),
        "namespaces": namespaces,
        "declarations": declarations[-8:],
    }


def _strip_inline_comment(line: str) -> str:
    text = str(line or "")
    if "/*" in text:
        text = text.split("/*", 1)[0]
    if "//" in text and not text.strip().startswith("///"):
        text = text.split("//", 1)[0]
    return text


def _clean_doc_summary(lines: Sequence[str]) -> str:
    raw_items: List[str] = []
    for raw in lines:
        text = str(raw or "").strip()
        if text.startswith("///"):
            text = text[3:].strip()
        raw_items.append(text)
    joined = "\n".join(raw_items)
    summary_match = re.search(r"<summary\b[^>]*>(.*?)</summary>", joined, re.IGNORECASE | re.DOTALL)
    source = summary_match.group(1) if summary_match else joined.split("<example", 1)[0].split("<code", 1)[0]
    cleaned: List[str] = []
    for text in source.splitlines():
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            cleaned.append(text)
    return " ".join(cleaned).strip()


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
            },
        )
        item["file_count"] += 1
        item["header_count"] += 1 if path.suffix.lower() in {".h", ".hpp"} else 0
        item["implementation_count"] += 1 if path.suffix.lower() in {".cpp", ".cxx", ".cc", ".cs"} else 0

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
    modules = manifest.get("modules") if isinstance(manifest.get("modules"), list) else []
    module_summaries = [
        {
            "module": _to_text(item.get("module")),
            "file_count": int(item.get("file_count") or 0),
            "header_count": int(item.get("header_count") or 0),
            "implementation_count": int(item.get("implementation_count") or 0),
        }
        for item in modules
        if isinstance(item, dict)
    ]
    return {
        "source": {
            "id": "raw",
            "root_path": source_root().as_posix(),
            "runtime_path": runtime_root().as_posix(),
            "method_count": int(manifest.get("method_count") or 0),
            "file_count": int(manifest.get("file_count") or 0),
            "generated_at": _to_text(manifest.get("generated_at")),
        },
        "modules": module_summaries,
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
    if "/" not in normalized and "\\" not in normalized and not any(ch in normalized for ch in "*?[]"):
        normalized = f"**/{normalized}"
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
                    "start_line": start + 1,
                    "end_line": end,
                    "line_text": line,
                    "line_range": f"{start + 1}-{end}",
                    "snippet": _clip_text(snippet, 1200),
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


def _method_payload(record: Dict[str, Any], *, include_doc: bool = False) -> Dict[str, Any]:
    refs = [
        {
            "path": _to_text(item.get("path")),
            "line_range": _to_text(item.get("line_range")),
        }
        for item in (record.get("source_refs") if isinstance(record.get("source_refs"), list) else [])
        if isinstance(item, dict) and _to_text(item.get("path"))
    ]
    csharp_signature = _csharp_signature(record.get("declaration"))
    shape = _csharp_signature_shape(csharp_signature)
    enum_literals = {
        type_name: _enum_literals(type_name)
        for type_name in [shape.get("return_type_name"), *shape.get("parameter_type_names", [])]
        if _to_text(type_name).startswith("e") and _enum_literals(_to_text(type_name))
    }
    payload = {
        "symbol": _to_text(record.get("qualified_symbol")),
        "qualified_type": _to_text(record.get("qualified_type")),
        "type_name": _to_text(record.get("type_name")),
        "member_name": _to_text(record.get("member_name")),
        "declaration": _to_text(record.get("declaration")),
        "csharp_signature": csharp_signature,
        "return_type": shape.get("return_type"),
        "parameter_types": shape.get("parameter_types", []),
        "kind": "symbol",
        "path": f"{METHODS_INDEX_RELATIVE_PATH}#{_to_text(record.get('qualified_symbol'))}",
        "source_refs": refs,
    }
    if enum_literals:
        payload["enum_literals"] = enum_literals
    if include_doc:
        payload["owner"] = record.get("owner") if isinstance(record.get("owner"), dict) else {}
        doc = record.get("doc") if isinstance(record.get("doc"), dict) else {}
        payload["doc"] = {key: value for key, value in doc.items() if key != "examples"}
    return payload


def _symbol_identity(record: Dict[str, Any]) -> str:
    return _normalized_token(
        "\n".join(
            [
                *(_to_text(record.get(key)) for key in ("qualified_symbol", "qualified_type", "type_name", "member_name", "declaration")),
            ]
        )
    )


def _query_word_tokens(query: str) -> List[str]:
    tokens: List[str] = []
    for item in re.findall(r"[\w#.+]{2,}", _to_text(query), flags=re.UNICODE):
        text = item.strip("_.+")
        if len(text) < 2 or not any(ch.isalnum() for ch in text):
            continue
        if text not in tokens:
            tokens.append(text)
    return tokens


def _is_ascii_identifier(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", _to_text(value)))


def _query_identifier_tokens(query: str) -> List[str]:
    tokens: List[str] = []
    named_api_tokens = {
        _to_text(match)
        for match in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+API(?=$|[^A-Za-z0-9_])", _to_text(query), flags=re.IGNORECASE)
    }
    expanded_tokens: List[str] = []
    for token in _query_word_tokens(query):
        expanded_tokens.append(token)
        expanded_tokens.extend(part for part in re.split(r"[.#:+]+", token) if part)
    for token in expanded_tokens:
        if not _is_ascii_identifier(token) or len(token) < 4:
            continue
        letters = [ch for ch in token if ch.isalpha()]
        upper_count = sum(1 for ch in letters if ch.isupper())
        has_digit = any(ch.isdigit() for ch in token)
        has_case_shape = bool(letters) and upper_count >= 2 and upper_count < len(letters)
        has_acronym_shape = upper_count >= 2
        if token not in named_api_tokens and not (has_digit or has_case_shape or has_acronym_shape):
            continue
        if token not in tokens:
            tokens.append(token)
    return tokens


def _query_primary_terms(query: str) -> List[str]:
    terms: List[str] = []
    for item in _query_word_tokens(query):
        token_key = _normalized_token(item)
        if len(token_key) > 1 and token_key not in terms:
            terms.append(token_key)
    return terms


def _query_terms(query: str) -> List[str]:
    terms: List[str] = []
    for item in _query_word_tokens(query):
        candidates = [item]
        if _is_ascii_identifier(item):
            candidates.extend(re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+", item))
        for candidate in candidates:
            token_key = _normalized_token(candidate)
            if len(token_key) > 1 and token_key not in terms:
                terms.append(token_key)
    return terms


def _record_match_order(record: Dict[str, Any], query: str) -> Optional[Tuple[int, str]]:
    query_key = _normalized_token(query)
    terms = _query_terms(query)
    identity = _symbol_identity(record)
    member_identity = _normalized_token(record.get("member_name"))
    type_identity = _normalized_token(record.get("type_name"))
    doc = record.get("doc") if isinstance(record.get("doc"), dict) else {}
    summary = _normalized_token(doc.get("summary"))
    if not query_key and not terms:
        return 0, _to_text(record.get("qualified_symbol"))
    exact = bool(query_key and query_key in identity)
    term_hits = sum(1 for term in terms if term in identity or term in summary)
    member_hits = sum(1 for term in terms if term and term == member_identity)
    type_hits = sum(1 for term in terms if term and term == type_identity)
    if not exact and term_hits <= 0:
        return None
    return -(40 * member_hits) - (20 * type_hits) - (20 if exact else 0) - term_hits, _to_text(record.get("qualified_symbol"))


def _symbol_matches(record: Dict[str, Any], query: str) -> bool:
    if not _normalized_token(query) and not _query_terms(query):
        return True
    return _record_match_order(record, query) is not None


def symbol_search(query: str, *, limit: int = 20) -> Dict[str, Any]:
    normalized_query = _to_text(query)
    safe_limit = _safe_limit(limit, default=20, high=100)
    matches: List[Tuple[Tuple[int, str], Dict[str, Any]]] = []
    for record in load_methods_index():
        order = _record_match_order(record, normalized_query)
        if normalized_query and order is None:
            continue
        matches.append((order or (0, _to_text(record.get("qualified_symbol"))), record))
    matches.sort(key=lambda item: item[0])
    results = [_method_payload(record) for _, record in matches[:safe_limit]]
    return {"ok": True, "query": normalized_query, "total": len(results), "results": results}


def _declaration_type_tokens(declaration: str) -> List[str]:
    ignored = {
        "OutAttribute",
        "String",
        "Boolean",
        "bool",
        "void",
        "int",
        "long",
        "double",
        "float",
        "char",
        "array",
        "cli",
        "property",
        "virtual",
        "static",
        "const",
        "ref",
        "class",
    }
    tokens: List[str] = []
    for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", _to_text(declaration)):
        if token in ignored:
            continue
        if token not in tokens:
            tokens.append(token)
    return tokens[:16]


def _split_parameters(params: str) -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    depth = 0
    for char in str(params or ""):
        if char in "(<[":
            depth += 1
        elif char in ")>]":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)
    part = "".join(current).strip()
    if part:
        parts.append(part)
    return parts


def _csharp_type(type_text: str) -> str:
    text = _to_text(type_text)
    text = re.sub(r"\[[^\]]+\]", " ", text)
    array_match = re.fullmatch(r"cli::array<\s*(?P<inner>.+?)\s*>\s*\^?", text)
    if array_match:
        return f"{_csharp_type(array_match.group('inner'))}[]"
    text = text.replace("cli::array<", "")
    text = text.replace("System::", "System.")
    text = re.sub(r"\bString\b\^?", "string", text)
    text = re.sub(r"\bBoolean\b", "bool", text)
    text = re.sub(r"\bInt32\b", "int", text)
    text = text.replace("^", "").replace("%", "")
    text = re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*::", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or "void"


def _csharp_parameter(param: str) -> str:
    raw = _to_text(param)
    direction = "out " if "[OutAttribute]" in raw else ""
    raw = raw.replace("[OutAttribute]", " ")
    if "%" in raw and not direction:
        direction = "ref "
    raw = raw.replace("^", "").replace("%", "")
    raw = re.sub(r"\s+", " ", raw).strip()
    match = re.match(r"(?P<type>.+?)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)$", raw)
    if not match:
        return direction + _csharp_type(raw)
    return f"{direction}{_csharp_type(match.group('type'))} {match.group('name')}"


def _csharp_signature(declaration: Any) -> str:
    text = _to_text(declaration).rstrip(";")
    property_match = re.match(r"property\s+(?P<type>.+?)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*(?P<rest>\{.*\})?", text)
    if property_match:
        return f"{_csharp_type(property_match.group('type'))} {property_match.group('name')} {{ get; set; }}"
    match = re.match(r"(?P<head>.+?)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\((?P<params>.*)\)$", text)
    if not match:
        return _csharp_type(text)
    return_type = _csharp_type(match.group("head"))
    name = match.group("name")
    params = ", ".join(_csharp_parameter(item) for item in _split_parameters(match.group("params")))
    return f"{return_type} {name}({params})"


_CS_PRIMITIVE_TYPES = {
    "bool",
    "byte",
    "char",
    "decimal",
    "double",
    "float",
    "int",
    "long",
    "object",
    "short",
    "string",
    "uint",
    "ulong",
    "ushort",
    "void",
    "Void",
    "Int16",
    "Int32",
    "Int64",
    "UInt16",
    "UInt32",
    "UInt64",
}


def _simple_csharp_type_name(type_text: Any) -> str:
    text = _to_text(type_text)
    text = re.sub(r"\b(ref|out|in|params)\b", " ", text)
    text = text.replace("[]", " ")
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text)
    for token in reversed(tokens):
        if token not in _CS_PRIMITIVE_TYPES:
            return token
    return ""


def _csharp_signature_shape(signature: Any) -> Dict[str, Any]:
    text = _to_text(signature)
    property_match = re.match(r"(?P<type>.+?)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\{", text)
    if property_match:
        property_type = _to_text(property_match.group("type"))
        type_name = _simple_csharp_type_name(property_type)
        return {
            "member_name": _to_text(property_match.group("name")),
            "return_type": property_type,
            "return_type_name": type_name,
            "parameter_types": [],
            "parameter_type_names": [],
        }
    method_match = re.match(r"(?P<return>.+?)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\((?P<params>.*)\)$", text)
    if not method_match:
        type_name = _simple_csharp_type_name(text)
        return {
            "member_name": "",
            "return_type": text,
            "return_type_name": type_name,
            "parameter_types": [],
            "parameter_type_names": [],
        }

    parameter_types: List[str] = []
    parameter_type_names: List[str] = []
    ref_parameter_type_names: List[str] = []
    out_parameter_type_names: List[str] = []
    for raw_param in _split_parameters(method_match.group("params")):
        param = _to_text(raw_param)
        if not param or param.lower() == "void":
            continue
        direction_match = re.match(r"\s*(ref|out)\b", param)
        direction = _to_text(direction_match.group(1)) if direction_match else ""
        param = re.sub(r"\b(ref|out|in|params)\b", " ", param)
        match = re.match(r"(?P<type>.+?)\s+[A-Za-z_][A-Za-z0-9_]*$", param.strip())
        param_type = re.sub(r"\s+", " ", _to_text(match.group("type") if match else param)).strip()
        if not param_type:
            continue
        parameter_types.append(param_type)
        param_type_name = _simple_csharp_type_name(param_type)
        if param_type_name and param_type_name not in parameter_type_names:
            parameter_type_names.append(param_type_name)
        if direction == "ref" and param_type_name and param_type_name not in ref_parameter_type_names:
            ref_parameter_type_names.append(param_type_name)
        if direction == "out" and param_type_name and param_type_name not in out_parameter_type_names:
            out_parameter_type_names.append(param_type_name)

    return_type = re.sub(r"\s+", " ", _to_text(method_match.group("return"))).strip()
    return {
        "member_name": _to_text(method_match.group("name")),
        "return_type": return_type,
        "return_type_name": _simple_csharp_type_name(return_type),
        "parameter_types": parameter_types,
        "parameter_type_names": parameter_type_names,
        "ref_parameter_type_names": ref_parameter_type_names,
        "out_parameter_type_names": out_parameter_type_names,
    }


def _enum_literals(enum_name: str) -> List[str]:
    name = _to_text(enum_name)
    if not name:
        return []
    if name in _ENUM_CACHE:
        return list(_ENUM_CACHE[name])
    enum_re = re.compile(rf"\benum\s+class\s+{re.escape(name)}\b")
    literals: List[str] = []
    for path in _iter_source_files():
        lines = _read_lines(path)
        for idx, line in enumerate(lines):
            if not enum_re.search(line):
                continue
            for body_line in lines[idx + 1 : idx + 80]:
                if "};" in body_line or body_line.strip() == "}":
                    break
                match = re.match(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|,|$)", body_line)
                if match:
                    literal = match.group(1)
                    if literal not in literals:
                        literals.append(literal)
            _ENUM_CACHE[name] = literals
            return list(literals)
    _ENUM_CACHE[name] = []
    return []


def _parse_base_types(value: str) -> List[str]:
    bases: List[str] = []
    for raw in str(value or "").split(","):
        text = re.sub(r"\b(public|protected|private|virtual)\b", " ", raw)
        text = text.replace("^", "").replace("%", "")
        text = re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*::", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if text and text not in bases:
            bases.append(text)
    return bases


def _load_type_index() -> List[Dict[str, Any]]:
    root = source_root().resolve()
    cache_key = root.as_posix()
    if _TYPE_CACHE.get("root") == cache_key and isinstance(_TYPE_CACHE.get("records"), list):
        return list(_TYPE_CACHE.get("records") or [])

    type_pattern = re.compile(
        r"^\s*(?:public\s+)?(?P<prefix>(?:ref|value)\s+)?"
        r"(?P<kind>class|struct|interface|enum(?:\s+class)?)\s+"
        r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
        r"(?:\s*:\s*(?P<bases>[^{;]+))?"
    )
    records: List[Dict[str, Any]] = []
    for header_path in sorted(root.rglob("*.h")):
        lines = _read_lines(header_path)
        namespace_stack: List[Tuple[str, int]] = []
        pending_namespaces: List[str] = []
        brace_depth = 0
        pending_summary: List[str] = []
        in_block_comment = False
        for line_number, raw_line in enumerate(lines, 1):
            line = str(raw_line or "")
            if in_block_comment:
                if "*/" not in line:
                    continue
                line = line.split("*/", 1)[1]
                in_block_comment = False
            if "/*" in line:
                before, after = line.split("/*", 1)
                if "*/" in after:
                    line = before + after.split("*/", 1)[1]
                else:
                    line = before
                    in_block_comment = True
            stripped = line.strip()
            if stripped.startswith("///"):
                pending_summary.append(stripped)
                continue

            namespace_match = _NAMESPACE_DECL_RE.match(stripped)
            if namespace_match:
                pending_namespaces.append(str(namespace_match.group(1) or "").strip())

            search_line = _strip_inline_comment(stripped)
            type_match = type_pattern.match(search_line)
            if type_match:
                type_name = str(type_match.group("name") or "").strip()
                kind = re.sub(r"\s+", " ", str(type_match.group("kind") or "")).strip()
                namespace_parts = [item[0] for item in namespace_stack]
                qualified_type = ".".join([*namespace_parts, type_name])
                records.append(
                    {
                        "qualified_type": qualified_type,
                        "type_name": type_name,
                        "kind": kind,
                        "declaration": re.sub(r"\s+", " ", search_line).strip(),
                        "bases": _parse_base_types(type_match.group("bases") or ""),
                        "source_ref": {"path": _source_path(header_path), "line_range": f"{line_number}-{line_number}"},
                        "summary": _clean_doc_summary(pending_summary),
                    }
                )
                pending_summary = []
            elif stripped and not stripped.startswith("["):
                pending_summary = []

            local_depth = brace_depth
            for char in line:
                if char == "{":
                    local_depth += 1
                    if pending_namespaces:
                        namespace_stack.append((pending_namespaces.pop(0), local_depth))
                elif char == "}":
                    local_depth -= 1
                    while namespace_stack and namespace_stack[-1][1] > local_depth:
                        namespace_stack.pop()
            brace_depth = local_depth

    _TYPE_CACHE["root"] = cache_key
    _TYPE_CACHE["records"] = records
    return list(records)


def _type_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "qualified_type": _to_text(record.get("qualified_type")),
        "type_name": _to_text(record.get("type_name")),
        "kind": _to_text(record.get("kind")),
        "declaration": _to_text(record.get("declaration")),
        "bases": record.get("bases") if isinstance(record.get("bases"), list) else [],
        "source_ref": record.get("source_ref") if isinstance(record.get("source_ref"), dict) else {},
        "summary": _to_text(record.get("summary")),
    }


_TYPE_GRAPH_SCHEMAS = {
    "declarations": ["symbol", "csharp_signature", "summary", "enum_literals", "types"],
    "types": ["type_name", "qualified_type", "bases"],
    "assignability": ["from", "to"],
    "edges": ["from", "relation", "to", "signature"],
    "operations": [
        "owner_type",
        "qualified_owner_type",
        "member_name",
        "csharp_signature",
        "returns",
        "accepts",
        "ref_accepts",
        "out_accepts",
        "enum_literals",
    ],
    "paths": ["from", "to", "steps"],
    "path_steps": ["from", "relation", "to", "member_name", "csharp_signature"],
}


def _type_graph_type_row(type_item: Dict[str, Any]) -> List[Any]:
    return [
        type_item.get("type_name") or "",
        type_item.get("qualified_type") or "",
        type_item.get("bases") if isinstance(type_item.get("bases"), list) else [],
    ]


def _type_graph_declaration_row(declaration: Dict[str, Any]) -> List[Any]:
    doc = declaration.get("doc") if isinstance(declaration.get("doc"), dict) else {}
    return [
        declaration.get("symbol") or "",
        declaration.get("csharp_signature") or "",
        doc.get("summary") or "",
        declaration.get("enum_literals") or {},
        declaration.get("types") or [],
    ]


def _type_graph_assignability_row(item: Dict[str, Any]) -> List[str]:
    return [_to_text(item.get("from")), _to_text(item.get("to"))]


def _type_graph_edge_row(item: Dict[str, Any]) -> List[str]:
    return [
        _to_text(item.get("from")),
        _to_text(item.get("relation")),
        _to_text(item.get("to")),
        _to_text(item.get("signature")),
    ]


def _type_graph_operation_row(operation: Dict[str, Any]) -> List[Any]:
    return [
        operation.get("owner_type") or "",
        operation.get("qualified_owner_type") or "",
        operation.get("member_name") or "",
        operation.get("csharp_signature") or "",
        operation.get("returns") or "",
        operation.get("accepts") or [],
        operation.get("ref_accepts") or [],
        operation.get("out_accepts") or [],
        operation.get("enum_literals") or {},
    ]


def _type_graph_path_row(path: Dict[str, Any]) -> List[Any]:
    steps = []
    for step in path.get("steps") if isinstance(path.get("steps"), list) else []:
        operation = step.get("operation") if isinstance(step.get("operation"), dict) else {}
        steps.append(
            [
                _to_text(step.get("from")),
                _to_text(step.get("relation")),
                _to_text(step.get("to")),
                _to_text(operation.get("member_name")),
                _to_text(operation.get("csharp_signature")),
            ]
        )
    return [_to_text(path.get("from")), _to_text(path.get("to")), steps]


def _type_graph_output_operations(
    operations: Sequence[Dict[str, Any]],
    paths: Sequence[Dict[str, Any]],
    *,
    limit: int,
) -> List[Dict[str, Any]]:
    path_keys = set()
    for path in paths:
        for step in path.get("steps") if isinstance(path.get("steps"), list) else []:
            operation = step.get("operation") if isinstance(step.get("operation"), dict) else {}
            member_name = _to_text(operation.get("member_name"))
            signature = _to_text(operation.get("csharp_signature"))
            if member_name and signature:
                path_keys.add((member_name, signature))

    selected: List[Dict[str, Any]] = []
    seen = set()

    def append(operation: Dict[str, Any]) -> None:
        member_name = _to_text(operation.get("member_name"))
        signature = _to_text(operation.get("csharp_signature"))
        key = (member_name, signature)
        if not member_name or not signature or key in seen:
            return
        seen.add(key)
        selected.append(operation)

    for operation in operations[:limit]:
        append(operation)
    for operation in operations:
        key = (_to_text(operation.get("member_name")), _to_text(operation.get("csharp_signature")))
        if key in path_keys:
            append(operation)
    return selected


def _json_chars(payload: Any) -> int:
    return len(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def _path_operation_signatures(path_rows: Sequence[List[Any]]) -> set:
    signatures = set()
    for path in path_rows:
        if not isinstance(path, list) or len(path) < 3 or not isinstance(path[2], list):
            continue
        for step in path[2]:
            if isinstance(step, list) and len(step) >= 5:
                signature = _to_text(step[4])
                if signature:
                    signatures.add(signature)
    return signatures


def _operation_row_signature(row: Any) -> str:
    if isinstance(row, list) and len(row) >= 4:
        return _to_text(row[3])
    return ""


def _select_operation_rows(
    rows: Sequence[List[Any]],
    path_rows: Sequence[List[Any]],
    *,
    limit: int,
) -> List[List[Any]]:
    path_signatures = _path_operation_signatures(path_rows)
    selected: List[List[Any]] = []
    seen = set()

    def append(row: List[Any]) -> None:
        signature = _operation_row_signature(row)
        key = signature or _json_chars(row)
        if key in seen:
            return
        seen.add(key)
        selected.append(row)

    for row in rows[: max(0, limit)]:
        append(row)
    for row in rows:
        if _operation_row_signature(row) in path_signatures:
            append(row)
    return selected


def _fit_type_graph_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if _json_chars(payload) <= TYPE_GRAPH_RESULT_CHARS:
        return payload

    budgets = (
        (4, 16, 72, 3, 80),
        (4, 12, 56, 3, 64),
        (3, 10, 44, 2, 48),
        (2, 8, 32, 2, 32),
        (1, 6, 24, 1, 16),
        (1, 4, 16, 1, 8),
    )
    best: Dict[str, Any] = payload
    for declaration_limit, type_limit, operation_limit, path_limit, assignability_limit in budgets:
        path_rows = payload.get("paths")[:path_limit] if isinstance(payload.get("paths"), list) else []
        operation_rows = (
            _select_operation_rows(payload.get("operations") or [], path_rows, limit=operation_limit)
            if isinstance(payload.get("operations"), list)
            else []
        )
        candidate = {
            **payload,
            "declarations": payload.get("declarations", [])[:declaration_limit],
            "types": payload.get("types", [])[:type_limit],
            "assignability": payload.get("assignability", [])[:assignability_limit],
            "operations": operation_rows,
            "paths": path_rows,
        }
        best = candidate
        if _json_chars(candidate) <= TYPE_GRAPH_RESULT_CHARS:
            return candidate

    while _json_chars(best) > TYPE_GRAPH_RESULT_CHARS and len(best.get("operations") or []) > 1:
        best = {**best, "operations": best["operations"][:-1]}
    return best


def _line_range_bounds(value: Any, *, padding: int = 1) -> Tuple[Optional[int], Optional[int]]:
    match = re.match(r"\s*(\d+)(?:\s*-\s*(\d+))?", _to_text(value))
    if not match:
        return None, None
    start = max(1, int(match.group(1)) - padding)
    end = int(match.group(2) or match.group(1)) + padding
    return start, max(start, end)


def _read_targets_for_method(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    targets: List[Dict[str, Any]] = []
    symbol_path = _to_text(payload.get("path"))
    if symbol_path:
        targets.append({"kind": "symbol", "path": symbol_path})
    for ref in payload.get("source_refs") if isinstance(payload.get("source_refs"), list) else []:
        path = _to_text(ref.get("path")) if isinstance(ref, dict) else ""
        if not path:
            continue
        start_line, end_line = _line_range_bounds(ref.get("line_range"))
        target = {"kind": "source_span", "path": path}
        if start_line is not None and end_line is not None:
            target.update({"start_line": start_line, "end_line": end_line})
        targets.append(target)
    return targets


def _candidate_from_method(record: Dict[str, Any], *, reason: str) -> Dict[str, Any]:
    payload = _method_payload(record, include_doc=True)
    shape = _csharp_signature_shape(payload.get("csharp_signature"))
    doc = payload.get("doc") if isinstance(payload.get("doc"), dict) else {}
    return {
        "kind": "symbol",
        "reason": reason,
        "symbol": payload.get("symbol"),
        "qualified_type": payload.get("qualified_type"),
        "type_name": payload.get("type_name"),
        "member_name": payload.get("member_name"),
        "csharp_signature": payload.get("csharp_signature"),
        "return_type": payload.get("return_type"),
        "parameter_types": payload.get("parameter_types") or [],
        "ref_parameter_types": shape.get("ref_parameter_type_names") or [],
        "out_parameter_types": shape.get("out_parameter_type_names") or [],
        "enum_literals": payload.get("enum_literals") or {},
        "summary": _to_text(doc.get("summary")),
        "path": payload.get("path"),
        "source_refs": payload.get("source_refs") or [],
        "read_targets": _read_targets_for_method(payload),
    }


def _candidate_for_output(candidate: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "kind": candidate.get("kind"),
        "reason": candidate.get("reason"),
        "symbol": candidate.get("symbol"),
        "qualified_type": candidate.get("qualified_type"),
        "type_name": candidate.get("type_name"),
        "member_name": candidate.get("member_name"),
        "csharp_signature": candidate.get("csharp_signature"),
        "return_type": candidate.get("return_type"),
        "parameter_types": candidate.get("parameter_types") or [],
        "ref_parameter_types": candidate.get("ref_parameter_types") or [],
        "out_parameter_types": candidate.get("out_parameter_types") or [],
        "enum_literals": candidate.get("enum_literals") or {},
        "summary": candidate.get("summary"),
        "path": candidate.get("path"),
    }


def _candidate_reason_rank(reason: str) -> int:
    ranks = {
        "exact_identifier": 0,
        "declaration": 1,
        "graph_path": 2,
        "graph_operation": 3,
        "type_member": 4,
        "owner_constructor": 5,
        "related_type_operation": 6,
        "constructor": 7,
        "graph_declaration": 8,
        "symbol": 9,
    }
    return ranks.get(_to_text(reason), 20)


def _candidate_output_order(candidate: Dict[str, Any], query: str) -> Tuple[int, int, Tuple[int, str], str]:
    type_key = _normalized_token(candidate.get("type_name"))
    query_key = _normalized_token(query)
    return (
        _candidate_reason_rank(_to_text(candidate.get("reason"))),
        0 if type_key and type_key in query_key else 1,
        _member_order_for_graph(
            {
                "declaration": candidate.get("declaration") or candidate.get("csharp_signature"),
                "member_name": candidate.get("member_name"),
                "type_name": candidate.get("type_name"),
                "doc": {"summary": candidate.get("summary")},
            },
            query,
            candidate.get("parameter_types") or [],
        ),
        _to_text(candidate.get("symbol")),
    )


def _constructor_record_order(record: Dict[str, Any]) -> Tuple[int, int, int, str]:
    declaration = _to_text(record.get("declaration"))
    signature = _csharp_signature(declaration)
    shape = _csharp_signature_shape(signature)
    parameter_count = len(shape.get("parameter_type_names") or [])
    lifecycle = 1 if declaration.lstrip().startswith(("!", "~")) else 0
    return lifecycle, parameter_count, len(signature), _to_text(record.get("qualified_symbol"))


def _csharp_ref_constraints(candidates: Sequence[Dict[str, Any]], relations: Sequence[Any]) -> List[Dict[str, Any]]:
    candidate_types = {_to_text(candidate.get("type_name")) for candidate in candidates if _to_text(candidate.get("type_name"))}
    constraints: List[Dict[str, Any]] = []
    for candidate in candidates:
        for ref_type in candidate.get("ref_parameter_types") if isinstance(candidate.get("ref_parameter_types"), list) else []:
            ref_type_text = _to_text(ref_type)
            assignable_types = [
                _to_text(row[0])
                for row in relations
                if isinstance(row, list)
                and len(row) >= 2
                and _to_text(row[1]) == ref_type_text
                and _to_text(row[0]) in candidate_types
            ]
            if assignable_types:
                constraints.append(
                    {
                        "symbol": candidate.get("symbol"),
                        "csharp_signature": candidate.get("csharp_signature"),
                        "ref_parameter_type": ref_type_text,
                        "required_variable_type": ref_type_text,
                        "assignable_types": assignable_types,
                        "call_note": (
                            f"Declare a {ref_type_text} variable before calling this ref parameter; "
                            f"assign derived values such as {', '.join(assignable_types)} to that variable first."
                        ),
                    }
                )
    return constraints


def _append_usage_term(terms: List[str], seen: set, value: Any) -> None:
    key = _normalized_token(value)
    if len(key) < 4 or key in seen:
        return
    seen.add(key)
    terms.append(key)


def _usage_terms_for_candidates(candidates: Sequence[Dict[str, Any]], query: str) -> List[str]:
    terms: List[str] = []
    seen = set()
    for token in _query_identifier_tokens(query):
        _append_usage_term(terms, seen, token)
    exact_candidates = [candidate for candidate in candidates if _to_text(candidate.get("reason")) == "exact_identifier"]
    seed_candidates = exact_candidates if exact_candidates else list(candidates[:48])
    for candidate in seed_candidates[:48]:
        _append_usage_term(terms, seen, candidate.get("member_name"))
        _append_usage_term(terms, seen, candidate.get("type_name"))
        _append_usage_term(terms, seen, candidate.get("return_type"))
        for parameter_type in candidate.get("parameter_types") if isinstance(candidate.get("parameter_types"), list) else []:
            _append_usage_term(terms, seen, parameter_type)
    return terms[:36]


def _source_usage_spans_for_candidates(
    candidates: Sequence[Dict[str, Any]],
    query: str,
    *,
    limit: int,
) -> List[Dict[str, Any]]:
    terms = _usage_terms_for_candidates(candidates, query)
    if len(terms) < 3:
        return []

    ranked_windows: List[Tuple[Tuple[int, int, str], Path, int, int, List[str]]] = []
    for path in _iter_source_files():
        lines = _read_lines(path)
        if not lines:
            continue
        normalized_lines = _read_normalized_lines(path)
        file_key = "".join(normalized_lines)
        present_terms = [term for term in terms if term in file_key]
        if len(present_terms) < 3:
            continue
        anchors = [
            idx
            for idx, line_key in enumerate(normalized_lines)
            if any(term in line_key for term in present_terms[:16])
        ]
        for anchor in anchors[:80]:
            start = max(0, anchor - 24)
            end = min(len(lines), anchor + 40)
            window_key = "".join(normalized_lines[start:end])
            hits = [term for term in present_terms if term in window_key]
            if len(hits) < 3:
                continue
            code_lines = sum(1 for line in lines[start:end] if "(" in line and (")" in line or ";" in line))
            score = (len(hits) * 10) + min(code_lines, 12)
            ranked_windows.append(((-score, end - start, _source_path(path)), path, start, end, hits))

    spans: List[Dict[str, Any]] = []
    selected_ranges: List[Tuple[Path, int, int]] = []
    for _, path, start, end, hits in sorted(ranked_windows, key=lambda item: item[0]):
        overlaps = any(
            path == selected_path and start <= selected_end and end >= selected_start
            for selected_path, selected_start, selected_end in selected_ranges
        )
        if overlaps:
            continue
        selected_ranges.append((path, start, end))
        content = "\n".join(f"{idx + 1}: {line}" for idx, line in enumerate(_read_lines(path)[start:end], start))
        spans.append(
            {
                "symbol": "source usage",
                "path": _source_path(path),
                "line_range": f"{start + 1}-{end}",
                "content": _clip_text(content, 2200),
                "matched_terms": hits[:12],
            }
        )
        if len(spans) >= limit:
            break
    return spans


def _source_spans_for_candidates(candidates: Sequence[Dict[str, Any]], *, query: str, limit: int) -> List[Dict[str, Any]]:
    spans: List[Dict[str, Any]] = []
    seen = set()
    for span in _source_usage_spans_for_candidates(candidates, query, limit=min(3, limit)):
        key = (span.get("path"), span.get("line_range"))
        if key in seen:
            continue
        seen.add(key)
        spans.append(span)
        if len(spans) >= limit:
            return spans
    for candidate in candidates:
        candidate_targets = candidate.get("read_targets") if isinstance(candidate.get("read_targets"), list) else []
        source_targets = [
            target
            for target in candidate_targets
            if isinstance(target, dict) and _to_text(target.get("kind")) == "source_span"
        ]
        if not source_targets:
            source_targets = [
                target
                for target in candidate_targets
                if isinstance(target, dict)
            ]
        for target in source_targets[:1]:
            path = _to_text(target.get("path"))
            if not path:
                continue
            key = (path, target.get("start_line"), target.get("end_line"))
            if key in seen:
                continue
            seen.add(key)
            source = read_source(path, start_line=target.get("start_line"), end_line=target.get("end_line"))
            if not source:
                continue
            spans.append(
                {
                    "symbol": candidate.get("symbol"),
                    "csharp_signature": candidate.get("csharp_signature"),
                    "path": source.get("path"),
                    "line_range": source.get("line_range"),
                    "content": _clip_text(source.get("content"), 1600),
                }
            )
            break
        if len(spans) >= limit:
            break
    return spans


def _record_by_symbol() -> Dict[str, Dict[str, Any]]:
    return {
        _to_text(record.get("qualified_symbol")): record
        for record in load_methods_index()
        if _to_text(record.get("qualified_symbol"))
    }


def _find_record_by_signature(
    records: Sequence[Dict[str, Any]],
    *,
    signature: str,
    member_name: str = "",
    owner_type: str = "",
) -> Optional[Dict[str, Any]]:
    signature_text = _to_text(signature)
    if not signature_text:
        return None
    member_key = _normalized_token(member_name)
    owner_key = _normalized_token(owner_type)
    for record in records:
        if _to_text(_csharp_signature(record.get("declaration"))) != signature_text:
            continue
        if member_key and member_key != _normalized_token(record.get("member_name")):
            continue
        if owner_key and owner_key != _normalized_token(record.get("type_name")):
            continue
        return record
    return None


def _is_direct_symbol_query(record: Dict[str, Any], query: str) -> bool:
    query_key = _normalized_token(query)
    terms = set(_query_terms(query))
    type_key = _normalized_token(record.get("type_name"))
    member_key = _normalized_token(record.get("member_name"))
    return bool(
        type_key
        and member_key
        and member_key != type_key
        and (type_key in terms or type_key in query_key)
        and (member_key in terms or member_key in query_key)
    )


def find_source(query: str, *, limit: int = 12) -> Dict[str, Any]:
    normalized_query = _to_text(query)
    safe_limit = _safe_limit(limit, default=12, high=40)
    records = load_methods_index()
    by_symbol = _record_by_symbol()
    candidates: List[Dict[str, Any]] = []
    type_members: List[Dict[str, Any]] = []
    seen_candidates = set()

    def append_record(record: Optional[Dict[str, Any]], reason: str) -> None:
        if not record:
            return
        if _to_text(record.get("declaration")).lstrip().startswith(("!", "~")):
            return
        candidate = _candidate_from_method(record, reason=reason)
        symbol = _to_text(candidate.get("symbol"))
        signature = _to_text(candidate.get("csharp_signature"))
        key = (symbol, signature)
        if not symbol or key in seen_candidates:
            return
        seen_candidates.add(key)
        candidates.append(candidate)

    def append_declaration_item(item: Dict[str, Any], reason: str) -> None:
        symbol = _to_text(item.get("symbol"))
        member_name = symbol.rsplit(".", 1)[-1]
        record = _find_record_by_signature(
            records,
            signature=_to_text(item.get("csharp_signature")),
            member_name=member_name,
        )
        append_record(record or by_symbol.get(symbol), reason)

    declaration_results = declaration_search(normalized_query, limit=safe_limit).get("results", [])
    graph = type_graph(normalized_query, limit=max(8, min(16, safe_limit)))

    def append_declarations() -> None:
        for item in declaration_results:
            append_declaration_item(item, "declaration")

    def append_exact_identifier_declarations() -> None:
        for token in _query_identifier_tokens(normalized_query)[:12]:
            token_key = _normalized_token(token)
            exact_items: List[Tuple[Tuple[int, Tuple[int, str], str], Dict[str, Any]]] = []
            query_key = _normalized_token(normalized_query)
            for record in records:
                member_name = _to_text(record.get("member_name"))
                if _normalized_token(member_name) != token_key:
                    continue
                symbol = _to_text(record.get("qualified_symbol"))
                type_key = _normalized_token(record.get("type_name"))
                exact_items.append(
                    (
                        (
                            0 if type_key and type_key in query_key else 1,
                            _member_order_for_graph(record, normalized_query, []),
                            symbol,
                        ),
                        record,
                    )
                )
            for _, record in sorted(exact_items, key=lambda entry: entry[0])[: min(16, safe_limit)]:
                append_record(record, "exact_identifier")

    def append_graph() -> None:
        for path in graph.get("paths") if isinstance(graph.get("paths"), list) else []:
            steps = path[2] if isinstance(path, list) and len(path) >= 3 and isinstance(path[2], list) else []
            for step in steps:
                if isinstance(step, list) and len(step) >= 5:
                    append_record(
                        _find_record_by_signature(records, signature=_to_text(step[4]), member_name=_to_text(step[3])),
                        "graph_path",
                    )
        for row in graph.get("operations") if isinstance(graph.get("operations"), list) else []:
            if isinstance(row, list) and len(row) >= 4:
                append_record(
                    _find_record_by_signature(
                        records,
                        signature=_to_text(row[3]),
                        member_name=_to_text(row[2]),
                        owner_type=_to_text(row[0]),
                    ),
                    "graph_operation",
                )
        for row in graph.get("declarations") if isinstance(graph.get("declarations"), list) else []:
            if isinstance(row, list) and row:
                record = _find_record_by_signature(
                    records,
                    signature=_to_text(row[1]) if len(row) > 1 else "",
                    member_name=_to_text(row[0]).rsplit(".", 1)[-1],
                )
                append_record(record or by_symbol.get(_to_text(row[0])), "graph_declaration")

    def append_direct_type_members() -> None:
        query_key = _normalized_token(normalized_query)
        identifier_terms = {_normalized_token(token) for token in _query_identifier_tokens(normalized_query)}
        direct_types = {
            _to_text(record.get("type_name"))
            for record in records
            if _to_text(record.get("type_name"))
            and (
                _normalized_token(record.get("type_name")) in query_key
                or any(term and term in _normalized_token(record.get("type_name")) for term in identifier_terms)
            )
        }
        if not direct_types:
            return
        ranked = [
            (_member_order_for_graph(record, normalized_query, direct_types), record)
            for record in records
            if _to_text(record.get("type_name")) in direct_types
        ]
        for _, record in sorted(ranked, key=lambda item: item[0])[: max(32, safe_limit * 2)]:
            member_candidate = _candidate_from_method(record, reason="type_member")
            if all(item.get("symbol") != member_candidate.get("symbol") for item in type_members):
                type_members.append(member_candidate)
            append_record(record, "type_member")

    top_declaration = by_symbol.get(_to_text(declaration_results[0].get("symbol"))) if declaration_results else None
    append_exact_identifier_declarations()
    if top_declaration and _is_direct_symbol_query(top_declaration, normalized_query):
        append_declarations()
        append_direct_type_members()
        append_graph()
    else:
        append_graph()
        append_direct_type_members()
        append_declarations()

    for item in symbol_search(normalized_query, limit=safe_limit * 2).get("results", []):
        append_record(by_symbol.get(_to_text(item.get("symbol"))), "symbol")

    related_type_names = {
        _to_text(candidate.get("type_name"))
        for candidate in candidates
        if _to_text(candidate.get("type_name"))
    }
    for candidate in list(candidates):
        parameter_types = candidate.get("parameter_types") if isinstance(candidate.get("parameter_types"), list) else []
        for type_name in [
            _to_text(candidate.get("return_type")),
            *(_to_text(item) for item in parameter_types),
        ]:
            if type_name:
                related_type_names.add(type_name)
    owner_type_names = {
        _to_text(candidate.get("type_name"))
        for candidate in candidates
        if _to_text(candidate.get("type_name"))
    }

    def append_constructors_for(type_names: set, reason: str) -> None:
        emitted_types = set()
        for record in sorted(records, key=_constructor_record_order):
            type_name = _to_text(record.get("type_name"))
            if not type_name or type_name not in type_names or type_name in emitted_types:
                continue
            if _to_text(record.get("member_name")) != type_name:
                continue
            if _to_text(record.get("declaration")).lstrip().startswith(("!", "~")):
                continue
            append_record(record, reason)
            emitted_types.add(type_name)

    append_constructors_for(owner_type_names, "owner_constructor")
    append_constructors_for(related_type_names, "constructor")
    related_type_keys = {_normalized_token(item) for item in related_type_names if _normalized_token(item)}
    related_added = 0
    for record in sorted(records, key=lambda item: _member_order_for_graph(item, normalized_query, related_type_names)):
        if related_added >= max(48, safe_limit * 4):
            break
        member_name = _to_text(record.get("member_name"))
        type_name = _to_text(record.get("type_name"))
        if not member_name or member_name == type_name or member_name.startswith(("~", "!")):
            continue
        signature = _csharp_signature(record.get("declaration"))
        shape = _csharp_signature_shape(signature)
        signature_types = {
            _normalized_token(shape.get("return_type_name")),
            *(_normalized_token(item) for item in shape.get("parameter_type_names", [])),
        }
        if signature_types.intersection(related_type_keys):
            append_record(record, "related_type_operation")
            related_added += 1

    file_candidates: List[Dict[str, Any]] = []
    seen_files = set()

    def append_file(path: str, reason: str, source: str = "") -> None:
        normalized_path = _to_text(path)
        if not normalized_path or normalized_path in seen_files:
            return
        seen_files.add(normalized_path)
        file_candidates.append({"kind": "source_file", "reason": reason, "path": normalized_path, "source": source})

    for candidate in candidates:
        for ref in candidate.get("source_refs") if isinstance(candidate.get("source_refs"), list) else []:
            append_file(_to_text(ref.get("path")) if isinstance(ref, dict) else "", "candidate_ref", _to_text(candidate.get("symbol")))
    for token in _query_word_tokens(normalized_query):
        if not _is_ascii_identifier(token):
            continue
        for item in glob_source(f"**/*{token}*", limit=8).get("matches", []):
            append_file(_to_text(item.get("path")), "filename", token)
            if len(file_candidates) >= safe_limit:
                break
        if len(file_candidates) >= safe_limit:
            break

    read_targets: List[Dict[str, Any]] = []
    seen_targets = set()
    for candidate in candidates:
        for target in candidate.get("read_targets") if isinstance(candidate.get("read_targets"), list) else []:
            key = json.dumps(target, ensure_ascii=False, sort_keys=True)
            if key in seen_targets:
                continue
            seen_targets.add(key)
            read_targets.append(target)
            if len(read_targets) >= safe_limit * 2:
                break
        if len(read_targets) >= safe_limit * 2:
            break

    output_candidate_limit = max(40, safe_limit * 3)
    output_type_member_limit = max(32, safe_limit * 2)
    output_candidates = sorted(candidates, key=lambda item: _candidate_output_order(item, normalized_query))[:output_candidate_limit]
    type_relations = graph.get("assignability", [])[:32]
    context = get_context()
    return {
        "ok": True,
        "query": normalized_query,
        "workspace": {
            "source_root": context.get("source_root"),
            "file_count": context.get("file_count"),
            "method_count": context.get("method_count"),
        },
        "type_relations": type_relations,
        "csharp_ref_constraints": _csharp_ref_constraints(output_candidates, type_relations),
        "type_members": [_candidate_for_output(item) for item in type_members[:output_type_member_limit]],
        "candidates": [_candidate_for_output(item) for item in output_candidates],
        "files": file_candidates[: min(8, safe_limit)],
        "read_targets": read_targets[: max(16, safe_limit)],
        "source_spans": _source_spans_for_candidates(output_candidates, query=normalized_query, limit=min(12, safe_limit)),
    }


def _type_order(record: Dict[str, Any], query: str, connected_types: Optional[Sequence[str]] = None) -> Optional[Tuple[int, str]]:
    query_key = _normalized_token(query)
    terms = _query_terms(query)
    connected = {_normalized_token(item) for item in (connected_types or []) if _normalized_token(item)}
    type_identity = _normalized_token(record.get("type_name"))
    identity = _normalized_token(
        "\n".join(
            [
                _to_text(record.get("qualified_type")),
                _to_text(record.get("type_name")),
                _to_text(record.get("declaration")),
                _to_text(record.get("summary")),
                " ".join(_to_text(item) for item in (record.get("bases") if isinstance(record.get("bases"), list) else [])),
            ]
        )
    )
    if not query_key and not terms and not connected:
        return 0, _to_text(record.get("qualified_type"))
    exact = bool(query_key and query_key in identity)
    term_hits = sum(1 for term in terms if term in identity)
    type_hits = sum(1 for term in terms if term and term in type_identity)
    connected_exact = 1 if type_identity and type_identity in connected else 0
    connected_hits = sum(1 for term in connected if term and term in identity)
    if not exact and term_hits <= 0 and connected_hits <= 0:
        return None
    return (
        -(25 * connected_exact)
        - (10 * type_hits)
        - (20 if exact else 0)
        - term_hits
        - connected_hits,
        _to_text(record.get("qualified_type")),
    )


def _member_order_for_graph(record: Dict[str, Any], query: str, connected_types: Sequence[str]) -> Tuple[int, str]:
    declaration = _to_text(record.get("declaration"))
    member = _to_text(record.get("member_name"))
    identity = _normalized_token("\n".join([member, declaration, _to_text(record.get("doc", {}).get("summary") if isinstance(record.get("doc"), dict) else "")]))
    terms = _query_terms(query)
    connected = [_normalized_token(item) for item in connected_types if _normalized_token(item)]
    rank = 0
    if member.startswith(("~", "!")):
        rank += 100
    if member and member == _to_text(record.get("type_name")):
        rank -= 10
    if "(" in declaration:
        rank -= 2
    if declaration.startswith("property "):
        rank += 8
    rank -= min(6, len(_declaration_type_tokens(declaration)))
    rank -= sum(5 for term in terms if term in identity)
    rank -= sum(3 for term in connected if term in identity)
    return rank, member


def _type_graph_edges(types: Sequence[Dict[str, Any]], known_type_names: set) -> List[Dict[str, Any]]:
    edges: List[Dict[str, Any]] = []
    edge_index: Dict[Tuple[str, str, str], int] = {}

    def append(edge: Dict[str, Any]) -> None:
        key = (_to_text(edge.get("from")), _to_text(edge.get("relation")), _to_text(edge.get("to")))
        if not key[0] or not key[2]:
            return
        existing_index = edge_index.get(key)
        if existing_index is not None:
            current_signature = _to_text(edges[existing_index].get("signature"))
            next_signature = _to_text(edge.get("signature"))
            if next_signature and (not current_signature or len(next_signature) < len(current_signature)):
                edges[existing_index] = edge
            return
        edge_index[key] = len(edges)
        edges.append(edge)

    for type_item in types:
        owner_type = _to_text(type_item.get("type_name"))
        if not owner_type:
            continue
        for base in type_item.get("bases") if isinstance(type_item.get("bases"), list) else []:
            base_name = _to_text(base)
            if base_name:
                append({"from": owner_type, "relation": "inherits", "to": base_name})

        for member in type_item.get("members") if isinstance(type_item.get("members"), list) else []:
            signature = _to_text(member.get("csharp_signature"))
            if not signature:
                continue
            shape = _csharp_signature_shape(signature)
            member_name = _to_text(member.get("member_name")) or _to_text(shape.get("member_name"))
            from_member = f"{owner_type}.{member_name}" if member_name else owner_type
            return_type = _to_text(shape.get("return_type_name"))
            if return_type and return_type in known_type_names and return_type != owner_type:
                append(
                    {
                        "from": from_member,
                        "relation": "returns",
                        "to": return_type,
                        "signature": signature,
                    }
                )
            for param_type in shape.get("parameter_type_names", []):
                target_type = _to_text(param_type)
                if target_type and target_type in known_type_names and target_type != owner_type:
                    append(
                        {
                            "from": from_member,
                            "relation": "accepts",
                            "to": target_type,
                            "signature": signature,
                        }
                    )
    return edges


def _type_edge_order(edge: Dict[str, Any], query: str, connected_types: Sequence[str]) -> Tuple[int, int, str]:
    identity = _normalized_token(
        "\n".join(
            [
                _to_text(edge.get("from")),
                _to_text(edge.get("relation")),
                _to_text(edge.get("to")),
            ]
        )
    )
    primary_terms = _query_primary_terms(query)
    terms = _query_terms(query)
    connected = [_normalized_token(item) for item in connected_types if _normalized_token(item)]
    query_key = _normalized_token(query)
    primary_hits = sum(1 for term in primary_terms if term and term in identity)
    term_hits = sum(1 for term in terms if term and term in identity)
    connected_hits = sum(1 for term in connected if term and term in identity)
    exact = 1 if query_key and query_key in identity else 0
    return (
        -(20 * exact) - (12 * primary_hits) - (4 * term_hits) - (2 * connected_hits),
        len(_to_text(edge.get("signature"))),
        f"{_to_text(edge.get('from'))}->{_to_text(edge.get('to'))}",
    )


def _sort_type_edges(edges: Sequence[Dict[str, Any]], query: str, connected_types: Sequence[str]) -> List[Dict[str, Any]]:
    return sorted(edges, key=lambda edge: _type_edge_order(edge, query, connected_types))


def _type_graph_operations(types: Sequence[Dict[str, Any]], known_type_names: set) -> List[Dict[str, Any]]:
    operations: List[Dict[str, Any]] = []
    operation_index: Dict[Tuple[str, str, str, Tuple[str, ...]], int] = {}
    for type_item in types:
        owner_type = _to_text(type_item.get("type_name"))
        if not owner_type:
            continue
        for member in type_item.get("members") if isinstance(type_item.get("members"), list) else []:
            signature = _to_text(member.get("csharp_signature"))
            if not signature:
                continue
            shape = _csharp_signature_shape(signature)
            member_name = _to_text(member.get("member_name")) or _to_text(shape.get("member_name"))
            if member_name.startswith(("~", "!")) or member_name == owner_type:
                continue
            returns = _to_text(shape.get("return_type_name"))
            accepts = [
                _to_text(type_name)
                for type_name in shape.get("parameter_type_names", [])
                if _to_text(type_name) and _to_text(type_name) in known_type_names
            ]
            if returns and returns not in known_type_names:
                returns = ""
            doc = member.get("doc") if isinstance(member.get("doc"), dict) else {}
            operation = {
                "owner_type": owner_type,
                "qualified_owner_type": type_item.get("qualified_type"),
                "member_name": member_name,
                "csharp_signature": signature,
                "summary": _to_text(doc.get("summary")),
                "returns": returns,
                "accepts": accepts,
                "ref_accepts": [
                    _to_text(type_name)
                    for type_name in shape.get("ref_parameter_type_names", [])
                    if _to_text(type_name)
                ],
                "out_accepts": [
                    _to_text(type_name)
                    for type_name in shape.get("out_parameter_type_names", [])
                    if _to_text(type_name)
                ],
                "enum_literals": member.get("enum_literals"),
                "source_refs": member.get("source_refs", [])[:1],
            }
            operation = {key: value for key, value in operation.items() if value not in ("", [], {}, None)}
            key = (owner_type, member_name, returns, tuple(accepts))
            existing_index = operation_index.get(key)
            if existing_index is not None:
                current_signature = _to_text(operations[existing_index].get("csharp_signature"))
                if len(signature) < len(current_signature):
                    operations[existing_index] = operation
                continue
            operation_index[key] = len(operations)
            operations.append(operation)
    return operations


def _operation_order(operation: Dict[str, Any], query: str, relevant_types: Sequence[str]) -> Tuple[int, int, str]:
    identity = _normalized_token(
        "\n".join(
            [
                _to_text(operation.get("owner_type")),
                _to_text(operation.get("member_name")),
                _to_text(operation.get("returns")),
                " ".join(_to_text(item) for item in operation.get("accepts", []) if item),
            ]
        )
    )
    primary_terms = _query_primary_terms(query)
    terms = _query_terms(query)
    relevant = {_normalized_token(item) for item in relevant_types if _normalized_token(item)}
    related_type_names = {
        _normalized_token(operation.get("owner_type")),
        _normalized_token(operation.get("returns")),
        *(_normalized_token(item) for item in operation.get("accepts", []) if _normalized_token(item)),
    }
    primary_hits = sum(1 for term in primary_terms if term and term in identity)
    term_hits = sum(1 for term in terms if term and term in identity)
    relevant_hits = len(related_type_names.intersection(relevant))
    member_name = _to_text(operation.get("member_name"))
    lifecycle_penalty = 8 if member_name.startswith(("~", "!")) or member_name == _to_text(operation.get("owner_type")) else 0
    return (
        lifecycle_penalty - (14 * primary_hits) - (4 * term_hits) - (5 * relevant_hits),
        len(_to_text(operation.get("csharp_signature"))),
        f"{_to_text(operation.get('owner_type'))}.{_to_text(operation.get('member_name'))}",
    )


def _sort_type_operations(
    operations: Sequence[Dict[str, Any]],
    query: str,
    relevant_types: Sequence[str],
) -> List[Dict[str, Any]]:
    return sorted(operations, key=lambda operation: _operation_order(operation, query, relevant_types))


def _type_graph_paths(
    operations: Sequence[Dict[str, Any]],
    types: Sequence[Dict[str, Any]],
    query: str,
    *,
    limit: int = 6,
) -> List[Dict[str, Any]]:
    primary_terms = _query_primary_terms(query)
    if not primary_terms:
        return []

    type_names = {
        _to_text(item.get("type_name"))
        for item in types
        if _to_text(item.get("type_name"))
    }
    weighted_query_types: List[Tuple[int, str]] = []
    for name in type_names:
        weight = sum(len(term) for term in primary_terms if term and term in _normalized_token(name))
        if weight > 0:
            weighted_query_types.append((weight, name))
    max_goal_weight = max((weight for weight, _ in weighted_query_types), default=0)
    max_weight_names = [name for weight, name in weighted_query_types if weight == max_goal_weight]
    min_goal_length = min((len(_normalized_token(name)) for name in max_weight_names), default=0)
    query_type_names = [name for name in max_weight_names if len(_normalized_token(name)) == min_goal_length]
    if not query_type_names:
        return []

    adjacency: Dict[str, List[Dict[str, Any]]] = {}

    def add_step(from_type: str, to_type: str, relation: str, operation: Optional[Dict[str, Any]] = None) -> None:
        if not from_type or not to_type or from_type == to_type:
            return
        adjacency.setdefault(from_type, []).append(
            {
                "from": from_type,
                "to": to_type,
                "relation": relation,
                "operation": operation,
            }
        )

    for operation in operations[:160]:
        if "(" not in _to_text(operation.get("csharp_signature")):
            continue
        owner = _to_text(operation.get("owner_type"))
        returns = _to_text(operation.get("returns"))
        if owner and returns:
            add_step(owner, returns, "returns", operation)
            add_step(returns, owner, "returned_by", operation)
        for accepted in operation.get("accepts", []) if isinstance(operation.get("accepts"), list) else []:
            accepted_type = _to_text(accepted)
            if accepted_type and owner:
                add_step(accepted_type, owner, "accepted_by", operation)

    for type_item in types:
        type_name = _to_text(type_item.get("type_name"))
        for base in type_item.get("bases") if isinstance(type_item.get("bases"), list) else []:
            base_name = _to_text(base)
            if type_name in _CS_PRIMITIVE_TYPES or base_name in _CS_PRIMITIVE_TYPES:
                continue
            add_step(type_name, base_name, "inherits")
            add_step(base_name, type_name, "base_of")

    def step_order(step: Dict[str, Any]) -> Tuple[int, int, str]:
        operation = step.get("operation") if isinstance(step.get("operation"), dict) else {}
        member = _to_text(operation.get("member_name"))
        member_identity = _normalized_token(member)
        signature_identity = _normalized_token(operation.get("csharp_signature"))
        from_type = _normalized_token(step.get("from"))
        to_type = _normalized_token(step.get("to"))
        member_related = 1 if (
            (from_type and from_type in member_identity)
            or (to_type and to_type in member_identity)
        ) else 0
        signature_related = 1 if (
            (from_type and from_type in signature_identity)
            or (to_type and to_type in signature_identity)
        ) else 0
        destructive_penalty = 1 if member_identity.startswith(("remove", "delete", "clear")) else 0
        relation_bonus = 1 if _to_text(step.get("relation")) == "accepted_by" else 0
        return (
            (12 * destructive_penalty) - (10 * member_related) - (4 * signature_related) - (3 * relation_bonus),
            len(member),
            len(_to_text(operation.get("csharp_signature"))),
            f"{_to_text(step.get('from'))}->{_to_text(step.get('to'))}",
        )

    for steps in adjacency.values():
        steps.sort(key=step_order)

    start_nodes: List[str] = []
    for operation in operations[:120]:
        if "(" not in _to_text(operation.get("csharp_signature")):
            continue
        identity = _normalized_token(
            "\n".join(
                [
                    _to_text(operation.get("member_name")),
                ]
            )
        )
        if not any(term and term in identity for term in primary_terms):
            continue
        for candidate in [_to_text(operation.get("returns")), _to_text(operation.get("owner_type"))]:
            if candidate and candidate in type_names and candidate not in start_nodes:
                start_nodes.append(candidate)
        for accepted in operation.get("accepts", []) if isinstance(operation.get("accepts"), list) else []:
            accepted_type = _to_text(accepted)
            if accepted_type and accepted_type in type_names and accepted_type not in start_nodes:
                start_nodes.append(accepted_type)

    paths: List[Dict[str, Any]] = []
    seen_paths = set()
    goal_nodes = set(query_type_names)
    for start in start_nodes[:16]:
        queue: List[Tuple[str, List[Dict[str, Any]]]] = [(start, [])]
        while queue and len(paths) < limit * 6:
            node, steps = queue.pop(0)
            if steps and node in goal_nodes:
                path_key = tuple((step["from"], step["relation"], step["to"]) for step in steps)
                if path_key not in seen_paths:
                    seen_paths.add(path_key)
                    paths.append(
                        {
                            "from": start,
                            "to": node,
                            "steps": [
                                {
                                    "from": step["from"],
                                    "relation": step["relation"],
                                    "to": step["to"],
                                    "operation": (
                                        {
                                            "owner_type": step["operation"].get("owner_type"),
                                            "member_name": step["operation"].get("member_name"),
                                            "csharp_signature": step["operation"].get("csharp_signature"),
                                        }
                                        if isinstance(step.get("operation"), dict)
                                        else None
                                    ),
                                }
                                for step in steps
                            ],
                        }
                    )
            if len(steps) >= 7:
                continue
            for step in adjacency.get(node, [])[:24]:
                next_node = _to_text(step.get("to"))
                path_nodes = set()
                for existing in steps:
                    path_nodes.add(_to_text(existing.get("from")))
                    path_nodes.add(_to_text(existing.get("to")))
                if not next_node or next_node in path_nodes:
                    continue
                queue.append((next_node, [*steps, step]))

    def path_order(path: Dict[str, Any]) -> Tuple[int, int, str]:
        target = _normalized_token(path.get("to"))
        target_hits = sum(1 for term in primary_terms if term and term in target)
        quality = sum(step_order(step)[0] for step in path.get("steps", []))
        return (-target_hits, quality, len(path.get("steps", [])), _to_text(path.get("to")))

    return sorted(paths, key=path_order)[:limit]


def type_graph(query: str, *, limit: int = 12) -> Dict[str, Any]:
    normalized_query = _to_text(query)
    safe_limit = _safe_limit(limit, default=12, high=20)
    declarations = declaration_search(normalized_query, limit=safe_limit).get("results", [])
    connected_types: List[str] = []
    for item in declarations:
        for token in item.get("types") if isinstance(item.get("types"), list) else []:
            if token not in connected_types:
                connected_types.append(token)
        type_name = _to_text(item.get("type_name"))
        if type_name and type_name not in connected_types:
            connected_types.append(type_name)

    type_matches: List[Tuple[Tuple[int, str], Dict[str, Any]]] = []
    for record in _load_type_index():
        order = _type_order(record, normalized_query, connected_types)
        if order is not None:
            type_matches.append((order, record))
    type_matches.sort(key=lambda item: item[0])

    selected_types: List[Dict[str, Any]] = []
    seen_type_names = set()
    type_records = _load_type_index()
    type_record_by_name = {
        _to_text(record.get("type_name")): record
        for record in type_records
        if _to_text(record.get("type_name"))
    }

    def append_type(record: Dict[str, Any]) -> None:
        type_name = _to_text(record.get("type_name"))
        if not type_name or type_name in seen_type_names:
            return
        seen_type_names.add(type_name)
        payload = _type_payload(record)
        members = [
            item
            for item in load_methods_index()
            if _to_text(item.get("type_name")) == type_name
            and not _to_text(item.get("member_name")).startswith(("~", "!"))
        ]
        members.sort(key=lambda item: _member_order_for_graph(item, normalized_query, connected_types))
        payload["members"] = [_method_payload(item, include_doc=True) for item in members[:96]]
        selected_types.append(payload)

    for _, record in type_matches:
        append_type(record)
        if len(selected_types) >= safe_limit:
            break

    assignability = []
    for item in list(selected_types):
        for base in item.get("bases") if isinstance(item.get("bases"), list) else []:
            assignability.append({"from": item["type_name"], "to": base})
            if base not in seen_type_names:
                for record in type_records:
                    if _to_text(record.get("type_name")) == base:
                        append_type(record)
                        break

    for type_name in connected_types:
        if type_name in seen_type_names:
            continue
        for record in type_records:
            if _to_text(record.get("type_name")) == type_name:
                append_type(record)
                break

    connected_keys = {_normalized_token(item) for item in seen_type_names if _normalized_token(item)}
    owner_candidates: List[Tuple[Tuple[int, str], str]] = []
    for member_record in load_methods_index():
        declaration_tokens = {_normalized_token(item) for item in _declaration_type_tokens(_to_text(member_record.get("declaration")))}
        if not declaration_tokens.intersection(connected_keys):
            continue
        owner_type = _to_text(member_record.get("type_name"))
        if not owner_type or owner_type in seen_type_names:
            continue
        order = _member_order_for_graph(member_record, normalized_query, [*seen_type_names, *connected_types])
        owner_identity = _normalized_token(owner_type)
        owner_term_hits = sum(1 for term in _query_terms(normalized_query) if term and term in owner_identity)
        order = (order[0] - (12 * owner_term_hits), order[1])
        owner_candidates.append((order, owner_type))
    for _, owner_type in sorted(owner_candidates)[: max(4, safe_limit // 2)]:
        if owner_type in seen_type_names:
            continue
        for record in type_records:
            if _to_text(record.get("type_name")) == owner_type:
                append_type(record)
                break
        if len(selected_types) >= safe_limit + 6:
            break

    derived_counts: Dict[str, int] = {}
    for record in type_records:
        bases = record.get("bases") if isinstance(record.get("bases"), list) else []
        matching_bases = [base for base in bases if base in seen_type_names and derived_counts.get(base, 0) < 4]
        if matching_bases:
            append_type(record)
            for base in matching_bases:
                derived_counts[base] = derived_counts.get(base, 0) + 1
            if matching_bases:
                assignability.extend(
                    {"from": _to_text(record.get("type_name")), "to": base}
                    for base in matching_bases
                )
    for member_record in load_methods_index():
        declaration_tokens = {_normalized_token(item) for item in _declaration_type_tokens(_to_text(member_record.get("declaration")))}
        if not declaration_tokens.intersection(connected_keys):
            continue
        owner_type = _to_text(member_record.get("type_name"))
        if not owner_type or owner_type in seen_type_names:
            continue
        for record in type_records:
            if _to_text(record.get("type_name")) == owner_type:
                append_type(record)
                break
        if len(selected_types) >= safe_limit + 8:
            break
    for _ in range(2):
        added = 0
        known_type_names = set(type_record_by_name)
        for edge in _sort_type_edges(_type_graph_edges(selected_types, known_type_names), normalized_query, [*seen_type_names, *connected_types]):
            target_type = _to_text(edge.get("to"))
            if not target_type or target_type in seen_type_names:
                continue
            record = type_record_by_name.get(target_type)
            if not record:
                continue
            append_type(record)
            added += 1
            if added >= safe_limit:
                break
        if not added:
            break
    selected_types.sort(
        key=lambda item: _type_order(item, normalized_query, connected_types)
        or (0, _to_text(item.get("qualified_type")))
    )
    primary_terms = _query_primary_terms(normalized_query)
    operation_relevant_types = [
        *connected_types,
        *(
            _to_text(type_name)
            for type_name in seen_type_names
            if any(term and term in _normalized_token(type_name) for term in primary_terms)
        ),
    ]
    all_operations = _sort_type_operations(
        _type_graph_operations(selected_types, set(type_record_by_name)),
        normalized_query,
        operation_relevant_types,
    )
    paths = _type_graph_paths(all_operations, selected_types, normalized_query, limit=min(6, safe_limit))
    operations = _type_graph_output_operations(all_operations, paths[:3], limit=safe_limit * 6)
    payload = {
        "ok": True,
        "query": normalized_query,
        "schemas": _TYPE_GRAPH_SCHEMAS,
        "declarations": [_type_graph_declaration_row(item) for item in declarations[: min(4, safe_limit)]],
        "types": [_type_graph_type_row(item) for item in selected_types[: safe_limit + 4]],
        "assignability": [_type_graph_assignability_row(item) for item in assignability],
        "edges": [],
        "operations": [_type_graph_operation_row(item) for item in operations],
        "paths": [_type_graph_path_row(item) for item in paths[:3]],
    }
    return _fit_type_graph_payload(payload)


def source_usages(query: str, *, limit: int = 12) -> Dict[str, Any]:
    normalized_query = _to_text(query)
    safe_limit = _safe_limit(limit, default=12, high=50)
    terms = _query_terms(normalized_query)
    matches: List[Dict[str, Any]] = []
    for path in _iter_source_files():
        lines = _read_lines(path)
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith(("///", "//", "*")):
                continue
            line_key = _normalized_token(stripped)
            if terms and not all(term in line_key for term in terms[:4]):
                if _normalized_token(normalized_query) not in line_key:
                    continue
            start = max(0, idx - 2)
            end = min(len(lines), idx + 3)
            snippet = "\n".join(f"{line_no + 1}: {lines[line_no]}" for line_no in range(start, end))
            matches.append(
                {
                    "path": _source_path(path),
                    "line": idx + 1,
                    "line_range": f"{start + 1}-{end}",
                    "line_text": stripped,
                    "snippet": _clip_text(snippet, 1600),
                }
            )
            if len(matches) >= safe_limit:
                return {"ok": True, "query": normalized_query, "total": len(matches), "matches": matches}
    return {"ok": True, "query": normalized_query, "total": len(matches), "matches": matches}


def declaration_search(query: str, *, limit: int = 12) -> Dict[str, Any]:
    normalized_query = _to_text(query)
    safe_limit = _safe_limit(limit, default=12, high=40)
    matches: List[Tuple[Tuple[int, str], Dict[str, Any]]] = []
    for record in load_methods_index():
        order = _record_match_order(record, normalized_query)
        if normalized_query and order is None:
            continue
        matches.append((order or (0, _to_text(record.get("qualified_symbol"))), record))
    matches.sort(key=lambda item: item[0])
    results: List[Dict[str, Any]] = []
    for _, record in matches[:safe_limit]:
        payload = _method_payload(record, include_doc=True)
        payload["types"] = _declaration_type_tokens(payload.get("declaration"))
        enum_literals = {
            token: _enum_literals(token)
            for token in payload["types"]
            if token.startswith("e") and _enum_literals(token)
        }
        if enum_literals:
            payload["enum_literals"] = enum_literals
        results.append(payload)
    return {"ok": True, "query": normalized_query, "total": len(results), "results": results}


def read_source(path: str, *, start_line: Optional[int] = None, end_line: Optional[int] = None) -> Optional[Dict[str, Any]]:
    path_value = _to_text(path)
    if path_value.startswith(METHODS_INDEX_RELATIVE_PATH) and "#" in path_value:
        symbol = path_value.split("#", 1)[1].strip()
        for record in load_methods_index():
            if _to_text(record.get("qualified_symbol")) == symbol:
                return {
                    "ok": True,
                    "source_id": "raw",
                    **_method_payload(record, include_doc=True),
                }
        return None

    target = _source_file_for_path(path_value)
    if not target or not target.exists() or not target.is_file():
        return None
    lines = _read_lines(target)
    if start_line is None:
        start_index = 0
        end_index = min(len(lines), DEFAULT_READ_LINES)
    else:
        start_index = max(0, int(start_line or 1) - 1)
        requested_end = int(end_line or start_index + DEFAULT_READ_LINES)
        end_index = min(len(lines), max(start_index + 1, min(requested_end, start_index + MAX_READ_LINES)))
    content = "\n".join(f"{idx + 1}: {lines[idx]}" for idx in range(start_index, end_index))
    rel = target.relative_to(source_root().resolve()).as_posix()
    source_path = f"Source/{rel}"
    return {
        "ok": True,
        "source_id": "raw",
        "path": source_path,
        "title": rel,
        "kind": "source_file",
        "line_range": f"{start_index + 1}-{end_index}",
        "context": _source_context(lines, start_index=start_index, end_index=end_index),
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
    remaining = max(1, safe_limit - len(symbols))
    matches = grep_source(query, limit=remaining, context=1)["matches"] if _to_text(query) else []
    results: List[Dict[str, Any]] = [*symbols]
    for item in matches:
        result_item = {
            "path": item["path"],
            "title": item["path"],
            "kind": "source_span",
            "line_range": item["line_range"],
            "excerpt": item.get("snippet") or item["line_text"],
        }
        if include_content:
            result_item["content"] = item.get("snippet") or item["line_text"]
        results.append(result_item)
    return {"source_id": "raw", "query": _to_text(query), "total": len(results), "results": results[:safe_limit]}


__all__ = [
    "find_source",
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
    "source_usages",
    "symbol_search",
    "type_graph",
]

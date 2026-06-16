import json
import re
import time
from collections import deque
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ... import config
from ._common import (
    clip,
    json_for_model,
    normalized_token as _normalized_token,
    safe_int,
    to_text as _to_text,
)
from .methods_index import _read_source_text, build_methods_index_from_raw_source


# 인덱싱/탐색 대상으로 인정하는 소스 파일 확장자 (C++/CLI 헤더·구현 + C#)


# ==========================================================================
#  1.  설정 · 상수 · 캐시
# ==========================================================================

SOURCE_EXTENSIONS = {".h", ".hpp", ".cpp", ".cxx", ".cc", ".cs"}

METHODS_INDEX_RELATIVE_PATH = ".runtime/methods_index.json"

SOURCE_MANIFEST_RELATIVE_PATH = ".runtime/source_manifest.json"

MAX_READ_CHARS = 6000

DEFAULT_READ_LINES = 120

MAX_READ_LINES = 180

MAX_GREP_PATTERN_LENGTH = 200

TYPE_GRAPH_RESULT_CHARS = config.TYPE_GRAPH_RESULT_CHARS

_NAMESPACE_DECL_RE = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_]*)\b")

# --- 모듈 수준 캐시 (프로세스 생존 동안 유지) ---
_INDEX_CACHE: Dict[str, Any] = {"mtime": 0.0, "records": []}

_ENUM_CACHE: Dict[str, List[str]] = {}

_TYPE_CACHE: Dict[str, Any] = {"root": "", "records": []}

_LINE_CACHE: Dict[str, Tuple[float, List[str]]] = {}

_NORMALIZED_LINE_CACHE: Dict[str, Tuple[float, List[str]]] = {}

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

_TYPE_GRAPH_SCHEMAS = {
    "declarations": ["symbol", "csharp_signature", "summary", "enum_literals", "types"],
    "types": ["type_name", "qualified_type", "bases"],
    "assignability": ["from", "to"],
    "event_declarations": ["type_name", "kind", "name", "declaration", "summary", "path", "line_range"],
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


# ==========================================================================
#  2.  파일 I/O · 경로 · 탐색/읽기 도구  (경로 보안 포함)
# ==========================================================================

def source_root() -> Path:
    """인덱싱 대상 SDK 원본 소스 트리의 루트 디렉터리(config.RAW_SOURCE_ROOT)를 반환한다."""
    return Path(config.RAW_SOURCE_ROOT)


def runtime_root() -> Path:
    """인덱스/manifest 산출물을 저장하는 런타임 디렉터리를 반환한다.

    config.SOURCE_RUNTIME_DIR이 상대 경로이면 백엔드 패키지 루트 기준 절대 경로로 변환한다.
    """
    root = Path(config.SOURCE_RUNTIME_DIR)
    if not root.is_absolute():
        root = Path(__file__).resolve().parents[3] / root
    return root


def methods_index_file() -> Path:
    """메서드 인덱스(methods_index.json)의 절대 경로를 반환한다."""
    return runtime_root() / PurePosixPath(METHODS_INDEX_RELATIVE_PATH).as_posix()


def source_manifest_file() -> Path:
    """소스 manifest(source_manifest.json)의 절대 경로를 반환한다."""
    return runtime_root() / PurePosixPath(SOURCE_MANIFEST_RELATIVE_PATH).as_posix()


def _as_list(container: Any, key: str) -> List[Any]:
    """container[key]가 list면 그대로, 아니면 빈 리스트. (반복되던 isinstance 가드 축약)"""
    value = container.get(key) if isinstance(container, dict) else None
    return value if isinstance(value, list) else []


def _clip_text(value: Any, limit: int = MAX_READ_CHARS) -> str:
    """텍스트를 limit 문자 이내로 절단한다. (공용 clip의 기본 limit만 MAX_READ_CHARS로 고정한 래퍼)"""
    return clip(value, limit)


def _safe_limit(value: Any, *, default: int = 50, high: int = 500) -> int:
    """외부 입력 limit 값을 1 이상 high 이하 정수로 강제한다. (공용 safe_int에 low=1 고정한 래퍼)"""
    return safe_int(value, default, 1, high)


def _is_source_file(path: Path) -> bool:
    """해당 경로가 탐색 대상 소스 파일(SOURCE_EXTENSIONS 확장자)인지 판정한다."""
    return path.is_file() and path.suffix.lower() in SOURCE_EXTENSIONS


def _iter_source_files() -> Iterable[Path]:
    """소스 루트 아래의 모든 소스 파일을 경로 정렬 순서로 순회하는 제너레이터를 반환한다."""
    root = source_root()
    if not root.exists() or not root.is_dir():
        return []
    return (path for path in sorted(root.rglob("*")) if _is_source_file(path))


def _source_path(path: Path) -> str:
    """실제 파일 경로를 API/에이전트에 노출하는 "Source/..." 가상 경로 문자열로 변환한다."""
    return f"Source/{path.relative_to(source_root().resolve()).as_posix()}"


def _source_file_for_path(path_value: str) -> Optional[Path]:
    """"Source/..." 가상 파일 경로를 실제 절대 경로로 변환한다. (경로 보안의 핵심)

    - 역슬래시를 슬래시로 통일하고 "#fragment"(심볼 표기)는 떼어낸다.
    - 절대 경로, "..", "../" 시작 등 명백한 탈출 시도는 즉시 거부한다.
    - resolve() 후 결과가 소스 루트 밖이면 None을 반환해 path traversal을 차단한다.
    """
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
    """"Source/..." 가상 디렉터리 경로를 실제 절대 경로로 변환한다.

    빈 입력은 소스 루트 자체를 가리키며, resolve() 결과가 루트 밖이면 None을
    반환해 디렉터리 탐색에서도 path traversal을 차단한다.
    """
    normalized = _to_text(path_value).replace("\\", "/")
    if normalized.startswith("Source/"):
        normalized = normalized[len("Source/") :]
    root = source_root().resolve()
    target = (root / PurePosixPath(normalized or ".").as_posix()).resolve()
    if target != root and root not in target.parents:
        return None
    return target


def _read_lines(path: Path) -> List[str]:
    """파일을 줄 단위 리스트로 읽되 _LINE_CACHE에 캐싱한다.

    캐시 키는 절대 경로이고, 저장된 mtime과 현재 mtime이 같을 때만 캐시를 재사용한다.
    인코딩 처리(_read_source_text)는 methods_index.py와 공유한다. 실패 시 빈 리스트.
    """
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
    """각 줄을 _normalized_token으로 정규화한 리스트를 mtime 기반으로 캐싱해 반환한다.

    사용처 검색(_source_usage_spans_for_candidates)에서 줄 단위 부분 문자열 매칭을
    반복 수행할 때 정규화 비용을 줄이기 위한 캐시다.
    """
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
    """읽은 구간 앞쪽에 등장한 namespace/타입 선언을 요약한 컨텍스트를 만든다.

    read_source가 파일 일부만 보여줄 때, 그 구간이 어떤 네임스페이스·클래스 안에
    있는지 모델이 알 수 있도록 namespace_path와 최근 선언 8개를 함께 제공한다.
    """
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
    """줄 끝의 "/*", "//" 주석을 제거한다. 단 문서주석 "///"으로 시작하는 줄은 보존한다."""
    text = str(line or "")
    if "/*" in text:
        text = text.split("/*", 1)[0]
    if "//" in text and not text.strip().startswith("///"):
        text = text.split("//", 1)[0]
    return text


def _clean_doc_summary(lines: Sequence[str]) -> str:
    """"///" XML 문서주석 줄들에서 사람이 읽을 요약 문장을 추출한다.

    <summary> 태그가 있으면 그 내용만, 없으면 <example>/<code> 이전 부분을 취해
    XML 태그를 제거하고 공백을 정리한 한 줄 텍스트로 합친다.
    """
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
    """JSON 파일을 읽어 파싱한다. 파일이 없거나 파싱에 실패하면 default_value를 반환한다."""
    if not path.exists():
        return default_value
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default_value


def list_source(path: str = "", *, depth: int = 1, limit: int = 200) -> Dict[str, Any]:
    """디렉터리 내용을 나열한다. (깊이 제한이 있는 `ls -R` 에 해당)

    path: "Source/..." 가상 경로(빈 값이면 루트). depth: 추가로 내려갈 깊이(0~8).
    디렉터리와 소스 파일만 포함하며, limit(최대 1000)개에서 중단한다.
    반환: {ok, path, total, items[{path, kind, size}]}.
    """
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
    """fnmatch 글롭 패턴으로 소스 파일을 찾는다.

    "Source/" 접두사는 있어도 없어도 동작하도록 두 형태 모두에 패턴을 대본다.
    반환: {ok, pattern, total, matches[{path, kind, size}]} (limit 최대 1000).
    """
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
    """grep_source의 path_glob 필터. 빈 패턴은 전체 허용.

    구분자/와일드카드 없이 파일명만 주면 "**/이름"으로 확장해 어느 깊이든 매칭되게 한다.
    """
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
    """소스 전체에서 텍스트를 검색한다. (grep에 해당)

    pattern: 부분 문자열(기본) 또는 regex=True 시 정규식. case_sensitive로 대소문자 구분.
    path_glob: 검색 대상 파일 필터. context: 매치 줄 앞뒤로 함께 보여줄 줄 수(0~8).
    각 매치는 줄 번호가 붙은 snippet(최대 1200자)을 포함하며, limit(최대 500)에서 즉시 중단한다.
    """
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


def read_source(path: str, *, start_line: Optional[int] = None, end_line: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """소스를 읽는다. (/source/read, 에이전트 source_read 도구) 경로 형식이 두 가지다:

    1. ".runtime/methods_index.json#Qualified.Symbol" — 인덱스에서 해당 심볼의
       선언/문서/시그니처 payload를 반환 (파일을 읽지 않음)
    2. "Source/디렉터리/파일.h" — 실제 파일의 지정 구간을 줄 번호를 붙여 반환.
       start_line 생략 시 앞 120줄, 최대 180줄/6000자로 제한.
       응답의 context 필드에는 구간 앞쪽의 namespace/타입 선언 요약이 들어가
       발췌만 보고도 어느 클래스 안의 코드인지 알 수 있다.

    경로가 없거나 소스 루트를 벗어나면 None을 반환한다. (라우터가 NOT_FOUND로 변환)
    """
    path_value = _to_text(path)
    # 형식 1: 인덱스 심볼 경로 ("#" 뒤가 qualified symbol)
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

    # 형식 2: 실제 파일 구간 읽기
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
    """단순 통합 검색. (/source/search 전용 — 에이전트는 더 풍부한 find_source를 쓴다)

    kind에 따라 동작이 갈린다:
      - "method"/"symbol"     : 심볼 검색만
      - "file"/"source_file"  : 파일명 글롭만 (query를 글롭 패턴으로 해석)
      - 그 외(기본)           : 심볼 검색 절반 + grep 매치 절반을 섞어 반환
    """
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


# ==========================================================================
#  3.  원본 파싱 — 인덱스 빌드/로드 · 헤더 → 타입 · 시그니처 · enum
# ==========================================================================

def _build_source_manifest(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """소스 트리를 한 번 훑어 모듈(최상위 디렉터리)별 파일 통계 manifest를 만든다.

    각 모듈의 전체/헤더/구현 파일 수와 인덱스의 메서드 수, 생성 시각을 담는다.
    get_context가 이 manifest를 읽어 에이전트에게 작업공간 개요를 제공한다.
    """
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
    """메서드 인덱스와 manifest를 처음부터 다시 생성해 디스크에 저장한다.

    인덱스 수명주기의 시작점: rebuild_index → load_methods_index(mtime 캐시) → get_context(요약).
    methods_index.py의 파서로 records를 만들고 두 JSON 파일을 기록한 뒤
    _INDEX_CACHE를 새 내용으로 즉시 채워 재로드 비용을 없앤다. 결과로 경로/건수 요약을 반환한다.
    """
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
    """메서드 인덱스 레코드 목록을 반환한다. (모든 심볼 검색의 데이터 원천)

    파일이 없으면 rebuild_index()로 만들고, 파일 mtime이 _INDEX_CACHE에 저장된
    mtime과 같으면 디스크를 건너뛰고 캐시 사본을 돌려준다. dict가 아닌 항목은 걸러낸다.
    """
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
    """manifest를 요약해 작업공간 컨텍스트(루트 경로, 파일/메서드 수, 모듈 목록)를 반환한다.

    manifest가 없으면 rebuild_index()로 생성한 뒤 다시 읽는다.
    에이전트가 세션 시작 시 소스 구조를 파악하는 용도로 쓰인다.
    """
    manifest = _load_json_file(source_manifest_file(), {})
    if not manifest:
        rebuild_index()
        manifest = _load_json_file(source_manifest_file(), {})
    modules = _as_list(manifest, "modules")
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


def _declaration_type_tokens(declaration: str) -> List[str]:
    """선언 문자열에서 SDK 고유 타입으로 보이는 식별자들만 추출한다. (최대 16개)

    기본 타입(int, bool 등)과 C++/CLI 키워드(property, cli, ref 등)는 제외해
    "이 멤버가 어떤 타입들과 연결되는가"를 타입 그래프 연결 판단에 쓴다.
    """
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
    """파라미터 목록 문자열을 쉼표로 분할하되, 괄호/제네릭(<>, [], ()) 안의 쉼표는 무시한다.

    예: "cli::array<int, 2>^ a, int b" → ["cli::array<int, 2>^ a", "int b"].
    """
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
    """C++/CLI 타입 표기를 C# 타입 표기로 변환한다.

    사용자는 C# 바인딩으로 SDK를 쓰므로 모델에게 C# 형태를 보여줘야 한다.
    규칙: 어트리뷰트([...]) 제거, `cli::array<T>^` → `T[]`(재귀), `String^` → string,
    Boolean → bool, Int32 → int, 핸들(^)·추적 참조(%) 제거, `네임스페이스::` 한정자 제거.
    빈 결과는 "void"로 간주한다.
    """
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
    """C++/CLI 파라미터 하나를 C# 파라미터 표기로 변환한다.

    [OutAttribute]가 붙으면 `out`, 추적 참조(%)만 있으면 `ref` 방향 한정자를 붙이고
    타입은 _csharp_type으로 변환한다. "타입 이름" 형태가 아니면 타입만 반환한다.
    """
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
    """C++/CLI 멤버 선언 전체를 C# 시그니처 문자열로 변환한다.

    - `property T Name {...}` → "T Name { get; set; }"
    - 메서드 → "반환타입 이름(파라미터, ...)" (각 부분은 _csharp_type/_csharp_parameter로 변환)
    - 둘 다 아니면 타입 변환 결과만 반환한다.
    """
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


def _simple_csharp_type_name(type_text: Any) -> str:
    """C# 타입 표기에서 SDK 고유 타입 이름 하나만 골라낸다.

    ref/out 한정자와 배열 표기를 벗긴 뒤, 기본 타입이 아닌 마지막 식별자를 반환한다.
    (제네릭 표기에서 가장 안쪽 타입이 잡히도록 뒤에서부터 본다.) 없으면 빈 문자열.
    """
    text = _to_text(type_text)
    text = re.sub(r"\b(ref|out|in|params)\b", " ", text)
    text = text.replace("[]", " ")
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text)
    for token in reversed(tokens):
        if token not in _CS_PRIMITIVE_TYPES:
            return token
    return ""


def _csharp_signature_shape(signature: Any) -> Dict[str, Any]:
    """C# 시그니처 문자열을 구조화한 "모양(shape)"으로 분해한다.

    반환 dict: member_name, return_type(원문)/return_type_name(고유 타입 이름),
    parameter_types(원문 목록), parameter_type_names(고유 타입 이름 목록),
    ref_parameter_type_names / out_parameter_type_names(방향 한정자별 타입 이름).
    property는 파라미터 없는 형태로, 파싱 불가 텍스트는 타입만 채워 반환한다.
    타입 그래프의 returns/accepts 관계와 enum 보강이 모두 이 분해 결과를 사용한다.
    """
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
    """`enum class <이름>` 선언을 소스에서 찾아 리터럴 목록을 추출하고 _ENUM_CACHE에 캐싱한다.

    선언 줄 다음부터 최대 80줄까지 본문을 훑으며 "식별자 (= 값)?," 패턴을 모은다.
    enum 파라미터를 받는 API를 모델이 호출할 때 올바른 리터럴을 제시하기 위함이다.
    찾지 못해도 빈 목록을 캐싱해 재탐색을 막는다.
    """
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
            # 선언 직후부터 최대 80줄 안에서 닫는 중괄호가 나올 때까지 리터럴을 수집
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
    """상속 절(": public A, B^" 등)을 파싱해 베이스 타입 이름 목록을 만든다.

    접근 지정자/virtual 키워드, 핸들 기호(^,%), 네임스페이스 한정자를 제거한다.
    """
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
    """모든 헤더(.h)를 줄 단위 스테이트 머신으로 훑어 타입 선언 인덱스를 만든다. (_TYPE_CACHE 캐싱)

    메서드 인덱스와 별개로 class/struct/interface/enum 선언 자체를 수집하는 이유는
    타입 그래프(상속, assignability)에 타입 단위 정보가 필요하기 때문이다.
    각 레코드: qualified_type(네임스페이스 경로 포함), type_name, kind, declaration,
    bases(상속 목록), source_ref(선언 위치), summary(직전 /// 문서주석 요약).

    스테이트 머신이 추적하는 상태:
      - in_block_comment: /* ... */ 블록 주석 내부 여부 (주석 안의 코드 무시)
      - pending_summary: 직전까지 연속된 /// 줄 (타입 선언을 만나면 summary로 소비)
      - pending_namespaces / namespace_stack: namespace 선언과 그것이 열리는 중괄호 깊이를
        짝지어 추적해, 타입 선언 시점의 정확한 네임스페이스 경로를 계산
      - brace_depth: 현재 중괄호 깊이
    """
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
            # 1단계: 블록 주석(/* */) 처리 — 주석 내부 텍스트는 분석에서 제외
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
            # 2단계: /// 문서주석은 다음 타입 선언의 summary 후보로 누적
            if stripped.startswith("///"):
                pending_summary.append(stripped)
                continue

            # 3단계: namespace 선언을 발견하면 대기열에 넣는다 (중괄호가 열릴 때 스택으로 이동)
            namespace_match = _NAMESPACE_DECL_RE.match(stripped)
            if namespace_match:
                pending_namespaces.append(str(namespace_match.group(1) or "").strip())

            # 4단계: 타입 선언 매칭 — 발견 시 현재 네임스페이스 경로로 한정한 레코드 생성
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
            # 타입 선언도 어트리뷰트([...])도 아닌 실질 코드 줄이 나오면 누적 중인 문서주석은 무효
            elif stripped and not stripped.startswith("["):
                pending_summary = []

            # 5단계: 중괄호 깊이 갱신 — '{'에서 대기 중인 namespace를 스택에 올리고,
            # '}'에서 해당 깊이보다 깊게 열린 namespace를 스택에서 내린다
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
    """타입 인덱스 레코드를 API 응답용 dict(필드 정제본)로 변환한다."""
    return {
        "qualified_type": _to_text(record.get("qualified_type")),
        "type_name": _to_text(record.get("type_name")),
        "kind": _to_text(record.get("kind")),
        "declaration": _to_text(record.get("declaration")),
        "bases": _as_list(record, "bases"),
        "source_ref": record.get("source_ref") if isinstance(record.get("source_ref"), dict) else {},
        "summary": _to_text(record.get("summary")),
    }


# ==========================================================================
#  4.  검색 — find_source · symbol · declaration · usages  (+ 토큰화/매칭/후보 헬퍼)
# ==========================================================================

def _method_payload(record: Dict[str, Any], *, include_doc: bool = False) -> Dict[str, Any]:
    """메서드 인덱스 레코드를 API 응답용 payload로 변환한다.

    C++/CLI 선언을 C# 시그니처로 변환해 붙이고(shape에서 반환/파라미터 타입 분해),
    "e"로 시작하는 enum 타입이 시그니처에 등장하면 enum_literals도 함께 담는다.
    include_doc=True면 owner 정보와 문서주석(doc, examples 제외)을 추가한다.
    path는 ".runtime/methods_index.json#Qualified.Symbol" 형태의 심볼 조회 경로다.
    """
    refs = [
        {
            "path": _to_text(item.get("path")),
            "line_range": _to_text(item.get("line_range")),
        }
        for item in (_as_list(record, "source_refs"))
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
    """레코드의 심볼/타입/멤버/선언을 모두 이어붙여 정규화한 매칭용 식별 문자열을 만든다."""
    return _normalized_token(
        "\n".join(
            [
                *(_to_text(record.get(key)) for key in ("qualified_symbol", "qualified_type", "type_name", "member_name", "declaration")),
            ]
        )
    )


def _query_word_tokens(query: str) -> List[str]:
    """질의 문장에서 단어 토큰을 추출한다.

    영문 식별자(점/해시 등으로 이어진 "Type.Member" 형태 포함), 숫자, 2자 이상의
    한글 단어를 등장 순서대로(중복 제거) 모은다. 모든 질의 토큰화의 기반 함수.
    """
    tokens: List[str] = []
    for item in re.findall(
        r"[A-Za-z_][A-Za-z0-9_]*(?:[.#:+][A-Za-z_][A-Za-z0-9_]*)*|\d+|[가-힣]{2,}",
        _to_text(query),
        flags=re.UNICODE,
    ):
        text = item.strip("_.+")
        if len(text) < 2 or not any(ch.isalnum() for ch in text):
            continue
        if text not in tokens:
            tokens.append(text)
    return tokens


def _is_ascii_identifier(value: str) -> bool:
    """값이 ASCII 식별자(영문/숫자/언더스코어, 숫자로 시작 안 함) 형태인지 판정한다."""
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", _to_text(value)))


def _query_identifier_tokens(query: str) -> List[str]:
    """자연어 질의 안에서 "코드 식별자로 보이는" 토큰만 골라낸다.

    일반 영단어와 구분하기 위해 토큰의 '모양'을 본다: 4자 이상이면서
    숫자 포함, CamelCase(대문자 2개 이상 + 소문자 혼재), 또는 약어(대문자 2개 이상)
    형태일 때만 식별자로 인정한다. 단 "Xxx API"처럼 API라는 단어가 뒤따르는
    이름은 모양과 무관하게 식별자 후보로 본다. "Type.Member" 토큰은 분해해서도 검사한다.
    find_source의 exact_identifier 매칭과 사용처 검색의 씨앗이 된다.
    """
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
    """질의의 단어 토큰을 CamelCase 분해 없이 통째로 정규화한 "1차 검색어" 목록을 만든다.

    _query_terms보다 강한 매칭(단어 전체 일치)에 쓰여 가중치가 높게 부여된다.
    """
    terms: List[str] = []
    for item in _query_word_tokens(query):
        token_key = _normalized_token(item)
        if len(token_key) > 1 and token_key not in terms:
            terms.append(token_key)
    return terms


def _query_terms(query: str) -> List[str]:
    """질의를 세분화한 검색어 목록을 만든다. (CamelCase 분해 포함)

    예: "GetPixelValue" → ["getpixelvalue", "get", "pixel", "value"].
    원형 토큰과 분해 조각을 모두 정규화해 넣어, 부분 일치 점수 계산의 기본 단위가 된다.
    """
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
    """메서드 레코드가 질의에 얼마나 잘 맞는지 정렬 키를 계산한다. (낮을수록 = 더 음수일수록 상위)

    가중치 의미:
      - 멤버 이름이 검색어와 완전히 같으면 항목당 -40 (가장 강한 신호)
      - 타입 이름이 검색어와 완전히 같으면 항목당 -20
      - 질의 전체가 식별 문자열에 통째로 포함되면(완전일치) -20
      - 검색어가 식별 문자열/요약에 부분 포함되면 항목당 -1
    아무 검색어도 맞지 않으면 None(매치 아님). symbol_search/declaration_search의 순위가 이것이다.
    반환 튜플 2번째 요소는 동점일 때 심볼 이름순 정렬을 위한 것이다.
    """
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


def symbol_search(query: str, *, limit: int = 20) -> Dict[str, Any]:
    """메서드 인덱스 전체를 _record_match_order 점수로 정렬해 상위 심볼을 반환한다.

    빈 질의면 전체를 심볼 이름순으로 나열한다. 결과 항목은 _method_payload 형식(문서주석 제외).
    """
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


def _line_range_bounds(value: Any, *, padding: int = 1) -> Tuple[Optional[int], Optional[int]]:
    """"12-34" 또는 "12" 형식의 줄 범위 문자열을 (시작, 끝) 정수로 파싱한다.

    앞뒤로 padding 줄을 넓혀(기본 1) 선언 주변 맥락이 함께 읽히게 한다. 파싱 실패 시 (None, None).
    """
    match = re.match(r"\s*(\d+)(?:\s*-\s*(\d+))?", _to_text(value))
    if not match:
        return None, None
    start = max(1, int(match.group(1)) - padding)
    end = int(match.group(2) or match.group(1)) + padding
    return start, max(start, end)


def _read_targets_for_method(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """메서드 payload로부터 "다음에 읽을 위치(read_targets)" 목록을 만든다.

    심볼 조회 경로(kind=symbol) 1건과, source_refs 각각을 줄 범위가 보정된
    source_span 타깃으로 변환해 담는다. 에이전트의 후속 read_source 호출을 안내한다.
    """
    targets: List[Dict[str, Any]] = []
    symbol_path = _to_text(payload.get("path"))
    if symbol_path:
        targets.append({"kind": "symbol", "path": symbol_path})
    for ref in _as_list(payload, "source_refs"):
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
    """메서드 레코드를 find_source의 후보(candidate) dict로 변환한다.

    reason은 이 후보가 어떤 수집 경로(exact_identifier, declaration, graph_path 등)로
    들어왔는지의 태그로, _candidate_reason_rank를 통해 출력 순위를 결정한다.
    C# 시그니처/ref·out 파라미터 타입/enum 리터럴/read_targets까지 미리 채워 둔다.
    """
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
    """후보 dict에서 최종 응답에 내보낼 필드만 추린다. (read_targets/source_refs 등 내부용 제외)"""
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
    """후보 수집 경로(reason) 태그의 우선순위를 정의한다. (숫자가 작을수록 상위)

    exact_identifier(질의의 식별자와 멤버명 완전 일치) > declaration(선언 검색)
    > graph_path/graph_operation(타입 그래프 경로/연산) > type_member(질의 타입의 멤버)
    > owner_constructor(후보 소유 타입의 생성자) > related_type_operation(관련 타입을 다루는 연산)
    > constructor > graph_declaration > symbol(일반 심볼 검색). 미정의 태그는 20.
    """
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
    """find_source 출력에서 후보의 최종 정렬 키를 만든다.

    1순위: reason 태그 순위, 2순위: 후보 타입명이 질의에 포함되는가(0이 우선),
    3순위: _member_order_for_graph 멤버 점수, 4순위: 심볼 이름순.
    """
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
    """생성자 후보 정렬 키: 소멸자/파이널라이저(~,!)는 뒤로, 파라미터 적고 시그니처 짧은 것 우선.

    타입마다 가장 단순한 생성자 하나를 대표로 골라 보여주기 위한 기준이다.
    """
    declaration = _to_text(record.get("declaration"))
    signature = _csharp_signature(declaration)
    shape = _csharp_signature_shape(signature)
    parameter_count = len(shape.get("parameter_type_names") or [])
    lifecycle = 1 if declaration.lstrip().startswith(("!", "~")) else 0
    return lifecycle, parameter_count, len(signature), _to_text(record.get("qualified_symbol"))


def _csharp_ref_constraints(candidates: Sequence[Dict[str, Any]], relations: Sequence[Any]) -> List[Dict[str, Any]]:
    """C#의 ref 파라미터 제약 안내를 만든다.

    C#에서 `ref Base` 파라미터에는 Derived 변수를 직접 넘길 수 없고
    Base 타입 변수를 선언한 뒤 거기에 파생 값을 담아 넘겨야 한다.
    후보들의 ref 파라미터 타입과 assignability 행렬(relations, [파생, 베이스] 행)을 대조해
    이런 상황을 찾아 호출 방법 노트(call_note)와 함께 반환한다. 모델의 잘못된 코드 생성 방지용.
    """
    candidate_types = {_to_text(candidate.get("type_name")) for candidate in candidates if _to_text(candidate.get("type_name"))}
    constraints: List[Dict[str, Any]] = []
    for candidate in candidates:
        for ref_type in _as_list(candidate, "ref_parameter_types"):
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
    """사용처 검색어 목록에 정규화 토큰을 중복 없이 추가한다. 4자 미만은 노이즈로 보고 버린다."""
    key = _normalized_token(value)
    if len(key) < 4 or key in seen:
        return
    seen.add(key)
    terms.append(key)


def _usage_terms_for_candidates(candidates: Sequence[Dict[str, Any]], query: str) -> List[str]:
    """사용처(usage) 창 검색에 쓸 검색어를 모은다. (최대 36개)

    질의의 코드 식별자 토큰 + 후보들의 멤버명/타입명/반환·파라미터 타입을 합친다.
    exact_identifier 후보가 있으면 그것만 씨앗으로 써서 정밀도를 높인다.
    """
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
        for parameter_type in _as_list(candidate, "parameter_types"):
            _append_usage_term(terms, seen, parameter_type)
    return terms[:36]


def _source_usage_spans_for_candidates(
    candidates: Sequence[Dict[str, Any]],
    query: str,
    *,
    limit: int,
) -> List[Dict[str, Any]]:
    """후보 API들이 실제로 함께 사용되는 코드 창(span)을 찾아 점수순으로 반환한다.

    "이 API를 실전에서 어떻게 조합해 쓰는가"를 보여주는 예제 코드를 발굴하는 함수다.
    검색어가 3개 이상 모이지 않으면(근거 부족) 빈 목록을 돌려준다.

    절차:
      1. 파일 전체에 검색어가 3개 이상 등장하는 파일만 후보로 남긴다 (정규화 줄 캐시 활용)
      2. 검색어가 등장하는 줄(anchor)마다 위 24줄/아래 40줄의 창을 만든다 (anchor 최대 80개)
      3. 창 점수 = (창 안에 등장한 검색어 수 × 10) + min(호출문처럼 보이는 줄 수, 12)
      4. 점수 내림차순으로 돌며 같은 파일에서 겹치는 창은 건너뛰고 limit개를 채운다
    """
    terms = _usage_terms_for_candidates(candidates, query)
    if len(terms) < 3:
        return []

    ranked_windows: List[Tuple[Tuple[int, int, str], Path, int, int, List[str]]] = []
    for path in _iter_source_files():
        lines = _read_lines(path)
        if not lines:
            continue
        normalized_lines = _read_normalized_lines(path)
        # 1단계: 파일 단위 사전 필터 — 검색어 3개 미만이면 창을 만들 필요도 없다
        file_key = "".join(normalized_lines)
        present_terms = [term for term in terms if term in file_key]
        if len(present_terms) < 3:
            continue
        # 2단계: 검색어(상위 16개)가 등장하는 줄을 anchor로 수집
        anchors = [
            idx
            for idx, line_key in enumerate(normalized_lines)
            if any(term in line_key for term in present_terms[:16])
        ]
        # 3단계: anchor 주변 ±24/40줄 창을 만들어 점수화
        for anchor in anchors[:80]:
            start = max(0, anchor - 24)
            end = min(len(lines), anchor + 40)
            window_key = "".join(normalized_lines[start:end])
            hits = [term for term in present_terms if term in window_key]
            if len(hits) < 3:
                continue
            # 괄호/세미콜론이 있는 줄을 "실제 호출 코드"로 간주해 가산점 (최대 12)
            code_lines = sum(1 for line in lines[start:end] if "(" in line and (")" in line or ";" in line))
            score = (len(hits) * 10) + min(code_lines, 12)
            # 정렬 키: 점수 높은 순 → 창 짧은 순 → 경로명 순
            ranked_windows.append(((-score, end - start, _source_path(path)), path, start, end, hits))

    # 4단계: 점수순으로 선별하되, 같은 파일에서 이미 고른 창과 겹치면 제외
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
    """find_source 응답의 source_spans(실제 코드 발췌)를 구성한다.

    우선 실사용 창(_source_usage_spans_for_candidates, 최대 3개)을 넣고,
    남은 자리는 각 후보의 첫 번째 source_span read_target을 read_source로 읽어 채운다.
    (path, 줄 범위) 기준으로 중복을 제거하고 본문은 1600자로 절단한다.
    """
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
        candidate_targets = _as_list(candidate, "read_targets")
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


def _read_target_identity(target: Dict[str, Any]) -> str:
    """read_target의 중복 판정 키(kind/path/줄 범위를 직렬화한 JSON)를 만든다."""
    payload = {
        "kind": _to_text(target.get("kind")),
        "path": _to_text(target.get("path")),
        "start_line": target.get("start_line"),
        "end_line": target.get("end_line"),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _compact_read_target(target: Dict[str, Any]) -> Dict[str, Any]:
    """dict에서 빈 값("", [], {}, None) 필드를 제거해 응답 크기를 줄인다."""
    return {key: value for key, value in target.items() if value not in ("", [], {}, None)}


def _source_span_read_target(span: Dict[str, Any]) -> Dict[str, Any]:
    """source_spans 항목을 read_target 형식(kind=source_span, 줄 범위 포함)으로 변환한다."""
    path = _to_text(span.get("path"))
    if not path:
        return {}
    target: Dict[str, Any] = {
        "kind": "source_span",
        "path": path,
        "source": "source_spans",
        "symbol": _to_text(span.get("symbol")),
        "csharp_signature": _to_text(span.get("csharp_signature")),
    }
    start_line, end_line = _line_range_bounds(span.get("line_range"), padding=0)
    if start_line is not None and end_line is not None:
        target.update({"start_line": start_line, "end_line": end_line})
    return _compact_read_target(target)


def _read_target_score(target: Dict[str, Any], query: str, order: int) -> Tuple[int, int, int, int, int, str]:
    """read_target 정렬 키를 계산한다. (낮을수록 우선)

    우선순위: 질의 검색어 적중 수(많을수록) → 1차 검색어 적중 수 →
    kind가 source_span인 것(실제 코드 위치) 우선 → 원래 삽입 순서 → 경로 길이/이름순.
    """
    text = _normalized_token(json.dumps(target, ensure_ascii=False, sort_keys=True))
    term_hits = sum(1 for term in _query_terms(query) if term and term in text)
    primary_hits = sum(1 for term in _query_primary_terms(query) if term and term in text)
    kind_rank = 0 if _to_text(target.get("kind")) == "source_span" else 1
    path = _to_text(target.get("path"))
    return (-term_hits, -primary_hits, kind_rank, order, len(path), path)


def _ranked_read_targets(
    candidates: Sequence[Dict[str, Any]],
    *,
    source_spans: Sequence[Dict[str, Any]],
    query: str,
    limit: int,
) -> List[Dict[str, Any]]:
    """source_spans와 모든 후보의 read_targets를 합쳐 점수순 상위 limit개의 추천 읽기 목록을 만든다.

    span 유래 타깃을 먼저 넣고, 후보 유래 타깃은 심볼/시그니처/reason을 보강해 넣은 뒤
    _read_target_score로 정렬한다. find_source의 read_targets/recommended_reads가 이 결과다.
    """
    entries: List[Tuple[Tuple[int, int, int, int, int, str], Dict[str, Any]]] = []
    seen = set()

    def append_target(target: Dict[str, Any], order: int) -> None:
        """타깃을 빈 값 제거 후 중복 검사하여 점수와 함께 수집한다."""
        compact = _compact_read_target(target)
        if not _to_text(compact.get("path")):
            return
        key = _read_target_identity(compact)
        if key in seen:
            return
        seen.add(key)
        entries.append((_read_target_score(compact, query, order), compact))

    for index, span in enumerate(source_spans):
        if isinstance(span, dict):
            append_target(_source_span_read_target(span), index)
    base_order = len(entries)
    for candidate_index, candidate in enumerate(candidates):
        candidate_targets = _as_list(candidate, "read_targets")
        for target_index, target in enumerate(candidate_targets):
            if not isinstance(target, dict):
                continue
            enriched = {
                **target,
                "source": target.get("source") or "candidate_refs",
                "symbol": target.get("symbol") or candidate.get("symbol"),
                "csharp_signature": target.get("csharp_signature") or candidate.get("csharp_signature"),
                "reason": target.get("reason") or candidate.get("reason"),
            }
            append_target(enriched, base_order + candidate_index * 4 + target_index)
    return [target for _, target in sorted(entries, key=lambda item: item[0])[:limit]]


def _leading_doc_summary(lines: Sequence[str], line_index: int) -> str:
    """선언 줄 바로 위에 연속으로 붙은 "///" 문서주석을 거슬러 올라가 모아 요약으로 만든다."""
    docs: List[str] = []
    idx = line_index - 1
    while idx >= 0:
        stripped = lines[idx].strip()
        if not stripped.startswith("///"):
            break
        docs.insert(0, stripped)
        idx -= 1
    return _clean_doc_summary(docs)


def _event_declarations_for_types(types: Sequence[Dict[str, Any]], *, limit: int) -> List[Dict[str, Any]]:
    """주어진 타입들의 헤더 파일에서 event/delegate 선언을 찾아낸다.

    이벤트는 메서드 인덱스에 잘 잡히지 않으므로 헤더를 직접 줄 단위로 훑는다.
    event는 현재 추적 중인 클래스가 대상 타입일 때만, delegate는 선언 텍스트에
    대상 타입 이름이 포함될 때만 채택한다. 각 항목에 선언 위치와 /// 요약을 붙여
    event 우선·타입명·경로 순으로 정렬 후 limit개를 반환한다.
    """
    paths: List[str] = []
    type_names = {
        _to_text(item.get("type_name"))
        for item in types
        if isinstance(item, dict) and _to_text(item.get("type_name"))
    }
    type_keys = {_normalized_token(type_name) for type_name in type_names if _normalized_token(type_name)}
    for item in types:
        if not isinstance(item, dict):
            continue
        ref = item.get("source_ref") if isinstance(item.get("source_ref"), dict) else {}
        path = _to_text(ref.get("path"))
        if path and path not in paths:
            paths.append(path)

    declarations: List[Dict[str, Any]] = []
    seen = set()
    for source_path in paths:
        path = _source_file_for_path(source_path)
        if not path or not path.exists() or not path.is_file():
            continue
        lines = _read_lines(path)
        current_type = ""
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("///"):
                continue
            type_match = re.search(r"\b(?:ref\s+)?class\s+([A-Za-z_][A-Za-z0-9_]*)\b", stripped)
            if type_match:
                current_type = type_match.group(1)
            event_match = re.search(r"\bevent\s+(.+?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*;", stripped)
            delegate_match = re.search(r"\bdelegate\s+(.+?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", stripped)
            match = event_match or delegate_match
            if not match:
                continue
            declaration = re.sub(r"\s+", " ", stripped).strip()
            declaration_key = _normalized_token(declaration)
            if event_match and current_type not in type_names:
                continue
            if delegate_match and not any(type_key and type_key in declaration_key for type_key in type_keys):
                continue
            name = match.group(2)
            key = (source_path, idx + 1, name, declaration)
            if key in seen:
                continue
            seen.add(key)
            item = {
                "type_name": current_type if current_type in type_names else "",
                "kind": "event" if event_match else "delegate",
                "name": name,
                "declaration": declaration,
                "summary": _leading_doc_summary(lines, idx),
                "path": _source_path(path),
                "line_range": f"{idx + 1}-{idx + 1}",
            }
            declarations.append(_compact_read_target(item))
    declarations.sort(
        key=lambda item: (
            0 if _to_text(item.get("kind")) == "event" else 1,
            _to_text(item.get("type_name")),
            _to_text(item.get("path")),
            _to_text(item.get("line_range")),
        )
    )
    return declarations[:limit]


def _type_family_key(value: Any) -> str:
    """타입 이름의 "가족(family)" 키를 만든다. 같은 접두 계열의 타입을 묶기 위함.

    CamelCase 첫 조각(첫 조각이 3자 이하 접두어면 두 조각)을 정규화해 반환한다.
    예: "NXImage", "NXImageView" → "nximage" 계열로 묶일 수 있다.
    """
    name = _to_text(value)
    parts = re.findall(r"[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z]+|\d+", name)
    if not parts:
        return _normalized_token(name)
    if len(parts[0]) <= 3 and len(parts) > 1:
        return _normalized_token("".join(parts[:2]))
    return _normalized_token(parts[0])


def _event_types_for_candidates(
    candidates: Sequence[Dict[str, Any]],
    type_relations: Sequence[Any],
    *,
    limit: int,
) -> List[Dict[str, Any]]:
    """후보들과 관련된 타입(이벤트 선언 탐색 대상)을 골라낸다.

    후보의 소유 타입/반환 타입/파라미터 타입을 씨앗으로 삼고, assignability 관계로
    이어진 타입 중 같은 가족(_type_family_key)인 것까지 확장한 뒤 씨앗 순서대로 정렬한다.
    결과는 _event_declarations_for_types의 입력이 된다.
    """
    type_records = _load_type_index()
    by_name = {
        _to_text(record.get("type_name")): record
        for record in type_records
        if _to_text(record.get("type_name"))
    }
    seed_order: Dict[str, int] = {}

    def add_type_name(value: Any, order: int) -> None:
        """타입 인덱스에 존재하는 이름이면 발견 순서(order)와 함께 씨앗으로 등록한다."""
        type_name = _to_text(value)
        if type_name in by_name and type_name not in seed_order:
            seed_order[type_name] = order

    for candidate_index, candidate in enumerate(candidates[:limit]):
        base_order = candidate_index * 10
        add_type_name(candidate.get("type_name"), base_order)
        add_type_name(candidate.get("return_type"), base_order + 1)
        parameter_types = _as_list(candidate, "parameter_types")
        for parameter_index, type_name in enumerate(parameter_types):
            add_type_name(type_name, base_order + 2 + parameter_index)

    seeds = set(seed_order)
    expanded = set(seeds)
    expanded_order = dict(seed_order)
    for relation in type_relations:
        if not isinstance(relation, (list, tuple)) or len(relation) < 2:
            continue
        source_type = _to_text(relation[0])
        target_type = _to_text(relation[1])
        if source_type in seeds and target_type in by_name:
            if _type_family_key(source_type) == _type_family_key(target_type):
                expanded.add(target_type)
                expanded_order.setdefault(target_type, seed_order[source_type] + 1)
        if target_type in seeds and source_type in by_name:
            if _type_family_key(source_type) == _type_family_key(target_type):
                expanded.add(source_type)
                expanded_order.setdefault(source_type, seed_order[target_type] + 1)

    ordered = [by_name[type_name] for type_name in expanded if type_name in by_name]
    ordered.sort(key=lambda record: (expanded_order.get(_to_text(record.get("type_name")), 9999), _to_text(record.get("type_name"))))
    return [_type_payload(record) for record in ordered[: max(limit, 1)]]


def _record_by_symbol() -> Dict[str, Dict[str, Any]]:
    """qualified_symbol → 메서드 레코드 매핑을 만든다. (find_source의 빠른 역참조용)"""
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
    """C# 시그니처(+선택적으로 멤버명/소유 타입명)로 메서드 레코드를 역으로 찾는다.

    타입 그래프 결과는 시그니처 문자열만 담고 있으므로, 후보로 승격하려면
    원본 레코드를 이 함수로 되찾아야 한다. 일치하는 첫 레코드를 반환한다.
    """
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
    """질의가 특정 심볼(타입명+멤버명 모두 포함)을 직접 지목하는지 판정한다.

    True면 find_source가 선언 검색 결과를 그래프보다 먼저 채택한다.
    """
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
    """통합 소스 검색 — 에이전트의 source_search 도구 본체이자 이 파일에서 가장 큰 오케스트레이터.

    하나의 자연어/API 질의에 대해 여러 수집 경로를 순차 실행해 후보(candidate)를 모은다.
    각 후보에는 어떤 경로로 발견됐는지 reason 태그가 붙고,
    _candidate_reason_rank가 정의한 우선순위(exact_identifier > declaration > graph_* > ... > symbol)로 정렬된다.

    수집 단계:
      1. 정확한 식별자 일치 (append_exact_identifier_declarations)
      2. 선언 검색 + 타입 그래프 (질의가 심볼 직접 지목이면 선언 우선, 아니면 그래프 우선)
      3. 질의에 등장한 타입의 전체 멤버 (append_direct_type_members)
      4. symbol_search 결과 보강
      5. 후보들의 소유/관련 타입 생성자 보강 (append_constructors_for)
      6. 관련 타입을 주고받는 연산 보강 (related_type_operation)
      7. 파일명 글롭 매치 (file_candidates)

    반환 dict에는 후보 외에도 에이전트가 바로 쓸 수 있는 부가 정보를 묶는다:
      - source_spans: 후보 API들이 실제로 쓰인 코드 발췌
      - read_targets/recommended_reads: 다음에 source_read로 읽을 위치 추천
      - type_relations(assignability) / csharp_ref_constraints: ref 파라미터 호출 제약
      - event_declarations: 관련 타입의 이벤트/델리게이트 선언
    """
    normalized_query = _to_text(query)
    safe_limit = _safe_limit(limit, default=12, high=40)
    records = load_methods_index()
    by_symbol = _record_by_symbol()
    candidates: List[Dict[str, Any]] = []
    type_members: List[Dict[str, Any]] = []
    seen_candidates = set()

    def append_record(record: Optional[Dict[str, Any]], reason: str) -> None:
        """메서드 레코드를 후보로 추가한다. 소멸자/파이널라이저 제외, (심볼, 시그니처) 중복 제거."""
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
        """declaration_search 결과 항목(payload)을 원본 레코드로 되찾아 후보로 추가한다."""
        symbol = _to_text(item.get("symbol"))
        member_name = symbol.rsplit(".", 1)[-1]
        record = _find_record_by_signature(
            records,
            signature=_to_text(item.get("csharp_signature")),
            member_name=member_name,
        )
        append_record(record or by_symbol.get(symbol), reason)

    # 두 가지 주 검색을 먼저 수행해 두고, 아래 append_* 함수들이 결과를 소비한다.
    declaration_results = declaration_search(normalized_query, limit=safe_limit).get("results", [])
    graph = type_graph(normalized_query, limit=max(8, min(16, safe_limit)))

    def append_declarations() -> None:
        """선언 검색 상위 결과 전체를 reason="declaration"으로 후보에 추가한다."""
        for item in declaration_results:
            append_declaration_item(item, "declaration")

    def append_exact_identifier_declarations() -> None:
        """질의 속 코드 식별자 토큰과 멤버명이 '정확히' 일치하는 레코드를 최우선 후보로 추가한다.

        예: 질의에 `GetLayerCount`가 있으면 멤버명이 정규화 기준으로 동일한 메서드를
        reason="exact_identifier"(최상위 순위)로 넣는다.
        같은 이름이 여러 타입에 있으면 질의에 타입명이 포함된 쪽을 먼저 채택한다.
        """
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
        """타입 그래프 결과(경로 스텝 → 연산 → 선언 순)에 등장한 메서드를 후보로 추가한다.

        그래프 출력은 행(row) 배열로 압축돼 있어 시그니처/멤버명으로
        _find_record_by_signature를 통해 원본 레코드를 역추적한다.
        """
        for path in _as_list(graph, "paths"):
            steps = path[2] if isinstance(path, list) and len(path) >= 3 and isinstance(path[2], list) else []
            for step in steps:
                if isinstance(step, list) and len(step) >= 5:
                    append_record(
                        _find_record_by_signature(records, signature=_to_text(step[4]), member_name=_to_text(step[3])),
                        "graph_path",
                    )
        for row in _as_list(graph, "operations"):
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
        for row in _as_list(graph, "declarations"):
            if isinstance(row, list) and row:
                record = _find_record_by_signature(
                    records,
                    signature=_to_text(row[1]) if len(row) > 1 else "",
                    member_name=_to_text(row[0]).rsplit(".", 1)[-1],
                )
                append_record(record or by_symbol.get(_to_text(row[0])), "graph_declaration")

    def append_direct_type_members() -> None:
        """질의가 특정 타입을 가리키면 그 타입의 멤버 전체를 점수순으로 후보에 추가한다.

        "NXScene에 어떤 메서드가 있나" 류의 질문에 대비해, 타입명이 질의에 포함되거나
        식별자 토큰과 겹치는 타입의 멤버를 type_members 목록에도 별도로 담는다.
        """
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

    # ---- 후보 수집 시작 ----
    # 정확한 식별자 일치를 항상 가장 먼저 넣고,
    # 질의가 "타입.멤버"를 직접 지목하는 형태면 선언 검색을, 아니면 그래프 탐색을 우선한다.
    # (append_record가 중복을 제거하므로 순서 = 우선순위가 된다)
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

    # 마지막 안전망: 일반 심볼 검색 결과도 reason="symbol"(최하위 순위)로 보탠다.
    for item in symbol_search(normalized_query, limit=safe_limit * 2).get("results", []):
        append_record(by_symbol.get(_to_text(item.get("symbol"))), "symbol")

    # ---- 관련 타입 보강 ----
    # related_type_names: 후보의 소유 타입 + 반환/파라미터 타입까지 (객체 생성·전달에 필요한 타입들)
    # owner_type_names: 후보를 소유한 타입만
    related_type_names = {
        _to_text(candidate.get("type_name"))
        for candidate in candidates
        if _to_text(candidate.get("type_name"))
    }
    for candidate in list(candidates):
        parameter_types = _as_list(candidate, "parameter_types")
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
        """주어진 타입들의 생성자를 타입당 1개씩 후보에 추가한다.

        모델이 예제 코드를 쓸 때 "이 타입을 어떻게 만드는지"가 항상 필요하기 때문.
        _constructor_record_order 순서상 파라미터가 적은(만들기 쉬운) 생성자가 선택된다.
        """
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
    # 관련 타입을 반환하거나 파라미터로 받는 다른 연산들도 추가한다.
    # (예: 후보가 NXLayer를 다루면 NXLayer를 만들거나 소비하는 메서드들까지)
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

    # ---- 파일 후보 수집 ----
    # 심볼 후보가 참조하는 파일 + 질의 식별자가 파일명에 들어간 파일.
    file_candidates: List[Dict[str, Any]] = []
    seen_files = set()

    def append_file(path: str, reason: str, source: str = "") -> None:
        """파일 경로를 중복 없이 file_candidates에 추가한다. source는 발견 근거(심볼/토큰)."""
        normalized_path = _to_text(path)
        if not normalized_path or normalized_path in seen_files:
            return
        seen_files.add(normalized_path)
        file_candidates.append({"kind": "source_file", "reason": reason, "path": normalized_path, "source": source})

    for candidate in candidates:
        for ref in _as_list(candidate, "source_refs"):
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

    # ---- 최종 출력 조립 ----
    # 후보를 reason 순위 + 질의 적합도로 정렬해 상위만 남기고,
    # 그 후보들을 근거로 부가 정보(코드 발췌, 읽기 추천, 이벤트, ref 제약)를 만든다.
    output_candidate_limit = max(40, safe_limit * 3)
    output_type_member_limit = max(32, safe_limit * 2)
    output_candidates = sorted(candidates, key=lambda item: _candidate_output_order(item, normalized_query))[:output_candidate_limit]
    source_spans = _source_spans_for_candidates(output_candidates, query=normalized_query, limit=min(12, safe_limit))
    read_targets = _ranked_read_targets(
        output_candidates,
        source_spans=source_spans,
        query=normalized_query,
        limit=max(16, safe_limit),
    )
    type_relations = graph.get("assignability", [])[:32]
    event_types = _event_types_for_candidates(
        output_candidates,
        type_relations,
        limit=max(12, safe_limit),
    )
    event_declarations = _event_declarations_for_types(event_types, limit=min(12, safe_limit))
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
        "event_declarations": event_declarations,
        "type_members": [_candidate_for_output(item) for item in type_members[:output_type_member_limit]],
        "candidates": [_candidate_for_output(item) for item in output_candidates],
        "files": file_candidates[: min(8, safe_limit)],
        "recommended_reads": read_targets[: min(8, safe_limit)],
        "read_targets": read_targets,
        "source_spans": source_spans,
    }


def source_usages(query: str, *, limit: int = 12) -> Dict[str, Any]:
    """타입/메서드의 "실제 사용처"를 찾는다. (/source/usages, 에이전트 source_usages 도구)

    grep과 달리 주석 줄(///, //, *)을 건너뛰고,
    한 줄 안에 검색어(상위 4개)가 전부 등장해야 매치로 친다.
    — 단순 언급이 아니라 실제 호출/사용 코드를 찾기 위한 조건.
    매치 줄 앞뒤 2줄을 스니펫으로 함께 반환한다.
    """
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
    """선언 검색: symbol_search와 같은 점수 방식이지만, 결과에 더 풍부한 정보를 붙인다.

    각 결과 payload에 문서주석(doc), 선언에 등장하는 SDK 타입 목록(types),
    'e'로 시작하는 enum 타입의 리터럴 목록(enum_literals)까지 포함한다.
    type_graph와 find_source가 내부적으로 사용한다.
    """
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


# ==========================================================================
#  5.  그래프 탐색 — type_graph · BFS · 간선/연산 · 출력 압축
# ==========================================================================

def _type_graph_type_row(type_item: Dict[str, Any]) -> List[Any]:
    """타입 dict를 _TYPE_GRAPH_SCHEMAS["types"] 열 순서의 행 배열로 압축한다."""
    return [
        type_item.get("type_name") or "",
        type_item.get("qualified_type") or "",
        _as_list(type_item, "bases"),
    ]


def _type_graph_declaration_row(declaration: Dict[str, Any]) -> List[Any]:
    """선언 payload를 _TYPE_GRAPH_SCHEMAS["declarations"] 열 순서의 행 배열로 압축한다."""
    doc = declaration.get("doc") if isinstance(declaration.get("doc"), dict) else {}
    return [
        declaration.get("symbol") or "",
        declaration.get("csharp_signature") or "",
        doc.get("summary") or "",
        declaration.get("enum_literals") or {},
        declaration.get("types") or [],
    ]


def _type_graph_assignability_row(item: Dict[str, Any]) -> List[str]:
    """assignability(파생→베이스 대입 가능) 관계를 [from, to] 행으로 압축한다."""
    return [_to_text(item.get("from")), _to_text(item.get("to"))]


def _type_graph_operation_row(operation: Dict[str, Any]) -> List[Any]:
    """연산(operation) dict를 _TYPE_GRAPH_SCHEMAS["operations"] 열 순서의 행 배열로 압축한다."""
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
    """경로 dict를 [from, to, steps] 행으로 압축한다. steps의 각 항목은 path_steps 스키마를 따른다."""
    steps = []
    for step in _as_list(path, "steps"):
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
    """출력에 포함할 연산을 선별한다: 점수 상위 limit개 + 경로(paths)에 등장한 연산은 무조건 포함.

    경로 스텝에 나오는 연산이 빠지면 모델이 경로를 따라갈 수 없으므로 보존이 필수다.
    (member_name, csharp_signature) 쌍으로 중복을 제거한다.
    """
    path_keys = set()
    for path in paths:
        for step in _as_list(path, "steps"):
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
    """payload를 최소 구분자 JSON으로 직렬화했을 때의 문자 수를 잰다. (예산 축소 판단용)"""
    return len(json_for_model(payload))


def _path_operation_signatures(path_rows: Sequence[List[Any]]) -> set:
    """행 형식으로 압축된 경로들에서 스텝에 등장하는 C# 시그니처 집합을 수집한다."""
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
    """연산 행(row)에서 C# 시그니처 열(인덱스 3)을 꺼낸다. 형식이 다르면 빈 문자열."""
    if isinstance(row, list) and len(row) >= 4:
        return _to_text(row[3])
    return ""


def _select_operation_rows(
    rows: Sequence[List[Any]],
    path_rows: Sequence[List[Any]],
    *,
    limit: int,
) -> List[List[Any]]:
    """행 형식 연산 목록을 limit개로 줄이되, 경로에 등장하는 시그니처의 행은 한도와 무관하게 유지한다.

    _type_graph_output_operations와 같은 원칙을 "이미 행으로 압축된" 데이터에 적용한 버전으로,
    _fit_type_graph_payload의 축소 단계에서 사용된다.
    """
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
    """type_graph 결과를 TYPE_GRAPH_RESULT_CHARS(15000자) 예산 안으로 단계적으로 축소한다.

    이미 예산 이내면 그대로 반환. 초과 시 budgets의 각 단계
    (declarations, types, operations, paths, assignability 한도)를 큰 것부터 작은 것 순으로
    적용해 보고, 처음으로 예산을 만족하는 후보를 반환한다.
    마지막 단계까지도 초과하면 operations를 한 행씩 뒤에서 잘라내며 강제로 맞춘다.
    """
    if _json_chars(payload) <= TYPE_GRAPH_RESULT_CHARS:
        return payload

    # 축소 단계표: (declarations, types, operations, paths, assignability) 최대 개수.
    # 위에서 아래로 갈수록 더 공격적으로 줄인다.
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
        path_rows = _as_list(payload, "paths")[:path_limit]
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

    # 모든 단계가 실패한 경우: operations를 한 행씩 제거하며 예산을 맞춘다 (최소 1개는 남김)
    while _json_chars(best) > TYPE_GRAPH_RESULT_CHARS and len(best.get("operations") or []) > 1:
        best = {**best, "operations": best["operations"][:-1]}
    return best


def _type_order(record: Dict[str, Any], query: str, connected_types: Optional[Sequence[str]] = None) -> Optional[Tuple[int, str]]:
    """타입 레코드가 질의에 얼마나 적합한지 정렬 키를 계산한다. (낮을수록 상위, None이면 매치 안 됨)

    가중치: 연결 타입 정확 일치 25점, 질의 전체 문자열 포함 20점, 타입명 부분 일치 10점,
    검색어/연결 타입 히트당 1점. type_graph가 그래프에 넣을 타입을 고를 때 쓴다.

    connected_types: declaration_search에서 미리 뽑은 "질의와 연결된 타입 이름들" —
    질의 단어와 직접 안 겹쳐도 관련 타입이면 끌어올리기 위한 보조 신호.
    """
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
                " ".join(_to_text(item) for item in (_as_list(record, "bases"))),
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
    """타입 그래프에 포함할 멤버의 정렬 키를 계산한다. (낮을수록 상위)

    가점: 검색어 히트당 5, 연결 타입 히트당 3, 생성자 10, 메서드(괄호 있음) 2,
          선언에 등장하는 SDK 타입 수(최대 6).
    감점: 소멸자/파이널라이저 100(사실상 제외), property 8(메서드보다 후순위).
    """
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
    """선택된 타입들에서 관계 엣지 목록을 뽑는다.

    엣지 종류:
      - inherits: 타입 → 베이스 타입 (상속)
      - returns : "타입.멤버" → 반환 타입 (그 타입을 얻는 방법)
      - accepts : "타입.멤버" → 파라미터 타입 (그 타입을 소비하는 방법)
    returns/accepts는 대상이 known_type_names(타입 인덱스에 있는 SDK 타입)일 때만 만든다.
    type_graph가 그래프를 인접 타입으로 확장할 때 이 엣지를 따라간다.
    """
    edges: List[Dict[str, Any]] = []
    edge_index: Dict[Tuple[str, str, str], int] = {}

    def append(edge: Dict[str, Any]) -> None:
        """(from, relation, to) 중복 엣지는 시그니처가 더 짧은(단순한) 쪽으로 갱신한다."""
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
        for base in _as_list(type_item, "bases"):
            base_name = _to_text(base)
            if base_name:
                append({"from": owner_type, "relation": "inherits", "to": base_name})

        for member in _as_list(type_item, "members"):
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
    """엣지 정렬 키. (낮을수록 상위)

    가중치: 질의 전체 일치 20, 1차 검색어 12, 세분화 검색어 4, 연결 타입 2.
    동점이면 시그니처가 짧은 엣지를 우선한다.
    """
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
    """엣지를 _type_edge_order 점수순으로 정렬한다."""
    return sorted(edges, key=lambda edge: _type_edge_order(edge, query, connected_types))


def _type_graph_operations(types: Sequence[Dict[str, Any]], known_type_names: set) -> List[Dict[str, Any]]:
    """선택된 타입들의 멤버를 "연산(operation)" 요약으로 변환한다.

    연산 = {소유 타입, 멤버명, C# 시그니처, returns(반환 SDK 타입), accepts(파라미터 SDK 타입),
            ref/out 파라미터 타입, enum 리터럴, 요약}.
    소멸자/생성자는 제외하고, SDK 타입이 아닌 반환/파라미터는 비워서 그래프 잡음을 줄인다.
    (owner, member, returns, accepts) 가 같은 중복 오버로드는 시그니처가 짧은 쪽만 남긴다.
    이 연산 목록이 _type_graph_paths의 그래프 간선 재료가 된다.
    """
    operations: List[Dict[str, Any]] = []
    operation_index: Dict[Tuple[str, str, str, Tuple[str, ...]], int] = {}
    for type_item in types:
        owner_type = _to_text(type_item.get("type_name"))
        if not owner_type:
            continue
        for member in _as_list(type_item, "members"):
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
    """연산 정렬 키. (낮을수록 상위)

    가중치: 1차 검색어 히트 14, 관련 타입(owner/returns/accepts와 교집합) 5, 세분화 검색어 4.
    소멸자나 생성자 형태(멤버명=타입명)는 8점 감점. 동점이면 시그니처 짧은 쪽 우선.
    """
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
    """연산을 _operation_order 점수순으로 정렬한다."""
    return sorted(operations, key=lambda operation: _operation_order(operation, query, relevant_types))


def _type_graph_paths(
    operations: Sequence[Dict[str, Any]],
    types: Sequence[Dict[str, Any]],
    query: str,
    *,
    limit: int = 6,
) -> List[Dict[str, Any]]:
    """타입 간 변환 경로를 BFS로 찾는다. ("A에서 B를 얻으려면 어떤 메서드를 거치나"의 답)

    1. 질의 1차 검색어와 가장 잘 맞는 타입(query_type_names)을 목표(goal)로 정한다.
    2. 연산/상속으로 인접 그래프(adjacency)를 만든다:
       returns(소유→반환), returned_by(반환→소유), accepted_by(파라미터→소유),
       inherits/base_of(상속 양방향).
    3. 멤버명이 검색어와 겹치는 연산의 타입들을 출발점(start_nodes)으로 삼는다.
    4. 각 출발점에서 BFS — 최대 7스텝, 노드 재방문 금지 — 로 목표 타입에 닿는 경로를 모은다.
    5. 목표 적합도/스텝 품질(step_order)로 정렬해 상위 limit개 반환.

    반환된 경로의 각 스텝에는 해당 변환을 수행하는 연산(멤버명, C# 시그니처)이 붙는다.
    """
    primary_terms = _query_primary_terms(query)
    if not primary_terms:
        return []

    # 목표 타입 선정: 검색어가 타입명에 많이(글자 수 가중) 포함될수록 높은 가중치.
    # 최고 가중치 동점이면 이름이 가장 짧은(가장 기본형인) 타입만 목표로 남긴다.
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

    # 인접 그래프 구축: 타입 이름 → 그 타입에서 나갈 수 있는 스텝 목록
    adjacency: Dict[str, List[Dict[str, Any]]] = {}

    def add_step(from_type: str, to_type: str, relation: str, operation: Optional[Dict[str, Any]] = None) -> None:
        """from_type → to_type 간선을 추가한다. 자기 자신으로의 간선은 무시."""
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
        for accepted in _as_list(operation, "accepts"):
            accepted_type = _to_text(accepted)
            if accepted_type and owner:
                add_step(accepted_type, owner, "accepted_by", operation)

    for type_item in types:
        type_name = _to_text(type_item.get("type_name"))
        for base in _as_list(type_item, "bases"):
            base_name = _to_text(base)
            if type_name in _CS_PRIMITIVE_TYPES or base_name in _CS_PRIMITIVE_TYPES:
                continue
            add_step(type_name, base_name, "inherits")
            add_step(base_name, type_name, "base_of")

    def step_order(step: Dict[str, Any]) -> Tuple[int, int, str]:
        """스텝(간선) 우선순위: 멤버명/시그니처가 양끝 타입과 관련 있을수록,
        accepted_by 관계일수록 우선. remove/delete/clear로 시작하는 파괴적 멤버는 감점."""
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

    # 출발점 선정: 멤버명이 검색어와 겹치는 연산의 반환/소유/파라미터 타입들
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
        for accepted in _as_list(operation, "accepts"):
            accepted_type = _to_text(accepted)
            if accepted_type and accepted_type in type_names and accepted_type not in start_nodes:
                start_nodes.append(accepted_type)

    # BFS 본체: 출발점 최대 16개, 경로당 최대 7스텝, 같은 노드 재방문 금지.
    # 목표(goal_nodes)에 닿으면 경로로 기록하되 탐색은 계속해 여러 경로를 수집한다.
    paths: List[Dict[str, Any]] = []
    seen_paths = set()
    goal_nodes = set(query_type_names)
    for start in start_nodes[:16]:
        # deque로 양끝 O(1) — list.pop(0)의 O(n) 제거
        queue: "deque[Tuple[str, List[Dict[str, Any]]]]" = deque([(start, [])])
        while queue and len(paths) < limit * 6:
            node, steps = queue.popleft()
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
            # 방문집합(사이클 방지)은 이웃마다가 아니라 노드당 한 번만 계산 (결과 동일)
            path_nodes = set()
            for existing in steps:
                path_nodes.add(_to_text(existing.get("from")))
                path_nodes.add(_to_text(existing.get("to")))
            for step in adjacency.get(node, [])[:24]:
                next_node = _to_text(step.get("to"))
                if not next_node or next_node in path_nodes:
                    continue
                queue.append((next_node, [*steps, step]))

    def path_order(path: Dict[str, Any]) -> Tuple[int, int, str]:
        """경로 우선순위: 목표 타입이 검색어와 잘 맞을수록, 스텝 품질이 좋고 짧을수록 상위."""
        target = _normalized_token(path.get("to"))
        target_hits = sum(1 for term in primary_terms if term and term in target)
        quality = sum(step_order(step)[0] for step in path.get("steps", []))
        return (-target_hits, quality, len(path.get("steps", [])), _to_text(path.get("to")))

    return sorted(paths, key=path_order)[:limit]


def type_graph(query: str, *, limit: int = 12) -> Dict[str, Any]:
    """질의 중심의 타입/멤버 관계 그래프를 만든다 — 이 파일에서 가장 복잡한 함수.

    에이전트가 "어떤 타입을 어떻게 조합해 쓰는가"를 한 번에 파악할 수 있도록,
    관련 타입·상속 관계·멤버 연산·타입 간 변환 경로를 모두 모아 압축한 결과를 반환한다.

    단계:
      1. declaration_search로 질의와 연결된 타입 이름(connected_types) 수집
      2. _type_order 점수로 타입 선별, 각 타입에 멤버 최대 96개 부착 (append_type)
      3. 베이스 타입 추가 + assignability(파생→베이스 대입 가능) 목록 작성
      4. 그래프 확장: 연결 타입을 선언에 쓰는 다른 소유 타입 → 파생 타입(베이스당 4개 제한)
         → 엣지(returns/accepts/inherits)를 따라 최대 2라운드 인접 타입 추가
      5. _type_graph_operations로 멤버를 연산 요약으로 변환, 점수순 정렬
      6. _type_graph_paths로 질의 타입까지의 변환 경로 BFS 탐색
      7. 모든 결과를 행(row) 배열로 압축 (열 정의는 _TYPE_GRAPH_SCHEMAS 의 schemas 필드 참조)
      8. _fit_type_graph_payload로 15000자 예산에 맞게 축소

    routers의 /source/type-graph와 에이전트의 source_type_graph 도구,
    그리고 find_source 내부에서 호출된다.
    """
    normalized_query = _to_text(query)
    safe_limit = _safe_limit(limit, default=12, high=20)
    declarations = declaration_search(normalized_query, limit=safe_limit).get("results", [])
    connected_types: List[str] = []
    for item in declarations:
        for token in _as_list(item, "types"):
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
        """타입을 그래프에 추가한다(중복 제거). 멤버를 점수순 정렬해 최대 96개까지 부착한다."""
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

    # 단계 3: 상속 기반 assignability 작성 + 베이스 타입도 그래프에 포함
    assignability = []
    for item in list(selected_types):
        for base in _as_list(item, "bases"):
            assignability.append({"from": item["type_name"], "to": base})
            if base not in seen_type_names:
                rec = type_record_by_name.get(base)
                if rec:
                    append_type(rec)

    # 선언 검색에서 나온 연결 타입도 빠짐없이 그래프에 포함
    for type_name in connected_types:
        if type_name in seen_type_names:
            continue
        rec = type_record_by_name.get(type_name)
        if rec:
            append_type(rec)

    # 단계 4-a: 지금까지 모은 타입을 멤버 선언에 사용하는 "소유 타입"을 점수순으로 추가
    # (예: NXLayer가 그래프에 있으면 NXLayer를 다루는 NXLayerManager 같은 타입을 발견)
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
        rec = type_record_by_name.get(owner_type)
        if rec:
            append_type(rec)
        if len(selected_types) >= safe_limit + 6:
            break

    # 단계 4-b: 그래프 내 타입을 상속하는 파생 타입 추가 (베이스당 최대 4개로 폭발 방지)
    derived_counts: Dict[str, int] = {}
    for record in type_records:
        bases = _as_list(record, "bases")
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
    # 단계 4-c: 소유 타입 2차 보강 (4-a와 같은 기준, 한도만 +8로 완화)
    for member_record in load_methods_index():
        declaration_tokens = {_normalized_token(item) for item in _declaration_type_tokens(_to_text(member_record.get("declaration")))}
        if not declaration_tokens.intersection(connected_keys):
            continue
        owner_type = _to_text(member_record.get("type_name"))
        if not owner_type or owner_type in seen_type_names:
            continue
        rec = type_record_by_name.get(owner_type)
        if rec:
            append_type(rec)
        if len(selected_types) >= safe_limit + 8:
            break
    # 단계 4-d: returns/accepts/inherits 엣지를 따라 인접 타입을 최대 2라운드 확장
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
    # 단계 5~8: 연산 추출/정렬 → 경로 BFS → 행 형식 압축 → 글자 예산 맞춤
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
    event_declarations = _event_declarations_for_types(selected_types, limit=min(12, safe_limit))
    payload = {
        "ok": True,
        "query": normalized_query,
        "schemas": _TYPE_GRAPH_SCHEMAS,
        "declarations": [_type_graph_declaration_row(item) for item in declarations[: min(4, safe_limit)]],
        "types": [_type_graph_type_row(item) for item in selected_types[: safe_limit + 4]],
        "assignability": [_type_graph_assignability_row(item) for item in assignability],
        "event_declarations": event_declarations,
        "edges": [],
        "operations": [_type_graph_operation_row(item) for item in operations],
        "paths": [_type_graph_path_row(item) for item in paths[:3]],
    }
    return _fit_type_graph_payload(payload)



# ==========================================================================
#  공개 심볼
# ==========================================================================

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

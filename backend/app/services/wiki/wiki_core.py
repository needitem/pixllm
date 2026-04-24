import json
import re
import time
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import yaml

from ... import config
from ..tools.query_terms import compact_token, extract_query_compacts, extract_query_terms, extract_symbol_query_candidates
from ...utils.time import now_iso
from .methods_index import (
    METHODS_INDEX_RELATIVE_PATH,
    build_methods_index_from_raw_source,
    build_method_page_results_for_root,
    load_methods_index_for_root,
    methods_index_file_for_root,
)
from .source_ingest import (
    SOURCE_MANIFEST_RELATIVE_PATH,
    build_source_manifest_from_raw_source,
    build_workflow_runtime_status_block,
    load_source_manifest_for_root,
    render_source_page,
    source_manifest_file_for_root,
    source_page_path_for_module,
    upsert_workflow_runtime_status,
)

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_CORE_COORDINATION_PATHS = (
    "README.md",
    "SCHEMA.md",
    "index.md",
    "log.md",
    "pages/home.md",
)
_OPTIONAL_COORDINATION_PATHS: Tuple[str, ...] = ()
_STRUCTURE_DIRS = (
    "pages",
    "pages/sources",
    "pages/topics",
    "pages/howtos",
    "pages/concepts",
    "pages/entities",
    "pages/analyses",
    "pages/decisions",
    "workflows",
)
_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_SOURCE_ANCHOR_RE = re.compile(r"\bSource/[^`\s:]+:\d+(?:-\d+)?\b")
_INLINE_PAGE_PATH_RE = re.compile(
    r"\b(?:(?:README|SCHEMA|index|log)\.md|(?:workflows|pages(?:/[A-Za-z0-9_.-]+)+)/[A-Za-z0-9_.-]+\.md)\b"
)
_CURATED_KINDS = {"home", "topic", "howto", "concept", "entity", "analysis", "decision", "workflow", "source", "page"}
_WRITEBACK_CATEGORY_PATHS = {
    "analysis": "pages/analyses",
    "decision": "pages/decisions",
    "topic": "pages/topics",
}
_RUNTIME_MANIFEST_PATH = ".runtime/manifest.json"
_RUNTIME_MANIFEST_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def _slugify(value: str, fallback: str = "engine") -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return fallback
    slug = re.sub(r"[^a-z0-9._-]+", "-", raw).strip("._-")
    return slug[:80] or fallback


def wiki_parent_root() -> Path:
    return _BACKEND_ROOT / config.WIKI_PROFILE_DIR / "wiki"


def wiki_root(wiki_id: str = "engine") -> Path:
    return wiki_parent_root() / _slugify(wiki_id, "engine")


def raw_source_root() -> Path:
    return Path(config.RAW_SOURCE_ROOT)


def _raw_source_root_text() -> str:
    return raw_source_root().resolve().as_posix()


def _normalize_page_path(value: str) -> str:
    raw = str(value or "").strip().replace("\\", "/").replace("./", "", 1)
    normalized = PurePosixPath(raw or "index.md").as_posix()
    if normalized.startswith("/") or normalized == ".." or normalized.startswith("../"):
        raise ValueError("page path must stay inside the wiki root")
    if not normalized.lower().endswith(".md"):
        normalized = f"{normalized}.md"
    return normalized


def _read_frontmatter(raw_text: str) -> Tuple[Dict[str, Any], str]:
    text = str(raw_text or "").lstrip("\ufeff")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    try:
        meta = yaml.safe_load(text[4:end]) or {}
    except Exception:
        meta = {}
    body = text[end + 5 :]
    return meta if isinstance(meta, dict) else {}, body


def _extract_title(path: str, content: str) -> str:
    meta, body = _read_frontmatter(content)
    title = str(meta.get("title") or "").strip()
    if title:
        return title
    for line in str(body or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return PurePosixPath(path).stem


def _extract_summary(content: str) -> str:
    meta, body = _read_frontmatter(content)
    description = str(meta.get("description") or "").strip()
    if description:
        return description[:240]
    lines = [line.strip() for line in str(body or "").splitlines() if line.strip()]
    if not lines:
        return ""
    return " ".join(lines[:4])[:240]


def _normalize_multiline_text(value: str) -> str:
    return str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def _normalize_string_list(values: Any, *, limit: int = 24) -> List[str]:
    output: List[str] = []
    seen = set()
    for item in values if isinstance(values, list) else []:
        normalized = str(item or "").strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(normalized)
        if len(output) >= limit:
            break
    return output


def _normalize_lookup_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())


def _compact_values(values: Iterable[str]) -> List[str]:
    output: List[str] = []
    seen = set()
    for item in values or []:
        compact = compact_token(item)
        if not compact or compact in seen:
            continue
        seen.add(compact)
        output.append(compact)
    return output


def _expand_manifest_match_tokens(values: Iterable[str]) -> List[str]:
    expanded: List[str] = []
    for item in values or []:
        raw_value = str(item or "").strip()
        if not raw_value:
            continue
        expanded.append(raw_value)
        expanded.extend(extract_query_terms(raw_value, limit=24))
        expanded.extend(extract_query_compacts(raw_value, limit=24))
    return _compact_values(expanded)


def _runtime_manifest_file(root: Path) -> Path:
    return root / PurePosixPath(_RUNTIME_MANIFEST_PATH).as_posix()


def _load_runtime_manifest_for_root(root: Path) -> Dict[str, Any]:
    path = _runtime_manifest_file(root)
    if not path.exists():
        return {}
    cache_key = str(path.resolve())
    try:
        mtime = path.stat().st_mtime
    except Exception:
        mtime = 0.0
    cached = _RUNTIME_MANIFEST_CACHE.get(cache_key)
    if cached and cached[0] == mtime:
        return cached[1]
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}
    normalized = payload if isinstance(payload, dict) else {}
    _RUNTIME_MANIFEST_CACHE[cache_key] = (mtime, normalized)
    return normalized


def _yaml_dump(data: Dict[str, Any]) -> str:
    clean: Dict[str, Any] = {}
    for key, value in (data or {}).items():
        if value in (None, "", [], {}):
            continue
        clean[str(key)] = value
    if not clean:
        return ""
    return str(
        yaml.safe_dump(
            clean,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        )
    ).strip()


def _render_markdown_page(meta: Dict[str, Any], body: str) -> str:
    normalized_body = _normalize_multiline_text(body)
    frontmatter = _yaml_dump(meta)
    if not frontmatter:
        return f"{normalized_body}\n" if normalized_body else ""
    if not normalized_body:
        return f"---\n{frontmatter}\n---\n"
    return f"---\n{frontmatter}\n---\n\n{normalized_body}\n"


def _link_targets(content: str) -> List[str]:
    links: List[str] = []
    for match in _MARKDOWN_LINK_RE.finditer(str(content or "")):
        target = str(match.group(1) or "").strip()
        if not target or target.startswith("#") or "://" in target or target.startswith("mailto:"):
            continue
        links.append(target.split("#", 1)[0].strip())
    return links


def _inline_page_targets(content: str) -> List[str]:
    targets: List[str] = []
    for match in _INLINE_PAGE_PATH_RE.finditer(str(content or "")):
        target = str(match.group(0) or "").strip().strip("`")
        if not target or "://" in target:
            continue
        targets.append(target)
    return targets


def _has_source_evidence(meta: Dict[str, Any], content: str) -> bool:
    sources = meta.get("sources")
    if isinstance(sources, list) and any(str(item or "").strip() for item in sources):
        return True
    lowered = str(content or "").lower()
    if _SOURCE_ANCHOR_RE.search(str(content or "")):
        return True
    return "](raw/" in lowered or "](pages/sources/" in lowered


def _infer_kind(path: str) -> str:
    lowered = str(path or "").lower()
    if lowered == "schema.md":
        return "schema"
    if lowered == "index.md":
        return "index"
    if lowered == "log.md":
        return "log"
    if lowered == "readme.md":
        return "readme"
    if lowered == "pages/home.md":
        return "home"
    if lowered.startswith("pages/sources/"):
        return "source"
    if lowered.startswith("pages/topics/"):
        return "topic"
    if lowered.startswith("pages/howtos/"):
        return "howto"
    if lowered.startswith("pages/concepts/"):
        return "concept"
    if lowered.startswith("pages/entities/"):
        return "entity"
    if lowered.startswith("pages/analyses/"):
        return "analysis"
    if lowered.startswith("pages/decisions/"):
        return "decision"
    if lowered.startswith("workflows/"):
        return "workflow"
    if lowered.startswith("pages/"):
        return "page"
    return "wiki"


__all__ = [name for name in globals() if not name.startswith("__")]

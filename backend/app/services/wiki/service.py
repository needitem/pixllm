import json
import re
import time
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import yaml

from ... import config
from ...utils.time import now_iso

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_CORE_COORDINATION_PATHS = (
    "README.md",
    "SCHEMA.md",
    "index.md",
    "log.md",
    "pages/home.md",
)
_OPTIONAL_COORDINATION_PATHS = (
    "01-method-wiki-index.md",
)
_STRUCTURE_DIRS = (
    "raw/inbox",
    "raw/processed",
    "pages",
    "pages/sources",
    "pages/topics",
    "pages/entities",
    "pages/analyses",
    "pages/decisions",
    "methods",
    "workflows",
)
_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_SOURCE_ANCHOR_RE = re.compile(r"\bSource/[^`\s:]+:\d+(?:-\d+)?\b")
_SOURCE_REF_CAPTURE_RE = re.compile(r"\b(Source/[^`\s:]+):(\d+)(?:-(\d+))?\b")
_SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
_CURATED_KINDS = {"home", "topic", "entity", "analysis", "decision", "workflow", "source", "page"}
_WRITEBACK_CATEGORY_PATHS = {
    "analysis": "pages/analyses",
    "decision": "pages/decisions",
    "topic": "pages/topics",
}
_RUNTIME_MANIFEST_PATH = ".runtime/manifest.json"


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


def _normalize_page_path(value: str) -> str:
    raw = str(value or "").strip().replace("\\", "/").replace("./", "", 1)
    normalized = PurePosixPath(raw or "index.md").as_posix()
    if normalized.startswith("/") or normalized == ".." or normalized.startswith("../"):
        raise ValueError("page path must stay inside the wiki root")
    if not normalized.lower().endswith(".md"):
        normalized = f"{normalized}.md"
    return normalized


def _read_frontmatter(raw_text: str) -> Tuple[Dict[str, Any], str]:
    text = str(raw_text or "")
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


def _runtime_manifest_file(root: Path) -> Path:
    return root / PurePosixPath(_RUNTIME_MANIFEST_PATH).as_posix()


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


def _safe_source_page_stem(source_path: str, title: str = "", fallback: str = "source") -> str:
    source_value = str(source_path or "").strip().replace("\\", "/")
    candidate = title or PurePosixPath(source_value).stem or PurePosixPath(source_value).name
    return _slugify(candidate, fallback)


def _heading_candidates(text: str, limit: int = 6) -> List[str]:
    seen = set()
    output: List[str] = []
    for raw_line in _normalize_multiline_text(text).splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
        else:
            heading = ""
        if not heading:
            continue
        key = heading.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(heading)
        if len(output) >= limit:
            break
    return output


def _link_targets(content: str) -> List[str]:
    links: List[str] = []
    for match in _MARKDOWN_LINK_RE.finditer(str(content or "")):
        target = str(match.group(1) or "").strip()
        if not target or target.startswith("#") or "://" in target or target.startswith("mailto:"):
            continue
        links.append(target.split("#", 1)[0].strip())
    return links


def _has_source_evidence(meta: Dict[str, Any], content: str) -> bool:
    sources = meta.get("sources")
    if isinstance(sources, list) and any(str(item or "").strip() for item in sources):
        return True
    lowered = str(content or "").lower()
    if _SOURCE_ANCHOR_RE.search(str(content or "")):
        return True
    return "](raw/" in lowered or "](pages/sources/" in lowered


def _resolve_relative_link_path(root: Path, current_path: str, raw_target: str) -> Optional[str]:
    target = str(raw_target or "").strip()
    if not target:
        return None
    candidate = PurePosixPath(PurePosixPath(current_path).parent, target).as_posix()
    normalized_candidate = str(PurePosixPath(candidate)).replace("\\", "/").lstrip("/")
    direct_path = (root / normalized_candidate).resolve()
    if direct_path.exists():
        return normalized_candidate
    try:
        normalized_page = _normalize_page_path(candidate)
    except ValueError:
        return None
    page_path = (root / normalized_page).resolve()
    if page_path.exists():
        return normalized_page
    return normalized_page


def _extract_section_yaml(content: str, heading: str) -> Dict[str, Any]:
    _meta, body = _read_frontmatter(content)
    lines = str(body or "").splitlines()
    normalized_heading = str(heading or "").strip().lower()
    for index, raw_line in enumerate(lines):
        if str(raw_line or "").strip().lower() != f"## {normalized_heading}":
            continue
        cursor = index + 1
        while cursor < len(lines) and not str(lines[cursor] or "").strip():
            cursor += 1
        if cursor >= len(lines) or str(lines[cursor] or "").strip().lower() not in {"```yaml", "```yml"}:
            return {}
        cursor += 1
        block_lines: List[str] = []
        while cursor < len(lines) and str(lines[cursor] or "").strip() != "```":
            block_lines.append(lines[cursor])
            cursor += 1
        try:
            parsed = yaml.safe_load("\n".join(block_lines)) or {}
        except Exception:
            parsed = {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _extract_method_records(root: Path, pages: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for page in pages or []:
        path = str(page.get("path") or "")
        if str(page.get("kind") or "") != "method":
            continue
        stem = PurePosixPath(path).stem
        if not stem.startswith("Methods_T_"):
            continue
        qualified_type = stem[len("Methods_T_") :].replace("_", ".")
        type_name = qualified_type.split(".")[-1]
        lines = str(page.get("content") or "").splitlines()
        section_starts = [
            index
            for index, raw_line in enumerate(lines)
            if _SECTION_HEADING_RE.match(str(raw_line or ""))
        ]
        for section_index, start in enumerate(section_starts):
            match = _SECTION_HEADING_RE.match(lines[start])
            member_name = str(match.group(1) if match else "").strip()
            if not member_name or member_name.lower() == "overview":
                continue
            end = section_starts[section_index + 1] if section_index + 1 < len(section_starts) else len(lines)
            section_text = "\n".join(lines[start:end]).strip()
            if not section_text:
                continue
            source_refs = [
                {
                    "path": str(ref_match.group(1) or "").strip().replace("\\", "/"),
                    "line_range": (
                        f"{max(1, int(ref_match.group(2) or 1))}-{max(max(1, int(ref_match.group(2) or 1)), int(ref_match.group(3) or ref_match.group(2) or 1))}"
                    ),
                }
                for ref_match in _SOURCE_REF_CAPTURE_RE.finditer(section_text)
            ]
            records.append(
                {
                    "qualified_type": qualified_type,
                    "type_name": type_name,
                    "member_name": member_name,
                    "qualified_symbol": f"{qualified_type}.{member_name}",
                    "doc_path": path,
                    "heading_path": f"{qualified_type} Methods > {member_name}",
                    "text": section_text,
                    "source_refs": source_refs,
                }
            )
    return records


def _resolve_method_records_for_symbols(
    symbols: Sequence[str],
    methods_index: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    by_qualified: Dict[str, Dict[str, Any]] = {}
    by_short_qualified: Dict[str, Dict[str, Any]] = {}
    by_member: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for record in methods_index or []:
        qualified_symbol = str(record.get("qualified_symbol") or "").strip()
        type_name = str(record.get("type_name") or "").strip()
        member_name = str(record.get("member_name") or "").strip()
        qualified_type = str(record.get("qualified_type") or "").strip()
        if qualified_symbol:
            by_qualified[_normalize_lookup_token(qualified_symbol)] = record
        if type_name and member_name:
            by_short_qualified[_normalize_lookup_token(f"{type_name}.{member_name}")] = record
        if qualified_type and member_name:
            by_short_qualified[_normalize_lookup_token(f"{qualified_type}.{member_name}")] = record
        if member_name:
            by_member[_normalize_lookup_token(member_name)].append(record)

    output: List[Dict[str, Any]] = []
    seen = set()
    for symbol in symbols or []:
        normalized_symbol = _normalize_lookup_token(symbol)
        if not normalized_symbol:
            continue
        selected = by_qualified.get(normalized_symbol) or by_short_qualified.get(normalized_symbol)
        if selected is None and "." not in str(symbol or ""):
            member_matches = by_member.get(normalized_symbol, [])
            if len(member_matches) == 1:
                selected = member_matches[0]
        if not selected:
            continue
        key = str(selected.get("qualified_symbol") or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(selected)
    return output


def _build_workflow_manifest_entry(
    page: Dict[str, Any],
    methods_index: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    content = str(page.get("content") or "")
    meta, _body = _read_frontmatter(content)
    required_section = _extract_section_yaml(content, "Required Facts")
    frontmatter_symbols = _normalize_string_list(meta.get("symbols"))
    required_symbols = _normalize_string_list(required_section.get("required_symbols"))
    required_facts: List[Dict[str, Any]] = []
    for item in required_section.get("required_facts") if isinstance(required_section.get("required_facts"), list) else []:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol") or "").strip()
        if not symbol:
            continue
        required_facts.append(
            {
                "symbol": symbol,
                "declaration": str(item.get("declaration") or "").strip() or None,
                "declaration_candidates": item.get("declaration_candidates") if isinstance(item.get("declaration_candidates"), list) else None,
                "source": str(item.get("source") or "").strip() or None,
            }
        )
    explicit_symbols = _normalize_string_list([item.get("symbol") for item in required_facts if isinstance(item, dict)], limit=64)
    linked_records = _resolve_method_records_for_symbols(
        [*explicit_symbols, *required_symbols],
        methods_index,
    )
    route_terms = _normalize_string_list(
        [
            page.get("title"),
            PurePosixPath(str(page.get("path") or "")).stem,
            required_section.get("workflow_family"),
            *(_normalize_string_list(meta.get("aliases"))),
            *frontmatter_symbols,
            *required_symbols,
        ],
        limit=64,
    )
    return {
        "path": str(page.get("path") or "").strip(),
        "title": str(page.get("title") or "").strip(),
        "summary": str(page.get("summary") or "").strip(),
        "aliases": _normalize_string_list(meta.get("aliases")),
        "symbols": frontmatter_symbols,
        "tags": _normalize_string_list(meta.get("tags")),
        "workflow_family": str(required_section.get("workflow_family") or "").strip(),
        "output_shape": str(required_section.get("output_shape") or "").strip(),
        "required_output_files": _normalize_string_list(required_section.get("required_output_files")),
        "required_symbols": required_symbols,
        "required_facts": required_facts,
        "verification_rules": _normalize_string_list(required_section.get("verification_rules")),
        "route_terms": route_terms,
        "linked_method_symbols": _normalize_string_list([record.get("qualified_symbol") for record in linked_records], limit=64),
        "source_anchors": _normalize_string_list(_SOURCE_ANCHOR_RE.findall(content), limit=64),
        "content": content,
    }


def _build_runtime_manifest(root: Path, pages: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    methods_index = _extract_method_records(root, pages)
    workflow_index = [
        _build_workflow_manifest_entry(page, methods_index)
        for page in pages or []
        if str(page.get("kind") or "") == "workflow"
    ]
    return {
        "version": 1,
        "wiki_id": root.name,
        "generated_at": now_iso(),
        "methods_index": methods_index,
        "workflow_index": workflow_index,
    }


def _infer_kind(path: str) -> str:
    lowered = str(path or "").lower()
    if lowered == "schema.md":
        return "schema"
    if lowered == "index.md" or lowered.endswith("method-wiki-index.md"):
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
    if lowered.startswith("pages/entities/"):
        return "entity"
    if lowered.startswith("pages/analyses/"):
        return "analysis"
    if lowered.startswith("pages/decisions/"):
        return "decision"
    if lowered.startswith("raw/inbox/"):
        return "raw_inbox"
    if lowered.startswith("raw/processed/"):
        return "raw_processed"
    if lowered.startswith("workflows/"):
        return "workflow"
    if lowered.startswith("methods/"):
        return "method"
    if lowered.startswith("pages/"):
        return "page"
    return "wiki"


def _build_excerpt(content: str, query: str, limit: int = 420) -> str:
    source = str(content or "")
    lowered = source.lower()
    needle = str(query or "").strip().lower()
    if not needle:
        return source[:limit]
    index = lowered.find(needle)
    if index < 0:
        return source[:limit]
    start = max(0, index - 120)
    end = min(len(source), index + max(120, len(needle) + 120))
    return source[start:end][:limit]


def _score_page(page: Dict[str, Any], query: str) -> int:
    needle = str(query or "").strip().lower()
    if not needle:
        priority = {
            "schema": 100,
            "home": 96,
            "index": 92,
            "workflow": 88,
            "topic": 84,
            "analysis": 82,
            "source": 80,
            "entity": 78,
            "decision": 76,
            "log": 58,
            "readme": 56,
            "method": 28,
            "raw_processed": 8,
        }
        return priority.get(str(page.get("kind") or ""), 10)

    title = str(page.get("title") or "").lower()
    path = str(page.get("path") or "").lower()
    summary = str(page.get("summary") or "").lower()
    content = str(page.get("content") or "").lower()
    tokens = [token for token in re.split(r"[\s|]+", needle) if token]
    score = 0
    for token in tokens:
        if token in title:
            score += 20
        if token in path:
            score += 16
        if token in summary:
            score += 10
        if token in content:
            score += 4
    if needle in content:
        score += 10
    kind = str(page.get("kind") or "")
    if kind in {"workflow", "topic", "analysis", "source", "entity", "decision"}:
        score += 8
    if kind in {"raw_processed", "raw_inbox"}:
        score -= 6
    if re.search(r"(workflow|steps|guide|how to|example|usage|program|flow|만들|예제|단계|도시|표시|로드)", needle, re.IGNORECASE):
        if kind == "workflow":
            score += 24
        elif kind in {"topic", "analysis"}:
            score += 10
        elif kind == "method":
            score -= 8
    return score


def _page_payload(root: Path, file_path: Path) -> Dict[str, Any]:
    raw_text = file_path.read_text(encoding="utf-8")
    rel_path = file_path.relative_to(root).as_posix()
    stat = file_path.stat()
    return {
        "wiki_id": root.name,
        "path": rel_path,
        "title": _extract_title(rel_path, raw_text),
        "kind": _infer_kind(rel_path),
        "content": raw_text,
        "summary": _extract_summary(raw_text),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat.st_mtime)),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat.st_ctime)),
        "version": 1,
    }


class WikiService:
    def __init__(self, redis=None):
        self.redis = redis

    def _root(self, wiki_id: str) -> Path:
        return wiki_root(wiki_id)

    def _page_file(self, wiki_id: str, page_path: str) -> Path:
        root = self._root(wiki_id)
        normalized = _normalize_page_path(page_path)
        target = (root / normalized).resolve()
        if root.resolve() not in target.parents and target != root.resolve():
            raise ValueError("page path must stay inside the wiki root")
        return target

    def _write_page_text(self, wiki_id: str, page_path: str, content: str) -> Dict[str, Any]:
        file_path = self._page_file(wiki_id, page_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(str(content or ""), encoding="utf-8")
        return _page_payload(self._root(wiki_id), file_path)

    def _meta(self, wiki_id: str) -> Dict[str, Any]:
        normalized_wiki_id = _slugify(wiki_id, "engine")
        root = self._root(normalized_wiki_id)
        pages = list(root.rglob("*.md")) if root.exists() else []
        updated_at = None
        if pages:
            updated_at = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ",
                time.gmtime(max(item.stat().st_mtime for item in pages)),
            )
        description = ""
        readme = root / "README.md"
        if readme.exists():
            description = _extract_summary(readme.read_text(encoding="utf-8"))
        return {
            "id": normalized_wiki_id,
            "name": normalized_wiki_id,
            "description": description,
            "root_path": root.relative_to(_BACKEND_ROOT).as_posix() if root.exists() else root.relative_to(_BACKEND_ROOT).as_posix(),
            "page_count": len(pages),
            "updated_at": updated_at or now_iso(),
        }

    def _coordination_status_payload(
        self,
        *,
        wiki_id: str,
        present_paths: Iterable[str],
        missing_paths_before: Iterable[str],
        created_paths: Iterable[str],
        root_created: bool,
    ) -> Dict[str, Any]:
        required_paths = list(_CORE_COORDINATION_PATHS)
        optional_paths = list(_OPTIONAL_COORDINATION_PATHS)
        present_path_set = {str(path or "") for path in present_paths if str(path or "")}
        required_present = [path for path in required_paths if path in present_path_set]
        optional_present = [path for path in optional_paths if path in present_path_set]
        return {
            "wiki_id": _slugify(wiki_id, "engine"),
            "required_paths": required_paths,
            "optional_paths": optional_paths,
            "required_present_paths": required_present,
            "optional_present_paths": optional_present,
            "present_paths": [*required_present, *optional_present],
            "missing_paths": [path for path in required_paths if path not in required_present],
            "missing_paths_before": [str(path or "") for path in missing_paths_before if str(path or "")],
            "created_paths": [str(path or "") for path in created_paths if str(path or "")],
            "auto_bootstrapped": bool(root_created or list(created_paths)),
            "has_coordination_spine": all(path in required_present for path in required_paths),
        }

    async def list_wikis(self) -> List[Dict[str, Any]]:
        parent = wiki_parent_root()
        if not parent.exists():
            return []
        items = []
        for child in sorted(parent.iterdir()):
            if not child.is_dir():
                continue
            if not list(child.rglob("*.md")):
                continue
            items.append(self._meta(child.name))
        return items

    async def list_pages(self, wiki_id: str) -> List[Dict[str, Any]]:
        root = self._root(wiki_id)
        if not root.exists():
            return []
        return [_page_payload(root, file_path) for file_path in sorted(root.rglob("*.md"))]

    async def get_page(self, wiki_id: str, page_path: str) -> Optional[Dict[str, Any]]:
        file_path = self._page_file(wiki_id, page_path)
        root = self._root(wiki_id)
        if not file_path.exists() or not file_path.is_file():
            return None
        return _page_payload(root, file_path)

    def _bootstrap_templates(self, wiki_id: str) -> List[Dict[str, str]]:
        today = now_iso()[:10]
        return [
            {
                "path": "README.md",
                "kind": "readme",
                "content": "\n".join([
                    "# LLM Wiki",
                    "",
                    f"This wiki compiles knowledge for `{wiki_id}` into persistent markdown pages.",
                    "",
                    "## Layers",
                    "",
                    "- `raw/` keeps immutable source manifests and ingestion traces.",
                    "- `pages/` keeps curated synthesis pages for topics, entities, analyses, and decisions.",
                    "- `methods/` and `workflows/` keep generated and verified reference material.",
                    "",
                    "## Operations",
                    "",
                    "- Ingest writes raw manifests, source summaries, curated topic pages, `index.md`, and `log.md`.",
                    "- Query should prefer the wiki first and fall back to raw retrieval only when coverage is weak.",
                    "- Lint should detect broken links, orphan pages, and uncited curated claims.",
                ]),
            },
            {
                "path": "SCHEMA.md",
                "kind": "schema",
                "content": "\n".join([
                    "# LLM Wiki Schema",
                    "",
                    "## Canonical Structure",
                    "",
                    "- `README.md`: human-readable overview of the wiki and its operating model.",
                    "- `SCHEMA.md`: editing rules and directory conventions.",
                    "- `index.md`: generated content-oriented catalog for navigation.",
                    "- `log.md`: chronological append-only record of ingest, writeback, and lint events.",
                    "- `pages/home.md`: curated landing page for high-level orientation.",
                    "- `raw/inbox/`: source manifests waiting for normalization or follow-up.",
                    "- `raw/processed/`: immutable source manifests that have been ingested.",
                    "- `pages/sources/`: source summary pages derived from raw sources.",
                    "- `pages/topics/`: curated synthesis pages for recurring themes or features.",
                    "- `pages/entities/`: entity-centric reference pages when named subjects matter.",
                    "- `pages/analyses/`: saved query answers, comparisons, and deep dives.",
                    "- `pages/decisions/`: decision records and notable tradeoffs.",
                    "- `workflows/`: verified task or implementation workflows.",
                    "- `methods/`: generated reference material; do not treat this as the whole wiki.",
                    "",
                    "## Editing Rules",
                    "",
                    "- Prefer updating curated pages under `pages/` over editing generated `methods/` pages.",
                    "- Every curated page should carry explicit provenance via `sources` frontmatter or inline source anchors.",
                    "- `index.md` must be rebuilt after ingest, writeback, or major manual edits.",
                    "- `log.md` must record ingest, writeback, lint, and repair events.",
                    "- Keep relative markdown links stable.",
                ]),
            },
            {
                "path": "index.md",
                "kind": "index",
                "content": "\n".join([
                    "# LLM Wiki Index",
                    "",
                    "- [SCHEMA.md](SCHEMA.md)",
                    "- [log.md](log.md)",
                    "- [pages/home.md](pages/home.md)",
                    "",
                    "## Curated Content",
                    "",
                    "- This file is generated. Rebuild it after ingest, writeback, or repair.",
                    "",
                    "## Reference",
                    "",
                    "- [01-method-wiki-index.md](01-method-wiki-index.md) - generated method catalog, if present",
                    "- [methods/](methods/) - generated method reference pages",
                    "- [workflows/](workflows/) - verified workflow pages",
                ]),
            },
            {
                "path": "log.md",
                "kind": "log",
                "content": "\n".join([
                    "# LLM Wiki Log",
                    "",
                    f"## [{today}] bootstrap | Initialize wiki structure",
                    "",
                    "- Created the coordination spine and baseline folders for wiki-first operation.",
                ]),
            },
            {
                "path": "pages/home.md",
                "kind": "home",
                "content": "\n".join([
                    "# Wiki Home",
                    "",
                    "Use this page for a curated overview of the knowledge base.",
                    "",
                    "## Start Here",
                    "",
                    "- Review [index.md](../index.md) for the current catalog.",
                    "- Review [SCHEMA.md](../SCHEMA.md) before changing page structure.",
                    "- Use `pages/topics/`, `pages/entities/`, `pages/analyses/`, and `pages/decisions/` for curated synthesis.",
                ]),
            },
        ]

    async def ensure_coordination_pages(
        self,
        wiki_id: str,
        *,
        create_if_missing: bool = True,
    ) -> Dict[str, Any]:
        normalized_wiki_id = _slugify(wiki_id, "engine")
        root = self._root(normalized_wiki_id)
        root_existed = root.exists()
        if not root_existed and not create_if_missing:
            return self._coordination_status_payload(
                wiki_id=normalized_wiki_id,
                present_paths=[],
                missing_paths_before=_CORE_COORDINATION_PATHS,
                created_paths=[],
                root_created=False,
            )

        if create_if_missing:
            root.mkdir(parents=True, exist_ok=True)
            for rel_dir in _STRUCTURE_DIRS:
                (root / rel_dir).mkdir(parents=True, exist_ok=True)

        templates = self._bootstrap_templates(normalized_wiki_id)
        created_paths: List[str] = []
        present_paths: List[str] = []
        missing_paths_before: List[str] = []

        for template in templates:
            path = template["path"]
            file_path = self._page_file(normalized_wiki_id, path)
            if file_path.exists():
                present_paths.append(path)
                continue
            missing_paths_before.append(path)
            if not create_if_missing:
                continue
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(template["content"], encoding="utf-8")
            created_paths.append(path)
            present_paths.append(path)

        existing_paths = set(present_paths)
        if root.exists():
            for extra_path in _OPTIONAL_COORDINATION_PATHS:
                if extra_path in existing_paths:
                    continue
                file_path = self._page_file(normalized_wiki_id, extra_path)
                if file_path.exists():
                    present_paths.append(extra_path)

        return self._coordination_status_payload(
            wiki_id=normalized_wiki_id,
            present_paths=present_paths,
            missing_paths_before=missing_paths_before,
            created_paths=created_paths,
            root_created=bool(create_if_missing and not root_existed),
        )

    async def write_page(
        self,
        wiki_id: str,
        page_path: str,
        content: str,
        *,
        title: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> Dict[str, Any]:
        del title, kind
        normalized_wiki_id = _slugify(wiki_id, "engine")
        await self.ensure_coordination_pages(normalized_wiki_id, create_if_missing=True)
        page = self._write_page_text(normalized_wiki_id, page_path, content)
        page_kind = str(page.get("kind") or "")
        if page_kind not in {"index", "log", "schema", "readme", "raw_inbox", "raw_processed"}:
            await self.rebuild_index(normalized_wiki_id)
            await self.append_log(
                normalized_wiki_id,
                title=f"Edit {page.get('title') or page.get('path')}",
                body_lines=[f"Updated page `{page.get('path')}`."],
                kind="edit",
            )
        return page

    async def append_log(
        self,
        wiki_id: str,
        *,
        title: str,
        body_lines: Iterable[str],
        kind: str = "update",
    ) -> Dict[str, Any]:
        page = await self.get_page(wiki_id, "log.md")
        content = str(page.get("content") or "# LLM Wiki Log\n") if page else "# LLM Wiki Log\n"
        date = now_iso()[:10]
        lines = [f"## [{date}] {str(kind or 'update').strip()} | {str(title or 'Log entry').strip()}", ""]
        for body_line in body_lines:
            text = str(body_line or "").strip()
            if text:
                lines.append(f"- {text}")
        if len(lines) == 2:
            lines.append("- Updated wiki content.")
        lines.append("")
        next_content = f"{content.rstrip()}\n\n" + "\n".join(lines)
        return self._write_page_text(wiki_id, "log.md", next_content)

    async def rebuild_index(self, wiki_id: str) -> Dict[str, Any]:
        await self.ensure_coordination_pages(wiki_id, create_if_missing=True)
        normalized_wiki_id = _slugify(wiki_id, "engine")
        root = self._root(normalized_wiki_id)
        pages = await self.list_pages(normalized_wiki_id)
        groups = {
            "Coordination": {"readme", "schema", "index", "log", "home"},
            "Sources": {"source"},
            "Topics": {"topic"},
            "Entities": {"entity"},
            "Analyses": {"analysis"},
            "Decisions": {"decision"},
            "Workflows": {"workflow"},
            "Reference": {"method"},
            "Raw": {"raw_inbox", "raw_processed"},
            "Other": {"page", "wiki"},
        }

        page_groups: Dict[str, List[Dict[str, Any]]] = {name: [] for name in groups}
        for page in pages:
            kind = str(page.get("kind") or "")
            matched = False
            for group_name, group_kinds in groups.items():
                if kind in group_kinds:
                    page_groups[group_name].append(page)
                    matched = True
                    break
            if not matched:
                page_groups["Other"].append(page)

        lines = [
            "# LLM Wiki Index",
            "",
            f"- Total pages: `{len(pages)}`",
            f"- Last rebuilt: `{now_iso()}`",
            "",
            "## Coordination",
            "",
            "- [README.md](README.md)",
            "- [SCHEMA.md](SCHEMA.md)",
            "- [log.md](log.md)",
            "- [pages/home.md](pages/home.md)",
        ]

        if any(str(page.get("path") or "") == "01-method-wiki-index.md" for page in pages):
            lines.append("- [01-method-wiki-index.md](01-method-wiki-index.md)")

        for group_name in ("Sources", "Topics", "Entities", "Analyses", "Decisions", "Workflows", "Reference", "Raw", "Other"):
            entries = [
                page
                for page in sorted(page_groups[group_name], key=lambda item: (str(item.get("title") or ""), str(item.get("path") or "")))
                if str(page.get("path") or "") not in {"index.md", "README.md", "SCHEMA.md", "log.md", "pages/home.md"}
            ]
            if not entries:
                continue
            lines.extend(["", f"## {group_name}", ""])
            for page in entries:
                summary = str(page.get("summary") or "").strip()
                suffix = f" - {summary}" if summary else ""
                lines.append(f"- [{page.get('title') or page.get('path')}]({page.get('path')}){suffix}")

        index_body = "\n".join(lines)
        manifest_file = _runtime_manifest_file(root)
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        manifest_file.write_text(
            json.dumps(_build_runtime_manifest(root, pages), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self._write_page_text(normalized_wiki_id, "index.md", index_body)

    async def ingest_source_document(
        self,
        wiki_id: str,
        *,
        source_path: str,
        raw_text: str,
        title: str = "",
        project: str = "",
        source_kind: str = "document",
        document_id: Optional[str] = None,
        revision_id: Optional[str] = None,
        content_hash: Optional[str] = None,
        object_name: Optional[str] = None,
        imported_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_wiki_id = _slugify(wiki_id, "engine")
        await self.ensure_coordination_pages(normalized_wiki_id, create_if_missing=True)

        normalized_source_path = str(source_path or "").strip().replace("\\", "/").strip("/")
        safe_title = str(title or PurePosixPath(normalized_source_path).stem or normalized_source_path or "Untitled Source").strip()
        body_text = _normalize_multiline_text(raw_text)
        headings = _heading_candidates(body_text, limit=8)
        source_stem = _safe_source_page_stem(normalized_source_path, safe_title)
        imported_stamp = str(imported_at or now_iso()).strip()

        raw_manifest_base = normalized_source_path or source_stem
        if str(raw_manifest_base).lower().endswith(".md"):
            raw_page_path = _normalize_page_path(f"raw/processed/{raw_manifest_base}.source.md")
        else:
            raw_page_path = _normalize_page_path(f"raw/processed/{raw_manifest_base}.md")
        source_page_path = _normalize_page_path(f"pages/sources/{source_stem}.md")
        topic_page_path = _normalize_page_path(f"pages/topics/{source_stem}.md")

        raw_meta = {
            "title": f"Raw Source | {safe_title}",
            "description": f"Immutable source manifest for {safe_title}",
            "tags": ["raw", "source", str(project or "shared").strip() or "shared"],
            "source_path": normalized_source_path,
            "source_kind": source_kind,
            "project": project or None,
            "document_id": document_id,
            "revision_id": revision_id,
            "content_hash": content_hash,
            "imported_at": imported_stamp,
        }
        raw_body_lines = [
            "# Raw Source",
            "",
            f"- Title: `{safe_title}`",
            f"- Source path: `{normalized_source_path or safe_title}`",
            f"- Source kind: `{source_kind}`",
        ]
        if project:
            raw_body_lines.append(f"- Project: `{project}`")
        if document_id:
            raw_body_lines.append(f"- Document ID: `{document_id}`")
        if revision_id:
            raw_body_lines.append(f"- Revision ID: `{revision_id}`")
        raw_body_lines.extend([
            f"- Imported at: `{imported_stamp}`",
            "",
            "## Extracted Text",
            "",
            body_text or "_No extracted text available._",
        ])
        raw_page = self._write_page_text(normalized_wiki_id, raw_page_path, _render_markdown_page(raw_meta, "\n".join(raw_body_lines)))

        source_meta = {
            "title": safe_title,
            "description": f"Source summary for {safe_title}",
            "tags": ["source", "ingest", str(project or "shared").strip() or "shared"],
            "source_path": normalized_source_path,
            "source_manifest": raw_page_path,
            "sources": [raw_page_path],
            "project": project or None,
            "imported_at": imported_stamp,
        }
        source_body_lines = [
            f"# {safe_title}",
            "",
            "## Overview",
            "",
            f"- Source manifest: [{raw_page.get('title') or raw_page_path}]({raw_page_path})",
            f"- Imported at: `{imported_stamp}`",
        ]
        if headings:
            source_body_lines.extend(["", "## Key Headings", ""])
            for heading in headings:
                source_body_lines.append(f"- {heading}")
        if body_text:
            source_body_lines.extend(["", "## Excerpt", "", body_text[:2400]])
        source_page = self._write_page_text(normalized_wiki_id, source_page_path, _render_markdown_page(source_meta, "\n".join(source_body_lines)))

        existing_topic = await self.get_page(normalized_wiki_id, topic_page_path)
        existing_meta, existing_body = _read_frontmatter(str(existing_topic.get("content") or "")) if existing_topic else ({}, "")
        topic_sources = []
        if isinstance(existing_meta.get("sources"), list):
            topic_sources.extend(str(item or "").strip() for item in existing_meta.get("sources") if str(item or "").strip())
        topic_sources.extend([source_page_path, raw_page_path])
        topic_sources = list(dict.fromkeys(topic_sources))

        topic_meta = {
            "title": existing_meta.get("title") or safe_title,
            "description": existing_meta.get("description") or f"Curated topic page for {safe_title}",
            "tags": list(dict.fromkeys([
                *([str(item or "").strip() for item in existing_meta.get("tags") or []] if isinstance(existing_meta.get("tags"), list) else []),
                "topic",
                "ingest",
                str(project or "shared").strip() or "shared",
            ])),
            "sources": topic_sources,
            "last_ingested_at": imported_stamp,
            "project": project or None,
        }
        topic_sections = [
            f"# {topic_meta['title']}",
            "",
            "## Overview",
            "",
            existing_body.strip() if existing_body.strip() else f"This topic page is maintained from imported source material for `{safe_title}`.",
            "",
            "## Source Material",
            "",
            f"- [Source summary]({source_page_path})",
            f"- [Raw source manifest]({raw_page_path})",
        ]
        if headings:
            topic_sections.extend(["", "## Key Headings", ""])
            for heading in headings:
                topic_sections.append(f"- {heading}")
        topic_page = self._write_page_text(normalized_wiki_id, topic_page_path, _render_markdown_page(topic_meta, "\n".join(topic_sections)))

        index_page = await self.rebuild_index(normalized_wiki_id)
        await self.append_log(
            normalized_wiki_id,
            title=f"Ingest {safe_title}",
            body_lines=[
                f"Added raw manifest `{raw_page_path}`.",
                f"Updated source summary `{source_page_path}`.",
                f"Updated topic page `{topic_page_path}`.",
                "Rebuilt `index.md`.",
            ],
            kind="ingest",
        )
        return {
            "wiki_id": normalized_wiki_id,
            "raw_page": raw_page,
            "source_page": source_page,
            "topic_page": topic_page,
            "index_page": index_page,
        }

    async def write_query_page(
        self,
        wiki_id: str,
        *,
        query: str,
        answer: str,
        title: str = "",
        category: str = "analysis",
        page_path: str = "",
        source_paths: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        normalized_wiki_id = _slugify(wiki_id, "engine")
        await self.ensure_coordination_pages(normalized_wiki_id, create_if_missing=True)

        normalized_category = str(category or "analysis").strip().lower()
        base_dir = _WRITEBACK_CATEGORY_PATHS.get(normalized_category, _WRITEBACK_CATEGORY_PATHS["analysis"])
        resolved_title = str(title or query or "Saved Analysis").strip()
        resolved_path = str(page_path or "").strip()
        if not resolved_path:
            resolved_path = f"{base_dir}/{_slugify(resolved_title, normalized_category)}.md"

        normalized_sources = list(
            dict.fromkeys(
                str(item or "").strip()
                for item in (source_paths or [])
                if str(item or "").strip()
            )
        )
        meta = {
            "title": resolved_title,
            "description": f"Saved {normalized_category} derived from a query.",
            "tags": [normalized_category, "query", "saved-answer"],
            "derived_from_query": query,
            "sources": normalized_sources,
            "updated_at": now_iso(),
        }
        body_lines = [
            f"# {resolved_title}",
            "",
            "## Query",
            "",
            query or "_No query recorded._",
            "",
            "## Answer",
            "",
            _normalize_multiline_text(answer) or "_No answer recorded._",
        ]
        if normalized_sources:
            body_lines.extend(["", "## Sources", ""])
            for item in normalized_sources:
                body_lines.append(f"- [{item}]({item})")

        page = self._write_page_text(normalized_wiki_id, resolved_path, _render_markdown_page(meta, "\n".join(body_lines)))
        index_page = await self.rebuild_index(normalized_wiki_id)
        await self.append_log(
            normalized_wiki_id,
            title=f"Writeback {resolved_title}",
            body_lines=[
                f"Saved query-derived page `{page.get('path')}`.",
                "Rebuilt `index.md`.",
            ],
            kind="writeback",
        )
        return {"page": page, "index_page": index_page}

    async def lint_wiki(self, wiki_id: str, *, repair: bool = False) -> Dict[str, Any]:
        normalized_wiki_id = _slugify(wiki_id, "engine")
        coordination_status = await self.ensure_coordination_pages(normalized_wiki_id, create_if_missing=repair)
        pages = await self.list_pages(normalized_wiki_id)
        root = self._root(normalized_wiki_id)
        by_path = {str(page.get("path") or ""): page for page in pages}
        inbound_links: Dict[str, set[str]] = defaultdict(set)
        findings: List[Dict[str, Any]] = []

        for missing in coordination_status.get("missing_paths") or []:
            findings.append(
                {
                    "severity": "error",
                    "code": "missing_coordination_page",
                    "path": str(missing),
                    "message": f"Required coordination page `{missing}` is missing.",
                }
            )

        for page in pages:
            path = str(page.get("path") or "")
            content = str(page.get("content") or "")
            for raw_target in _link_targets(content):
                normalized_target = _resolve_relative_link_path(root, path, raw_target)
                if normalized_target and (root / normalized_target).exists():
                    inbound_links[normalized_target].add(path)
                    continue
                findings.append(
                    {
                        "severity": "warning",
                        "code": "broken_relative_link",
                        "path": path,
                        "target": normalized_target or str(raw_target or "").strip(),
                        "message": f"Broken relative link from `{path}` to `{normalized_target or str(raw_target or '').strip()}`.",
                    }
                )

        for page in pages:
            path = str(page.get("path") or "")
            content = str(page.get("content") or "")
            meta, _body = _read_frontmatter(content)
            kind = str(page.get("kind") or "")
            if kind in _CURATED_KINDS and path not in {"pages/home.md"} and not inbound_links.get(path):
                findings.append(
                    {
                        "severity": "warning",
                        "code": "orphan_page",
                        "path": path,
                        "message": f"Curated page `{path}` has no inbound wiki links.",
                    }
                )

            if kind in {"topic", "entity", "analysis", "decision", "workflow", "page"} and not _has_source_evidence(meta, content):
                findings.append(
                    {
                        "severity": "warning",
                        "code": "missing_provenance",
                        "path": path,
                        "message": f"Curated page `{path}` lacks explicit source evidence.",
                    }
                )

            if kind in {"topic", "analysis", "decision", "workflow", "entity"} and isinstance(meta.get("sources"), list):
                page_updated = str(page.get("updated_at") or "")
                for source_path in [str(item or "").strip() for item in meta.get("sources") or [] if str(item or "").strip()]:
                    source_page = by_path.get(source_path)
                    if source_page and str(source_page.get("updated_at") or "") > page_updated:
                        findings.append(
                            {
                                "severity": "info",
                                "code": "stale_source_reference",
                                "path": path,
                                "target": source_path,
                                "message": f"Source `{source_path}` is newer than curated page `{path}`.",
                            }
                        )

        repaired = False
        if repair:
            await self.rebuild_index(normalized_wiki_id)
            await self.append_log(
                normalized_wiki_id,
                title="Lint repair",
                body_lines=[
                    f"Ran wiki lint with repair. Findings: `{len(findings)}`.",
                    "Rebuilt `index.md`.",
                ],
                kind="lint",
            )
            repaired = True

        severity_counts: Dict[str, int] = defaultdict(int)
        for finding in findings:
            severity_counts[str(finding.get("severity") or "info")] += 1
        return {
            "wiki_id": normalized_wiki_id,
            "repair": repaired,
            "coordination_status": coordination_status,
            "finding_count": len(findings),
            "severity_counts": dict(severity_counts),
            "findings": findings,
        }

    async def get_context(self, wiki_id: str) -> Dict[str, Any]:
        coordination_status = await self.ensure_coordination_pages(wiki_id, create_if_missing=True)
        pages = await self.list_pages(wiki_id)
        coordination_paths = set(str(path or "") for path in coordination_status.get("present_paths") or [])
        coordination_pages = [page for page in pages if str(page.get("path") or "") in coordination_paths]
        return {
            "wiki": self._meta(wiki_id),
            "pages": pages,
            "coordination_pages": coordination_pages,
            "coordination_status": coordination_status,
        }

    async def search_pages(
        self,
        wiki_id: str,
        *,
        query: str,
        limit: int = 12,
        include_content: bool = False,
        kind: Optional[str] = None,
    ) -> Dict[str, Any]:
        await self.ensure_coordination_pages(wiki_id, create_if_missing=True)
        pages = await self.list_pages(wiki_id)
        filtered = [page for page in pages if not kind or str(page.get("kind") or "") == str(kind)]
        scored = []
        for page in filtered:
            score = _score_page(page, query)
            if str(query or "").strip() and score <= 0:
                continue
            scored.append((score, page))
        scored.sort(key=lambda item: (item[0], str(item[1].get("path") or "")), reverse=True)

        results = []
        for score, page in scored[: max(1, min(int(limit or 12), 50))]:
            item = {
                "path": page.get("path"),
                "title": page.get("title"),
                "kind": page.get("kind"),
                "summary": page.get("summary"),
                "score": score,
                "updated_at": page.get("updated_at"),
            }
            if include_content:
                item["content"] = page.get("content")
            else:
                item["excerpt"] = _build_excerpt(str(page.get("content") or ""), query)
            results.append(item)

        return {
            "wiki_id": _slugify(wiki_id, "engine"),
            "query": str(query or "").strip(),
            "total": len(scored),
            "results": results,
        }

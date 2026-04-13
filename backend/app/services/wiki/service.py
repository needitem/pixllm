import json
import re
from pathlib import PurePosixPath
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote

from ...utils.time import now_iso


def _slugify(value: str, fallback: str = "default") -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return fallback
    slug = re.sub(r"[^a-z0-9._-]+", "-", raw).strip("._-")
    return slug[:80] or fallback


def _normalize_page_path(value: str) -> str:
    raw = str(value or "").strip().replace("\\", "/").replace("./", "", 1)
    normalized = PurePosixPath(raw or "index.md").as_posix()
    if normalized.startswith("/") or normalized == ".." or normalized.startswith("../"):
        raise ValueError("page path must stay inside the wiki root")
    if not normalized.lower().endswith(".md"):
        normalized = f"{normalized}.md"
    return normalized


def _read_frontmatter(raw_text: str) -> tuple[Dict[str, Any], str]:
    text = str(raw_text or "")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    attributes: Dict[str, Any] = {}
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.+?)\s*$", line)
        if not match:
            continue
        attributes[str(match.group(1)).strip()] = str(match.group(2)).strip().strip("\"'")
    return attributes, text[end + 5 :]


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
    _meta, body = _read_frontmatter(content)
    lines = [line.strip() for line in str(body or "").splitlines() if line.strip()]
    if not lines:
        return ""
    return " ".join(lines[:4])[:240]


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
    if lowered.startswith("pages/topics/"):
        return "topic"
    if lowered.startswith("pages/entities/"):
        return "entity"
    if lowered.startswith("pages/decisions/"):
        return "decision"
    if lowered.startswith("raw/inbox/"):
        return "raw_inbox"
    if lowered.startswith("raw/processed/"):
        return "raw_processed"
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
        kind = str(page.get("kind") or "")
        priority = {
            "schema": 100,
            "index": 90,
            "log": 80,
            "home": 70,
        }
        return priority.get(kind, 10)

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
    return score


class WikiService:
    def __init__(self, redis):
        self.redis = redis
        self._wiki_index_key = "wiki:index"

    def _meta_key(self, wiki_id: str) -> str:
        return f"wiki:{wiki_id}:meta"

    def _page_index_key(self, wiki_id: str) -> str:
        return f"wiki:{wiki_id}:page_index"

    def _page_key(self, wiki_id: str, page_path: str) -> str:
        return f"wiki:{wiki_id}:page:{quote(page_path, safe='')}"

    async def _load_meta(self, wiki_id: str) -> Optional[Dict[str, Any]]:
        raw = await self.redis.get(self._meta_key(wiki_id))
        return json.loads(raw) if raw else None

    async def _save_meta(self, wiki_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        await self.redis.set(self._meta_key(wiki_id), json.dumps(payload))
        await self.redis.sadd(self._wiki_index_key, wiki_id)
        return payload

    async def list_wikis(self) -> List[Dict[str, Any]]:
        items = []
        wiki_ids = sorted(list(await self.redis.smembers(self._wiki_index_key)))
        for wiki_id in wiki_ids:
            meta = await self._load_meta(wiki_id)
            if meta:
                items.append(meta)
        return items

    async def list_pages(self, wiki_id: str) -> List[Dict[str, Any]]:
        normalized_wiki_id = _slugify(wiki_id)
        page_paths = sorted(list(await self.redis.smembers(self._page_index_key(normalized_wiki_id))))
        pages: List[Dict[str, Any]] = []
        for page_path in page_paths:
            page = await self.get_page(normalized_wiki_id, page_path)
            if page:
                pages.append(page)
        return pages

    async def get_page(self, wiki_id: str, page_path: str) -> Optional[Dict[str, Any]]:
        normalized_wiki_id = _slugify(wiki_id)
        normalized_path = _normalize_page_path(page_path)
        raw = await self.redis.get(self._page_key(normalized_wiki_id, normalized_path))
        return json.loads(raw) if raw else None

    async def upsert_page(
        self,
        wiki_id: str,
        page_path: str,
        content: str,
        *,
        title: Optional[str] = None,
        kind: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_wiki_id = _slugify(wiki_id)
        normalized_path = _normalize_page_path(page_path)
        now = now_iso()
        previous = await self.get_page(normalized_wiki_id, normalized_path)
        payload = {
            "wiki_id": normalized_wiki_id,
            "path": normalized_path,
            "title": str(title or _extract_title(normalized_path, content)).strip() or PurePosixPath(normalized_path).stem,
            "kind": str(kind or _infer_kind(normalized_path)).strip() or _infer_kind(normalized_path),
            "content": str(content or ""),
            "summary": _extract_summary(content),
            "updated_at": now,
            "updated_by": str(user_id or "").strip() or None,
            "created_at": str(previous.get("created_at") or now) if previous else now,
            "version": int(previous.get("version") or 0) + 1 if previous else 1,
        }
        await self.redis.set(self._page_key(normalized_wiki_id, normalized_path), json.dumps(payload))
        await self.redis.sadd(self._page_index_key(normalized_wiki_id), normalized_path)

        meta = await self._load_meta(normalized_wiki_id) or {
            "id": normalized_wiki_id,
            "name": normalized_wiki_id,
            "description": "",
            "created_at": now,
            "updated_at": now,
            "page_count": 0,
        }
        meta["updated_at"] = now
        meta["page_count"] = len(await self.redis.smembers(self._page_index_key(normalized_wiki_id)))
        await self._save_meta(normalized_wiki_id, meta)
        return payload

    def _bootstrap_templates(self, wiki_id: str, name: str = "", description: str = "") -> List[Dict[str, str]]:
        title = name or wiki_id
        overview = description or "Shared backend-managed workspace wiki."
        today = now_iso()[:10]
        return [
            {
                "path": "README.md",
                "kind": "readme",
                "content": "\n".join([
                    "# Shared Workspace Wiki",
                    "",
                    f"This backend-managed wiki is shared by clients connected to `{wiki_id}`.",
                    "",
                    "- `SCHEMA.md` defines the operating contract.",
                    "- `index.md` is the main navigation page.",
                    "- `log.md` records ingest, query-derived synthesis, and lint passes.",
                    "- `pages/` stores durable synthesized knowledge.",
                    "- `raw/` stores normalized source notes.",
                ]),
            },
            {
                "path": "SCHEMA.md",
                "kind": "schema",
                "content": "\n".join([
                    "# Shared Wiki Schema",
                    "",
                    f"- Wiki: `{title}`",
                    f"- Description: {overview}",
                    "",
                    "## Core Files",
                    "",
                    "- `index.md`: top-level catalog of important pages",
                    "- `log.md`: append-only operations log",
                    "- `pages/home.md`: high-level overview",
                    "",
                    "## Directory Contract",
                    "",
                    "- `raw/inbox/`: new source notes",
                    "- `raw/processed/`: already-ingested sources",
                    "- `pages/topics/`: topic syntheses",
                    "- `pages/entities/`: people, teams, systems, components",
                    "- `pages/decisions/`: decisions and tradeoffs",
                    "",
                    "## Agent Rules",
                    "",
                    "- Prefer updating an existing page before creating a near-duplicate.",
                    "- Keep markdown links relative.",
                    "- After substantive page edits, update `index.md` and append a matching entry to `log.md`.",
                    "- Use source notes as evidence and durable pages as synthesis.",
                ]),
            },
            {
                "path": "index.md",
                "kind": "index",
                "content": "\n".join([
                    "# Shared Wiki Index",
                    "",
                    "- [SCHEMA.md](SCHEMA.md)",
                    "- [log.md](log.md)",
                    "- [pages/home.md](pages/home.md)",
                    "- [raw/inbox/README.md](raw/inbox/README.md)",
                    "- [raw/processed/README.md](raw/processed/README.md)",
                    "",
                    "## Pages",
                    "",
                    "- [pages/home.md](pages/home.md) - workspace wiki overview",
                ]),
            },
            {
                "path": "log.md",
                "kind": "log",
                "content": "\n".join([
                    "# Shared Wiki Log",
                    "",
                    f"## [{today}] bootstrap | Initialize shared wiki",
                    "",
                    "- Created the backend-managed shared wiki scaffold.",
                ]),
            },
            {
                "path": "pages/home.md",
                "kind": "home",
                "content": "\n".join([
                    "---",
                    f"title: {title} Home",
                    f"description: {overview}",
                    "---",
                    "",
                    "# Home",
                    "",
                    "Use this page as the durable entry point for shared knowledge.",
                    "",
                    "Suggested contents:",
                    "- current project scope",
                    "- architecture map",
                    "- important systems and teams",
                    "- links to topic, entity, and decision pages",
                ]),
            },
            {
                "path": "pages/topics/README.md",
                "kind": "topic",
                "content": "# Topic Pages\n\nStore durable topic syntheses here.\n",
            },
            {
                "path": "pages/entities/README.md",
                "kind": "entity",
                "content": "# Entity Pages\n\nStore people, teams, services, and subsystems here.\n",
            },
            {
                "path": "pages/decisions/README.md",
                "kind": "decision",
                "content": "# Decision Pages\n\nCapture design and operational decisions here.\n",
            },
            {
                "path": "raw/inbox/README.md",
                "kind": "raw_inbox",
                "content": "# Raw Source Inbox\n\nAdd normalized source notes here before ingestion.\n",
            },
            {
                "path": "raw/processed/README.md",
                "kind": "raw_processed",
                "content": "# Processed Sources\n\nMove or copy ingested source notes here.\n",
            },
        ]

    async def bootstrap_wiki(
        self,
        wiki_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        overwrite: bool = False,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_wiki_id = _slugify(wiki_id)
        now = now_iso()
        meta = await self._load_meta(normalized_wiki_id)
        if not meta:
            meta = {
                "id": normalized_wiki_id,
                "name": str(name or normalized_wiki_id).strip() or normalized_wiki_id,
                "description": str(description or "").strip(),
                "created_at": now,
                "updated_at": now,
                "page_count": 0,
            }
        else:
            if name:
                meta["name"] = str(name).strip() or meta.get("name") or normalized_wiki_id
            if description is not None:
                meta["description"] = str(description).strip()
            meta["updated_at"] = now

        created_paths = []
        updated_paths = []
        skipped_paths = []
        for template in self._bootstrap_templates(normalized_wiki_id, meta.get("name"), meta.get("description")):
            existing = await self.get_page(normalized_wiki_id, template["path"])
            if existing and not overwrite:
                skipped_paths.append(template["path"])
                continue
            await self.upsert_page(
                normalized_wiki_id,
                template["path"],
                template["content"],
                title=None,
                kind=template["kind"],
                user_id=user_id,
            )
            if existing:
                updated_paths.append(template["path"])
            else:
                created_paths.append(template["path"])

        meta["page_count"] = len(await self.redis.smembers(self._page_index_key(normalized_wiki_id)))
        await self._save_meta(normalized_wiki_id, meta)
        return {
            "wiki": meta,
            "created_paths": created_paths,
            "updated_paths": updated_paths,
            "skipped_paths": skipped_paths,
        }

    async def append_log(
        self,
        wiki_id: str,
        *,
        title: str,
        body_lines: Iterable[str],
        kind: str = "update",
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        page = await self.get_page(wiki_id, "log.md")
        content = str(page.get("content") or "# Shared Wiki Log\n") if page else "# Shared Wiki Log\n"
        date = now_iso()[:10]
        lines = [f"## [{date}] {str(kind or 'update').strip()} | {str(title or 'Log entry').strip()}", ""]
        for body_line in body_lines:
            text = str(body_line or "").strip()
            if text:
                lines.append(f"- {text}")
        if len(lines) == 2:
            lines.append("- Updated shared wiki content.")
        lines.append("")
        next_content = f"{content.rstrip()}\n\n" + "\n".join(lines)
        return await self.upsert_page(wiki_id, "log.md", next_content, kind="log", user_id=user_id)

    async def get_context(self, wiki_id: str) -> Dict[str, Any]:
        normalized_wiki_id = _slugify(wiki_id)
        meta = await self._load_meta(normalized_wiki_id)
        if not meta:
            return {
                "wiki": None,
                "pages": [],
                "coordination_pages": [],
            }
        pages = await self.list_pages(normalized_wiki_id)
        coordination_paths = ["SCHEMA.md", "index.md", "log.md", "pages/home.md", "README.md"]
        coordination_pages = [page for page in pages if page.get("path") in coordination_paths]
        return {
            "wiki": meta,
            "pages": pages,
            "coordination_pages": coordination_pages,
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
        normalized_wiki_id = _slugify(wiki_id)
        pages = await self.list_pages(normalized_wiki_id)
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
            "wiki_id": normalized_wiki_id,
            "query": str(query or "").strip(),
            "total": len(scored),
            "results": results,
        }

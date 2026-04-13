import re
import time
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

from ... import config
from ...utils.time import now_iso

_BACKEND_ROOT = Path(__file__).resolve().parents[3]


def _slugify(value: str, fallback: str = "engine") -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return fallback
    slug = re.sub(r"[^a-z0-9._-]+", "-", raw).strip("._-")
    return slug[:80] or fallback


def wiki_parent_root() -> Path:
    return _BACKEND_ROOT / config.ORCHESTRATION_CONFIG_DIR / "wiki"


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
            "index": 90,
            "log": 80,
            "home": 70,
            "readme": 60,
            "method": 20,
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
                    "# Engine Shared Wiki",
                    "",
                    f"This shared wiki uses the existing engine reference wiki at `{wiki_id}` as its source of truth.",
                    "",
                    "- `SCHEMA.md` defines shared editing rules.",
                    "- `index.md` is the human-oriented navigation page.",
                    "- `01-method-wiki-index.md` is the generated method reference index.",
                    "- `log.md` records ingest, query-derived synthesis, and lint passes.",
                    "- `methods/` contains generated method reference pages.",
                ]),
            },
            {
                "path": "SCHEMA.md",
                "kind": "schema",
                "content": "\n".join([
                    "# Engine Wiki Schema",
                    "",
                    "- This shared wiki is the same backend engine reference wiki used by `company_reference_search`.",
                    "- Generated method reference pages live under `methods/`.",
                    "- Human-curated overview, synthesis, and workflow pages may live at the wiki root or under `pages/`.",
                    "",
                    "## Editing Rules",
                    "",
                    "- Do not hand-edit generated `methods/*.md` pages unless you are intentionally overriding the generator.",
                    "- Prefer adding curated context in `pages/` and linking to generated reference pages.",
                    "- Update `index.md` and `log.md` after substantive shared wiki edits.",
                    "- Keep relative markdown links stable.",
                ]),
            },
            {
                "path": "index.md",
                "kind": "index",
                "content": "\n".join([
                    "# Engine Wiki Index",
                    "",
                    "- [SCHEMA.md](SCHEMA.md)",
                    "- [log.md](log.md)",
                    "- [01-method-wiki-index.md](01-method-wiki-index.md)",
                    "",
                    "## Curated Pages",
                    "",
                    "- Add human-oriented overview, topic, and workflow pages here.",
                    "",
                    "## Generated Reference",
                    "",
                    "- [01-method-wiki-index.md](01-method-wiki-index.md) - generated method reference catalog",
                    "- [methods/](methods/) - generated method pages",
                ]),
            },
            {
                "path": "log.md",
                "kind": "log",
                "content": "\n".join([
                    "# Engine Wiki Log",
                    "",
                    f"## [{today}] bootstrap | Enable shared editing on engine wiki",
                    "",
                    "- Added shared coordination files on top of the engine reference wiki.",
                ]),
            },
            {
                "path": "pages/home.md",
                "kind": "home",
                "content": "\n".join([
                    "# Engine Wiki Home",
                    "",
                    "Use this page for curated overview, navigation, and shared context on top of the generated engine method reference.",
                ]),
            },
        ]

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
        del title, kind, user_id
        file_path = self._page_file(wiki_id, page_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(str(content or ""), encoding="utf-8")
        root = self._root(wiki_id)
        return _page_payload(root, file_path)

    async def bootstrap_wiki(
        self,
        wiki_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        overwrite: bool = False,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        del name, description, user_id
        root = self._root(wiki_id)
        root.mkdir(parents=True, exist_ok=True)
        created_paths: List[str] = []
        updated_paths: List[str] = []
        skipped_paths: List[str] = []
        for template in self._bootstrap_templates(_slugify(wiki_id, "engine")):
            file_path = self._page_file(wiki_id, template["path"])
            if file_path.exists() and not overwrite:
                skipped_paths.append(template["path"])
                continue
            existed = file_path.exists()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(template["content"], encoding="utf-8")
            if existed:
                updated_paths.append(template["path"])
            else:
                created_paths.append(template["path"])
        return {
            "wiki": self._meta(wiki_id),
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
        del user_id
        page = await self.get_page(wiki_id, "log.md")
        content = str(page.get("content") or "# Engine Wiki Log\n") if page else "# Engine Wiki Log\n"
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
        return await self.upsert_page(wiki_id, "log.md", next_content)

    async def get_context(self, wiki_id: str) -> Dict[str, Any]:
        root = self._root(wiki_id)
        if not root.exists():
            return {"wiki": None, "pages": [], "coordination_pages": []}
        pages = await self.list_pages(wiki_id)
        coordination_paths = {
            "README.md",
            "SCHEMA.md",
            "index.md",
            "log.md",
            "pages/home.md",
            "01-method-wiki-index.md",
        }
        coordination_pages = [page for page in pages if page.get("path") in coordination_paths]
        return {
            "wiki": self._meta(wiki_id),
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

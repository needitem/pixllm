from typing import Dict, Iterable, List, Optional

from .wiki_runtime import _OPTIONAL_COORDINATION_PATHS, _STRUCTURE_DIRS, _slugify, now_iso
from .wiki_templates import build_bootstrap_templates


class WikiServiceBootstrapMixin:
    def _bootstrap_templates(self, wiki_id: str) -> List[Dict[str, str]]:
        return build_bootstrap_templates(wiki_id)

    async def ensure_coordination_pages(
        self,
        wiki_id: str,
        *,
        create_if_missing: bool = True,
    ) -> Dict[str, object]:
        normalized_wiki_id = _slugify(wiki_id, "engine")
        root = self._root(normalized_wiki_id)
        root_existed = root.exists()
        if not root_existed and not create_if_missing:
            return self._coordination_status_payload(
                wiki_id=normalized_wiki_id,
                present_paths=[],
                missing_paths_before=self._required_coordination_paths(),
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
    ) -> Dict[str, object]:
        del title, kind
        normalized_wiki_id = _slugify(wiki_id, "engine")
        await self.ensure_coordination_pages(normalized_wiki_id, create_if_missing=True)
        page = self._write_page_text(normalized_wiki_id, page_path, content)
        page_kind = str(page.get("kind") or "")
        if page_kind not in {"index", "log", "schema", "readme"}:
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
    ) -> Dict[str, object]:
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


__all__ = ["WikiServiceBootstrapMixin"]

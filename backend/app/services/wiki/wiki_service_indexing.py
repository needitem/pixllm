from .wiki_runtime import *  # noqa: F401,F403


class WikiServiceIndexingMixin:
    async def rebuild_index(self, wiki_id: str) -> Dict[str, Any]:
        await self.ensure_coordination_pages(wiki_id, create_if_missing=True)
        normalized_wiki_id = _slugify(wiki_id, "engine")
        root = self._root(normalized_wiki_id)
        methods_index = (
            build_methods_index_from_raw_source(raw_source_root())
            if normalized_wiki_id == "engine"
            else []
        )
        source_manifest = (
            build_source_manifest_from_raw_source(raw_source_root(), methods_index)
            if normalized_wiki_id == "engine"
            else {}
        )
        if normalized_wiki_id == "engine":
            _sync_source_pages(
                root=root,
                source_manifest=source_manifest,
                raw_root_text=_raw_source_root_text(),
            )
            _sync_workflow_runtime_status(
                root=root,
                methods_index=methods_index,
                source_manifest=source_manifest,
            )

        pages = await self.list_pages(normalized_wiki_id)
        groups = {
            "Coordination": {"readme", "schema", "index", "log", "home"},
            "Sources": {"source"},
            "Topics": {"topic"},
            "Entities": {"entity"},
            "Analyses": {"analysis"},
            "Decisions": {"decision"},
            "Workflows": {"workflow"},
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

        for group_name in ("Sources", "Topics", "Entities", "Analyses", "Decisions", "Workflows", "Other"):
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
        methods_index_file = methods_index_file_for_root(root)
        methods_index_file.parent.mkdir(parents=True, exist_ok=True)
        methods_index_file.write_text(
            json.dumps(methods_index, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        source_manifest_file = source_manifest_file_for_root(root)
        source_manifest_file.parent.mkdir(parents=True, exist_ok=True)
        source_manifest_file.write_text(
            json.dumps(source_manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        manifest_file = _runtime_manifest_file(root)
        manifest_file.parent.mkdir(parents=True, exist_ok=True)
        manifest_file.write_text(
            json.dumps(_build_runtime_manifest(root, pages, methods_index), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self._write_page_text(normalized_wiki_id, "index.md", index_body)

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


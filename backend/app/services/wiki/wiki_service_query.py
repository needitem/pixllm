from ... import config
from .wiki_classifier import classify_workflow_family
from .wiki_runtime import *  # noqa: F401,F403


class WikiServiceQueryMixin:
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
        normalized_wiki_id = _slugify(wiki_id, "engine")
        root = self._root(normalized_wiki_id)
        normalized_kind = str(kind or "").strip()
        if normalized_kind == "method":
            results = build_method_page_results_for_root(
                root,
                query=str(query or "").strip(),
                limit=limit,
                include_content=include_content,
            )
            return {
                "wiki_id": normalized_wiki_id,
                "query": str(query or "").strip(),
                "total": len(results),
                "results": results,
            }

        normalized_query = str(query or "").strip()
        if normalized_query and normalized_kind in {"", "workflow"}:
            classified_families = []
            classifier_confidence = ""
            explicit_families = _query_explicit_family_hints(normalized_query)
            priority_families = _query_priority_family_hints(normalized_query)
            if config.WORKFLOW_CLASSIFIER_URL and config.WORKFLOW_CLASSIFIER_MODEL:
                manifest = _load_runtime_manifest_for_root(root)
                family_catalog = manifest.get("workflow_index") if isinstance(manifest.get("workflow_index"), list) else []
                classified = classify_workflow_family(normalized_query, family_catalog=family_catalog)
                primary_family = str(classified.get("primary_family") or "").strip()
                classifier_confidence = str(classified.get("confidence") or "").strip().lower()
                if primary_family and classifier_confidence in {"medium", "high"}:
                    classified_families.append(primary_family)
                if classifier_confidence == "high":
                    for family in classified.get("secondary_families") if isinstance(classified.get("secondary_families"), list) else []:
                        family_value = str(family or "").strip()
                        if family_value and family_value not in classified_families:
                            classified_families.append(family_value)
            preferred_families = list(explicit_families)
            for family in classified_families:
                if family not in preferred_families:
                    preferred_families.append(family)
            workflow_results = _route_workflow_results(
                root,
                query=normalized_query,
                limit=limit,
                include_content=include_content,
                preferred_families=preferred_families,
                priority_families=priority_families,
            )
            if workflow_results:
                return {
                    "wiki_id": normalized_wiki_id,
                    "query": normalized_query,
                    "total": len(workflow_results),
                    "results": workflow_results,
                }

        pages = await self.list_pages(wiki_id)
        filtered = [page for page in pages if not normalized_kind or str(page.get("kind") or "") == normalized_kind]
        matched: List[Tuple[Tuple[int, int, int, int, str], Dict[str, Any]]] = []
        for page in filtered:
            match_tuple = _page_match_tuple(page, normalized_query)
            if match_tuple is None:
                continue
            matched.append((match_tuple, page))
        matched.sort(key=lambda item: item[0])

        results = []
        for rank, (_match_tuple, page) in enumerate(matched[: max(1, min(int(limit or 12), 50))], start=1):
            item = {
                "path": page.get("path"),
                "title": page.get("title"),
                "kind": page.get("kind"),
                "summary": page.get("summary"),
                "rank": rank,
                "updated_at": page.get("updated_at"),
            }
            if include_content:
                item["content"] = page.get("content")
            else:
                item["excerpt"] = _build_excerpt(str(page.get("content") or ""), normalized_query)
            results.append(item)

        return {
            "wiki_id": normalized_wiki_id,
            "query": normalized_query,
            "total": len(matched),
            "results": results,
        }

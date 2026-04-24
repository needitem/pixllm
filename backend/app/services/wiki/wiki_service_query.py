from ... import config
from .wiki_classifier import classify_workflow_family
from .wiki_evidence_pack import build_workflow_evidence_pack
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
            manifest = _load_runtime_manifest_for_root(root)
            family_catalog = manifest.get("workflow_index") if isinstance(manifest.get("workflow_index"), list) else []
            manifest_rankings = _manifest_family_rankings(
                root,
                query=normalized_query,
                workflow_index=family_catalog,
                limit=6,
            )
            family_preferences = _manifest_family_preferences(
                root,
                query=normalized_query,
                workflow_index=family_catalog,
                rankings=manifest_rankings,
                limit=6,
            )
            preferred_families = [
                str(item or "").strip()
                for item in (family_preferences.get("preferred_families") if isinstance(family_preferences, dict) else [])
                if str(item or "").strip()
            ]
            priority_families = [
                str(item or "").strip()
                for item in (family_preferences.get("priority_families") if isinstance(family_preferences, dict) else [])
                if str(item or "").strip()
            ]
            classified_families = []
            classifier_confidence = ""
            top_score = int(manifest_rankings[0].get("score") or 0) if manifest_rankings else 0
            next_score = int(manifest_rankings[1].get("score") or 0) if len(manifest_rankings) > 1 else 0
            manifest_margin = top_score - next_score
            should_consult_classifier = bool(
                config.WORKFLOW_CLASSIFIER_URL
                and config.WORKFLOW_CLASSIFIER_MODEL
                and (
                    not preferred_families
                    or manifest_margin < _WORKFLOW_FAMILY_RANK_MARGIN
                )
            )
            if should_consult_classifier:
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
            for family in classified_families:
                if family not in preferred_families:
                    preferred_families.append(family)
                if not priority_families and classifier_confidence == "high" and family not in priority_families:
                    priority_families.append(family)
            workflow_results = _route_workflow_results(
                root,
                query=normalized_query,
                limit=limit,
                include_content=include_content,
                preferred_families=preferred_families,
                priority_families=priority_families,
            )
            if workflow_results:
                evidence_pack = build_workflow_evidence_pack(
                    root,
                    query=normalized_query,
                    workflow_result=workflow_results[0],
                )
                return {
                    "wiki_id": normalized_wiki_id,
                    "query": normalized_query,
                    "total": len(workflow_results),
                    "results": workflow_results,
                    **({"evidence_pack": evidence_pack} if evidence_pack else {}),
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

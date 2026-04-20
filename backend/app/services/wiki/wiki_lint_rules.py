from collections import defaultdict
from pathlib import PurePosixPath
from typing import Any, Dict, List

from .methods_index import load_methods_index_for_root
from .source_ingest import load_source_manifest_for_root
from .wiki_runtime import (
    _CURATED_KINDS,
    _SOURCE_ANCHOR_RE,
    _bundle_relation_expected_kind,
    _expand_manifest_match_tokens,
    _extract_knowledge_bundle,
    _extract_section_yaml,
    _has_source_evidence,
    _inline_page_targets,
    _link_targets,
    _normalize_fact_signature,
    _normalize_string_list,
    _page_search_terms,
    _read_frontmatter,
    _resolve_method_records_for_symbols,
    _resolve_relative_link_path,
    _slugify,
)


async def run_wiki_lint(service, wiki_id: str, *, repair: bool = False) -> Dict[str, Any]:
    normalized_wiki_id = _slugify(wiki_id, "engine")
    coordination_status = await service.ensure_coordination_pages(normalized_wiki_id, create_if_missing=repair)
    pages = await service.list_pages(normalized_wiki_id)
    root = service._root(normalized_wiki_id)
    methods_index = load_methods_index_for_root(root) if normalized_wiki_id == "engine" else []
    load_source_manifest_for_root(root) if normalized_wiki_id == "engine" else {}
    by_path = {str(page.get("path") or ""): page for page in pages}
    page_terms_by_path = {str(page.get("path") or ""): _page_search_terms(page) for page in pages}
    concept_page_paths = [str(page.get("path") or "") for page in pages if str(page.get("kind") or "") == "concept"]
    howto_page_paths = [str(page.get("path") or "") for page in pages if str(page.get("kind") or "") == "howto"]
    inbound_links: Dict[str, set[str]] = defaultdict(set)
    workflow_fact_claims: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    findings: List[Dict[str, Any]] = []

    for missing in coordination_status.get("missing_paths") or []:
        findings.append({"severity": "error", "code": "missing_coordination_page", "path": str(missing), "message": f"Required coordination page `{missing}` is missing."})

    for page in pages:
        path = str(page.get("path") or "")
        content = str(page.get("content") or "")
        kind = str(page.get("kind") or "")
        knowledge_bundle = _extract_knowledge_bundle(content) if kind == "workflow" else {"bundle_pages": []}
        for raw_target in _link_targets(content):
            normalized_target = _resolve_relative_link_path(root, path, raw_target)
            if normalized_target and (root / normalized_target).exists():
                inbound_links[normalized_target].add(path)
                continue
            findings.append({"severity": "warning", "code": "broken_relative_link", "path": path, "target": normalized_target or str(raw_target or "").strip(), "message": f"Broken relative link from `{path}` to `{normalized_target or str(raw_target or '').strip()}`."})
        for raw_target in _inline_page_targets(content):
            normalized_target = _resolve_relative_link_path(root, path, raw_target)
            if normalized_target and (root / normalized_target).exists():
                inbound_links[normalized_target].add(path)
        for item in knowledge_bundle.get("bundle_pages") if isinstance(knowledge_bundle.get("bundle_pages"), list) else []:
            if not isinstance(item, dict):
                continue
            raw_target = str(item.get("path") or "").strip()
            relation = str(item.get("relation") or "").strip() or "bundle_page"
            normalized_target = _resolve_relative_link_path(root, path, raw_target)
            if not normalized_target or not (root / normalized_target).exists():
                findings.append({"severity": "warning", "code": "broken_bundle_page", "path": path, "target": normalized_target or raw_target, "message": f"Workflow `{path}` references missing bundle page `{normalized_target or raw_target}`."})
                continue
            inbound_links[normalized_target].add(path)
            expected_kind = _bundle_relation_expected_kind(relation)
            target_page = by_path.get(normalized_target)
            if expected_kind and target_page and str(target_page.get("kind") or "") != expected_kind:
                findings.append({"severity": "warning", "code": "bundle_relation_kind_mismatch", "path": path, "target": normalized_target, "message": f"Workflow `{path}` expects bundle page `{normalized_target}` to be kind `{expected_kind}`."})

    for page in pages:
        path = str(page.get("path") or "")
        content = str(page.get("content") or "")
        meta, _body = _read_frontmatter(content)
        kind = str(page.get("kind") or "")
        if kind in _CURATED_KINDS and path not in {"pages/home.md"} and not inbound_links.get(path):
            findings.append({"severity": "warning", "code": "orphan_page", "path": path, "message": f"Curated page `{path}` has no inbound wiki links."})
        if kind in {"topic", "howto", "concept", "entity", "analysis", "decision", "workflow", "page"} and not _has_source_evidence(meta, content):
            findings.append({"severity": "warning", "code": "missing_provenance", "path": path, "message": f"Curated page `{path}` lacks explicit source evidence."})
        if kind in {"topic", "howto", "concept", "analysis", "decision", "workflow", "entity"} and isinstance(meta.get("sources"), list):
            page_updated = str(page.get("updated_at") or "")
            for source_path in [str(item or "").strip() for item in meta.get("sources") or [] if str(item or "").strip()]:
                source_page = by_path.get(source_path)
                if source_page and str(source_page.get("updated_at") or "") > page_updated:
                    findings.append({"severity": "info", "code": "stale_source_reference", "path": path, "target": source_path, "message": f"Source `{source_path}` is newer than curated page `{path}`."})
        if kind != "workflow":
            continue

        required_section = _extract_section_yaml(content, "Required Facts")
        knowledge_bundle = _extract_knowledge_bundle(content)
        required_symbols = _normalize_string_list(required_section.get("required_symbols"), limit=64)
        required_facts = required_section.get("required_facts") if isinstance(required_section.get("required_facts"), list) else []
        bundle_pages = knowledge_bundle.get("bundle_pages") if isinstance(knowledge_bundle.get("bundle_pages"), list) else []
        has_family_concept = any(str(item.get("relation") or "").strip() == "family_concept" for item in bundle_pages if isinstance(item, dict))
        if knowledge_bundle.get("concept_terms") and not has_family_concept:
            findings.append({"severity": "warning", "code": "missing_concept_bundle", "path": path, "message": f"Workflow `{path}` defines concept terms but has no `family_concept` bundle page."})

        concept_targets = [str(item.get("path") or "").strip() for item in bundle_pages if isinstance(item, dict) and str(item.get("relation") or "").strip() == "family_concept"]
        if knowledge_bundle.get("concept_terms") and concept_targets:
            concept_terms = _expand_manifest_match_tokens(knowledge_bundle.get("concept_terms") if isinstance(knowledge_bundle.get("concept_terms"), list) else [])
            covered = False
            for target in concept_targets or concept_page_paths:
                target_terms = page_terms_by_path.get(target, [])
                if any(term in target_terms for term in concept_terms if len(term) >= 4):
                    covered = True
                    break
            if not covered:
                findings.append({"severity": "warning", "code": "missing_concept_page", "path": path, "message": f"Workflow `{path}` concept terms are not clearly covered by bundled concept pages."})

        for item in required_facts:
            if not isinstance(item, dict):
                continue
            symbol = str(item.get("symbol") or "").strip()
            normalized_signature = _normalize_fact_signature(item)
            if symbol and normalized_signature:
                workflow_fact_claims[symbol].append({"path": path, "signature": normalized_signature})

        if normalized_wiki_id == "engine":
            for symbol in required_symbols:
                if not _resolve_method_records_for_symbols([symbol], methods_index):
                    findings.append({"severity": "warning", "code": "workflow_symbol_unresolved", "path": path, "target": symbol, "message": f"Workflow `{path}` requires symbol `{symbol}` that is missing from the runtime methods index."})

            workflow_updated_ts = 0.0
            try:
                workflow_updated_ts = (root / PurePosixPath(path).as_posix()).stat().st_mtime
            except Exception:
                workflow_updated_ts = 0.0

            for anchor in _SOURCE_ANCHOR_RE.findall(content):
                raw_anchor = str(anchor or "").strip()
                if not raw_anchor:
                    continue
                source_path = raw_anchor.split(":", 1)[0]
                if not source_path.startswith("Source/"):
                    continue
                resolved = service.raw_source_root() / PurePosixPath(source_path[len("Source/"):]).as_posix()
                if not resolved.exists():
                    findings.append({"severity": "warning", "code": "workflow_source_anchor_missing", "path": path, "target": source_path, "message": f"Workflow `{path}` references missing raw source anchor `{source_path}`."})
                    continue
                if workflow_updated_ts and resolved.stat().st_mtime > workflow_updated_ts:
                    findings.append({"severity": "info", "code": "workflow_source_newer_than_page", "path": path, "target": source_path, "message": f"Raw source `{source_path}` is newer than workflow `{path}`."})

    for symbol, claims in workflow_fact_claims.items():
        unique_signatures = sorted({str(item.get("signature") or "").strip() for item in claims if str(item.get("signature") or "").strip()})
        unique_paths = sorted({str(item.get("path") or "").strip() for item in claims if str(item.get("path") or "").strip()})
        if len(unique_signatures) > 1:
            findings.append({"severity": "info", "code": "workflow_fact_divergence", "path": unique_paths[0] if unique_paths else "", "target": symbol, "related_paths": unique_paths, "message": f"Workflow pages disagree on the exact required fact for `{symbol}`; clarify the intended overload or reconcile the contradiction."})

    repaired = False
    if repair:
        await service.rebuild_index(normalized_wiki_id)
        await service.append_log(normalized_wiki_id, title="Lint repair", body_lines=[f"Ran wiki lint with repair. Findings: `{len(findings)}`.", "Rebuilt `index.md`."], kind="lint")
        repaired = True

    severity_counts: Dict[str, int] = defaultdict(int)
    for finding in findings:
        severity_counts[str(finding.get("severity") or "info")] += 1
    return {"wiki_id": normalized_wiki_id, "repair": repaired, "coordination_status": coordination_status, "finding_count": len(findings), "severity_counts": dict(severity_counts), "findings": findings}


__all__ = ["run_wiki_lint"]

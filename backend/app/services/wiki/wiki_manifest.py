from .wiki_core import *  # noqa: F401,F403
from .wiki_bundle import *  # noqa: F401,F403
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
    root: Path,
    page: Dict[str, Any],
    methods_index: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    content = str(page.get("content") or "")
    current_path = str(page.get("path") or "").strip()
    meta, _body = _read_frontmatter(content)
    required_section = _extract_section_yaml(content, "Verified Facts")
    knowledge_bundle = _extract_knowledge_bundle(content)
    resolved_bundle_pages = _resolve_bundle_page_descriptors(
        root,
        current_path=current_path,
        bundle_pages=knowledge_bundle.get("bundle_pages") if isinstance(knowledge_bundle.get("bundle_pages"), list) else [],
    )
    frontmatter_symbols = _normalize_string_list(meta.get("symbols"))
    required_symbols = _normalize_string_list(required_section.get("required_symbols"))
    linked_records = _resolve_method_records_for_symbols(
        required_symbols,
        methods_index,
    )
    route_terms = _normalize_string_list(
        [
            page.get("title"),
            PurePosixPath(current_path).stem,
            required_section.get("workflow_family"),
            *(_normalize_string_list(meta.get("aliases"))),
            *(knowledge_bundle.get("concept_terms") if isinstance(knowledge_bundle.get("concept_terms"), list) else []),
            *[item.get("title") for item in resolved_bundle_pages if isinstance(item, dict)],
            *frontmatter_symbols,
            *required_symbols,
        ],
        limit=64,
    )
    semantic_terms = _normalize_string_list(
        [
            page.get("summary"),
            *(_normalize_string_list(meta.get("aliases"))),
            *(knowledge_bundle.get("concept_terms") if isinstance(knowledge_bundle.get("concept_terms"), list) else []),
            *[item.get("title") for item in resolved_bundle_pages if isinstance(item, dict)],
            *[item.get("summary") for item in resolved_bundle_pages if isinstance(item, dict)],
        ],
        limit=128,
    )
    return {
        "path": current_path,
        "title": str(page.get("title") or "").strip(),
        "summary": str(page.get("summary") or "").strip(),
        "aliases": _normalize_string_list(meta.get("aliases")),
        "symbols": frontmatter_symbols,
        "tags": _normalize_string_list(meta.get("tags")),
        "workflow_family": str(required_section.get("workflow_family") or "").strip(),
        "output_shape": str(required_section.get("output_shape") or "").strip(),
        "required_symbols": required_symbols,
        "verification_rules": _normalize_string_list(required_section.get("verification_rules")),
        "forbidden_answer_patterns": _normalize_string_list(required_section.get("forbidden_answer_patterns"), limit=64),
        "concept_terms": knowledge_bundle.get("concept_terms") if isinstance(knowledge_bundle.get("concept_terms"), list) else [],
        "routing_hints": knowledge_bundle.get("routing_hints") if isinstance(knowledge_bundle.get("routing_hints"), list) else [],
        "bundle_pages": [{"path": str(item.get("path") or "").strip(), "relation": str(item.get("relation") or "").strip() or "bundle_page"} for item in resolved_bundle_pages if isinstance(item, dict)],
        "bundle_page_titles": _normalize_string_list([item.get("title") for item in resolved_bundle_pages if isinstance(item, dict)], limit=32),
        "bundle_page_summaries": _normalize_string_list([item.get("summary") for item in resolved_bundle_pages if isinstance(item, dict)], limit=32),
        "semantic_terms": semantic_terms,
        "route_terms": route_terms,
        "linked_method_symbols": _normalize_string_list([record.get("qualified_symbol") for record in linked_records], limit=64),
        "source_anchors": _normalize_string_list(_SOURCE_ANCHOR_RE.findall(content), limit=64),
        "content": content,
    }


def _build_runtime_manifest(
    root: Path,
    pages: Sequence[Dict[str, Any]],
    methods_index: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    workflow_index = [
        _build_workflow_manifest_entry(root, page, methods_index)
        for page in pages or []
        if str(page.get("kind") or "") == "workflow"
    ]
    return {
        "version": 1,
        "wiki_id": root.name,
        "generated_at": now_iso(),
        "methods_index_path": METHODS_INDEX_RELATIVE_PATH,
        "source_manifest_path": SOURCE_MANIFEST_RELATIVE_PATH,
        "workflow_index": workflow_index,
    }


def _linked_modules_for_records(records: Sequence[Dict[str, Any]]) -> List[str]:
    output: List[str] = []
    seen = set()
    for record in records or []:
        for source_ref in record.get("source_refs") if isinstance(record.get("source_refs"), list) else []:
            source_path = str(source_ref.get("path") or "").strip()
            if not source_path.startswith("Source/"):
                continue
            parts = source_path.split("/")
            if len(parts) < 2:
                continue
            module = parts[1]
            key = module.lower()
            if key in seen:
                continue
            seen.add(key)
            output.append(module)
    return output


def _sync_source_pages(
    *,
    root: Path,
    source_manifest: Dict[str, Any],
        raw_root_text: str,
) -> List[str]:
    created_or_updated: List[str] = []
    module_entries = source_manifest.get("modules") if isinstance(source_manifest.get("modules"), list) else []
    expected_paths = {
        source_page_path_for_module(str(entry.get("module") or "").strip())
        for entry in module_entries
        if str(entry.get("module") or "").strip()
    }
    for entry in module_entries:
        module = str(entry.get("module") or "").strip()
        if not module:
            continue
        rel_path = source_page_path_for_module(module)
        file_path = root / PurePosixPath(rel_path).as_posix()
        content = render_source_page(entry, raw_root_text=raw_root_text)
        existing = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
        if existing != content:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            created_or_updated.append(rel_path)

    sources_dir = root / "pages" / "sources"
    if sources_dir.exists():
        for file_path in sources_dir.glob("*.md"):
            rel_path = file_path.relative_to(root).as_posix()
            if rel_path == "pages/sources/raw-source-root.md":
                continue
            if rel_path not in expected_paths:
                file_path.unlink()
                created_or_updated.append(rel_path)
    return created_or_updated


def _sync_workflow_runtime_status(
    *,
    root: Path,
    methods_index: Sequence[Dict[str, Any]],
    source_manifest: Dict[str, Any],
) -> List[str]:
    updated_paths: List[str] = []
    generated_at = str(source_manifest.get("generated_at") or now_iso())
    for file_path in sorted((root / "workflows").glob("*.md")):
        raw_text = file_path.read_text(encoding="utf-8")
        required_section = _extract_section_yaml(raw_text, "Verified Facts")
        required_symbols = _normalize_string_list(required_section.get("required_symbols"), limit=64)
        linked_records = _resolve_method_records_for_symbols(required_symbols, methods_index)
        missing_required_symbols = [
            symbol
            for symbol in required_symbols
            if not _resolve_method_records_for_symbols([symbol], methods_index)
        ]
        linked_modules = _linked_modules_for_records(linked_records)
        block = build_workflow_runtime_status_block(
            linked_modules=linked_modules,
            resolved_required_count=len(required_symbols) - len(missing_required_symbols),
            total_required_count=len(required_symbols),
            missing_required_symbols=missing_required_symbols,
            source_manifest_generated_at=generated_at,
        )
        updated = upsert_workflow_runtime_status(raw_text, block)
        if updated != raw_text:
            file_path.write_text(updated, encoding="utf-8")
            updated_paths.append(file_path.relative_to(root).as_posix())
    return updated_paths



__all__ = [name for name in globals() if not name.startswith("__")]

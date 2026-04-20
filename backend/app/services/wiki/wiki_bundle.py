from .wiki_core import *  # noqa: F401,F403
from .source_ingest import source_page_path_for_module

def _resolve_relative_link_path(root: Path, current_path: str, raw_target: str) -> Optional[str]:
    target = str(raw_target or "").strip()
    if not target:
        return None
    normalized_target = str(PurePosixPath(target)).replace("\\", "/").lstrip("/")
    if normalized_target and normalized_target != ".." and not normalized_target.startswith("../"):
        root_relative = (root / normalized_target).resolve()
        if root_relative.exists():
            return normalized_target
    candidate = PurePosixPath(PurePosixPath(current_path).parent, target).as_posix()
    normalized_candidate = str(PurePosixPath(candidate)).replace("\\", "/").lstrip("/")
    direct_path = (root / normalized_candidate).resolve()
    if direct_path.exists():
        try:
            return direct_path.relative_to(root.resolve()).as_posix()
        except Exception:
            return normalized_candidate
    try:
        normalized_page = _normalize_page_path(candidate)
    except ValueError:
        return None
    page_path = (root / normalized_page).resolve()
    if page_path.exists():
        return normalized_page
    return normalized_page


def _module_names_from_source_anchors(values: Sequence[str]) -> List[str]:
    output: List[str] = []
    seen = set()
    for raw_value in values or []:
        path_value = str(raw_value or "").strip()
        if not path_value.startswith("Source/"):
            continue
        parts = path_value.split("/")
        if len(parts) < 2:
            continue
        module_name = str(parts[1] or "").strip()
        key = module_name.lower()
        if not module_name or key in seen:
            continue
        seen.add(key)
        output.append(module_name)
    return output


def _collect_related_page_refs(
    root: Path,
    *,
    current_path: str,
    content: str,
    max_related_pages: int = 10,
) -> List[Dict[str, str]]:
    refs: List[Dict[str, str]] = []
    seen = set()

    def append_target(raw_target: str, relation: str) -> None:
        normalized_target = _resolve_relative_link_path(root, current_path, raw_target)
        if not normalized_target or normalized_target == current_path:
            return
        target_file = root / PurePosixPath(normalized_target).as_posix()
        if not target_file.exists() or not target_file.is_file():
            return
        key = normalized_target.lower()
        if key in seen:
            return
        seen.add(key)
        refs.append({"path": normalized_target, "relation": relation})

    knowledge_bundle = _extract_knowledge_bundle(content)
    has_curated_bundle = bool(knowledge_bundle.get("bundle_pages"))
    for item in knowledge_bundle.get("bundle_pages") if isinstance(knowledge_bundle.get("bundle_pages"), list) else []:
        if not isinstance(item, dict):
            continue
        append_target(str(item.get("path") or "").strip(), str(item.get("relation") or "").strip() or "bundle_page")

    if not has_curated_bundle:
        for raw_target in _link_targets(content):
            append_target(raw_target, "markdown_link")
        for raw_target in _inline_page_targets(content):
            append_target(raw_target, "inline_reference")

    for module_name in _module_names_from_source_anchors(_SOURCE_ANCHOR_RE.findall(content)):
        source_page = source_page_path_for_module(module_name)
        append_target(source_page, "source_module")

    return refs[: max(0, int(max_related_pages or 0))]


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


def _normalize_bundle_page_entries(
    value: Any,
    *,
    limit: int = 12,
) -> List[Dict[str, str]]:
    output: List[Dict[str, str]] = []
    seen = set()
    if not isinstance(value, list):
        return output
    for item in value:
        path_value = ""
        relation = "bundle_page"
        if isinstance(item, str):
            path_value = item
        elif isinstance(item, dict):
            path_value = str(item.get("path") or "").strip()
            relation = str(item.get("relation") or "").strip() or relation
        if not path_value:
            continue
        key = path_value.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append({"path": path_value, "relation": relation})
        if len(output) >= max(1, int(limit or 12)):
            break
    return output


def _normalize_routing_hint_entries(
    value: Any,
    *,
    limit: int = 16,
) -> List[Dict[str, List[str]]]:
    output: List[Dict[str, List[str]]] = []
    if not isinstance(value, list):
        return output
    for item in value:
        if not isinstance(item, dict):
            continue
        all_of = _normalize_string_list(item.get("all_of"), limit=8)
        any_of = _normalize_string_list(item.get("any_of"), limit=8)
        if not all_of and not any_of:
            continue
        output.append({"all_of": all_of, "any_of": any_of})
        if len(output) >= max(1, int(limit or 16)):
            break
    return output


def _extract_knowledge_bundle(content: str) -> Dict[str, Any]:
    bundle_section = _extract_section_yaml(content, "Knowledge Bundle")
    return {
        "concept_terms": _normalize_string_list(bundle_section.get("concept_terms"), limit=32),
        "bundle_pages": _normalize_bundle_page_entries(bundle_section.get("bundle_pages"), limit=12),
        "routing_hints": _normalize_routing_hint_entries(bundle_section.get("routing_hints"), limit=16),
    }


def _resolve_bundle_page_descriptors(
    root: Path,
    *,
    current_path: str,
    bundle_pages: Sequence[Dict[str, str]],
) -> List[Dict[str, str]]:
    output: List[Dict[str, str]] = []
    seen = set()
    for item in bundle_pages or []:
        if not isinstance(item, dict):
            continue
        raw_path = str(item.get("path") or "").strip()
        if not raw_path:
            continue
        normalized_path: Optional[str] = None
        if raw_path and raw_path != ".." and not raw_path.startswith("../"):
            try:
                normalized_path = _normalize_page_path(raw_path)
            except Exception:
                normalized_path = None
        if not normalized_path:
            normalized_path = _resolve_relative_link_path(root, current_path, raw_path)
        if not normalized_path:
            normalized_path = raw_path
        relation = str(item.get("relation") or "").strip() or "bundle_page"
        key = normalized_path.lower()
        if key in seen:
            continue
        seen.add(key)
        descriptor: Dict[str, str] = {"path": normalized_path, "relation": relation}
        target_file = root / PurePosixPath(normalized_path).as_posix()
        if target_file.exists() and target_file.is_file():
            raw_text = target_file.read_text(encoding="utf-8")
            descriptor["title"] = _extract_title(normalized_path, raw_text)
            descriptor["summary"] = _extract_summary(raw_text)
            descriptor["kind"] = _infer_kind(normalized_path)
        output.append(descriptor)
    return output


def _page_search_terms(page: Dict[str, Any]) -> List[str]:
    return _expand_manifest_match_tokens(
        [
            page.get("title"),
            page.get("summary"),
            str(page.get("path") or ""),
            str(page.get("content") or "")[:800],
        ]
    )


def _bundle_relation_expected_kind(relation: str) -> Optional[str]:
    normalized = str(relation or "").strip().lower()
    if normalized == "family_howto":
        return "howto"
    if normalized == "family_concept":
        return "concept"
    if normalized == "dependency_workflow":
        return "workflow"
    if normalized == "source_summary":
        return "source"
    return None


def _normalize_fact_signature(item: Dict[str, Any]) -> str:
    declarations: List[str] = []
    direct = str(item.get("declaration") or "").strip()
    if direct:
        declarations.append(direct)
    for candidate in item.get("declaration_candidates") if isinstance(item.get("declaration_candidates"), list) else []:
        if not isinstance(candidate, dict):
            continue
        declaration = str(candidate.get("declaration") or "").strip()
        if declaration:
            declarations.append(declaration)
    source_value = str(item.get("source") or "").strip()
    normalized_declarations = sorted({str(value or "").strip() for value in declarations if str(value or "").strip()})
    return " | ".join([*normalized_declarations, source_value] if source_value else normalized_declarations)

__all__ = [name for name in globals() if not name.startswith("__")]

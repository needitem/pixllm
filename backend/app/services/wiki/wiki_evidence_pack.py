import re
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .methods_index import build_method_page_results_for_root, load_methods_index_for_root, _read_source_text
from .wiki_bundle import _extract_section_yaml
from .wiki_core import _SOURCE_ANCHOR_RE, raw_source_root
from .wiki_manifest import _load_runtime_manifest_for_root, _resolve_method_records_for_symbols
from .wiki_pages import _page_payload


_METHOD_TOKEN_RE = re.compile(r"\b[A-Z][A-Za-z0-9_]*(?:\.[A-Z][A-Za-z0-9_]*)?\b")
_BACKTICK_RE = re.compile(r"`([^`]{2,160})`")
_NEGATIVE_METHOD_LINE_RE = re.compile(
    r"\bdo\s+not\b|\bdon't\b|\bmust\s+not\b|\bnever\b|확인\s*안\s*된|쓰지\s*않|넣지\s*않|하지\s*않|금지",
    re.IGNORECASE,
)

_WORKFLOW_CONTENT_LIMIT = 5600
_BUNDLE_CONTENT_LIMIT = 3600
_METHOD_CONTENT_LIMIT = 1200
_METHOD_SOURCE_SNIPPET_LIMIT = 2200
_MAX_BUNDLE_PAGES = 4
_MAX_METHOD_DECLARATIONS = 24
_MAX_SOURCE_SNIPPETS_PER_METHOD = 3
_SOURCE_TEXT_CACHE: Dict[str, Dict[str, Any]] = {}

_BUNDLE_RELATION_PRIORITY = {
    "family_howto": 0,
    "family_concept": 1,
    "source_summary": 2,
    "dependency_workflow": 3,
    "bundle_page": 4,
}


def _ascii_query_terms(query: str) -> List[str]:
    return [
        term.lower()
        for term in re.findall(r"[A-Za-z][A-Za-z0-9_]{1,}", str(query or ""))
        if len(term) >= 2
    ]


def _query_match_terms(query: str) -> List[str]:
    raw_terms = [
        term.lower()
        for term in re.findall(r"[A-Za-z][A-Za-z0-9_]{1,}|[가-힣]{2,}", str(query or ""))
    ]
    suffixes = ("으로", "에서", "에게", "의", "을", "를", "은", "는", "이", "가", "과", "와", "로")
    terms: List[str] = []
    for term in raw_terms:
        terms.append(term)
        for suffix in suffixes:
            if term.endswith(suffix) and len(term) > len(suffix) + 1:
                terms.append(term[: -len(suffix)])
                break
    return _unique_strings(terms, limit=24)


def _clip_text(value: str, limit: int) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return f"{text[: max(0, limit - 15)]}\n...[truncated]"


def _parse_start_line(line_range: str) -> int:
    match = re.match(r"^\s*(\d+)", str(line_range or ""))
    if not match:
        return 0
    return max(1, int(match.group(1) or 0))


def _source_file_for_ref(source_path: str) -> Optional[Path]:
    normalized = str(source_path or "").strip().replace("\\", "/")
    if not normalized.startswith("Source/"):
        return None
    relative = normalized[len("Source/") :]
    if not relative or relative.startswith("/") or relative == ".." or relative.startswith("../"):
        return None
    return raw_source_root() / PurePosixPath(relative).as_posix()


def _source_lines(target: Path) -> List[str]:
    try:
        stat = target.stat()
    except OSError:
        return []
    cache_key = target.resolve().as_posix()
    cached = _SOURCE_TEXT_CACHE.get(cache_key)
    if cached and cached.get("mtime") == stat.st_mtime:
        return cached.get("lines") if isinstance(cached.get("lines"), list) else []
    try:
        lines = _read_source_text(target).splitlines()
    except Exception:
        lines = []
    _SOURCE_TEXT_CACHE[cache_key] = {"mtime": stat.st_mtime, "lines": lines}
    if len(_SOURCE_TEXT_CACHE) > 64:
        _SOURCE_TEXT_CACHE.pop(next(iter(_SOURCE_TEXT_CACHE)), None)
    return lines


def _source_snippet_from_ref(source_ref: Dict[str, Any], *, role: str) -> Optional[Dict[str, Any]]:
    source_path = str(source_ref.get("path") or "").strip().replace("\\", "/")
    start_line = _parse_start_line(str(source_ref.get("line_range") or ""))
    target = _source_file_for_ref(source_path)
    if not target or start_line <= 0 or not target.exists() or not target.is_file():
        return None
    lines = _source_lines(target)
    if not lines:
        return None

    before = 6 if role == "declaration" else 0
    after = 8 if role == "declaration" else 32
    start_index = max(0, start_line - 1 - before)
    end_index = min(len(lines), start_line - 1 + after + 1)
    rendered = "\n".join(
        f"{index + 1}: {lines[index]}"
        for index in range(start_index, end_index)
    )
    return {
        "path": source_path,
        "line_range": f"{start_index + 1}-{end_index}",
        "role": role,
        "content": _clip_text(rendered, _METHOD_SOURCE_SNIPPET_LIMIT),
    }


def _source_example_snippet_for_record(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    member_name = str(record.get("member_name") or "").strip()
    source_refs = record.get("source_refs") if isinstance(record.get("source_refs"), list) else []
    first_ref = source_refs[0] if source_refs and isinstance(source_refs[0], dict) else {}
    source_path = str(first_ref.get("path") or "").strip().replace("\\", "/")
    declaration_line = _parse_start_line(str(first_ref.get("line_range") or ""))
    if not member_name or declaration_line <= 0:
        return None
    target = _source_file_for_ref(source_path)
    if not target or not target.exists() or not target.is_file():
        return None
    lines = _source_lines(target)
    if not lines:
        return None

    call_pattern = re.compile(rf"\b{re.escape(member_name)}\s*\(")
    search_start = max(0, declaration_line - 220)
    search_end = min(len(lines), declaration_line + 80)
    candidates: List[int] = []
    for index in range(search_start, search_end):
        line = lines[index]
        if not call_pattern.search(line):
            continue
        # Prefer examples in XML doc comments; skip the actual declaration line.
        if index == declaration_line - 1:
            continue
        stripped = line.strip()
        if not stripped.startswith("///") and index < declaration_line - 1:
            continue
        candidates.append(index)

    if not candidates:
        return None
    before_declaration = [index for index in candidates if index < declaration_line - 1]
    match_index = before_declaration[-1] if before_declaration else candidates[0]
    start_index = max(0, match_index - 8)
    end_index = min(len(lines), match_index + 22)
    rendered = "\n".join(
        f"{index + 1}: {lines[index]}"
        for index in range(start_index, end_index)
    )
    return {
        "path": source_path,
        "line_range": f"{start_index + 1}-{end_index}",
        "role": "example",
        "content": _clip_text(rendered, _METHOD_SOURCE_SNIPPET_LIMIT),
    }


def _source_snippets_for_record(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    snippets: List[Dict[str, Any]] = []
    source_refs = record.get("source_refs") if isinstance(record.get("source_refs"), list) else []
    first_ref = source_refs[0] if source_refs and isinstance(source_refs[0], dict) else {}
    declaration = _source_snippet_from_ref(first_ref, role="declaration") if first_ref else None
    if declaration:
        snippets.append(declaration)
    example = _source_example_snippet_for_record(record)
    if example and not any(
        snippet.get("path") == example.get("path") and snippet.get("line_range") == example.get("line_range")
        for snippet in snippets
    ):
        snippets.append(example)
    for source_ref in source_refs[1:]:
        if len(snippets) >= _MAX_SOURCE_SNIPPETS_PER_METHOD:
            break
        if not isinstance(source_ref, dict):
            continue
        snippet = _source_snippet_from_ref(source_ref, role="implementation")
        if snippet:
            snippets.append(snippet)
    return snippets


def _unique_strings(values: Iterable[str], *, limit: int = 64) -> List[str]:
    output: List[str] = []
    seen = set()
    for value in values or []:
        normalized = str(value or "").strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(normalized)
        if len(output) >= max(1, int(limit or 1)):
            break
    return output


def _workflow_entry_for_path(root: Path, workflow_path: str) -> Dict[str, Any]:
    normalized_path = str(workflow_path or "").strip()
    if not normalized_path:
        return {}
    manifest = _load_runtime_manifest_for_root(root)
    for entry in manifest.get("workflow_index") if isinstance(manifest.get("workflow_index"), list) else []:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("path") or "").strip().lower() == normalized_path.lower():
            return entry
    return {}


def _workflow_page_payload(root: Path, workflow_path: str) -> Dict[str, Any]:
    normalized_path = str(workflow_path or "").strip()
    if not normalized_path:
        return {}
    target = root / PurePosixPath(normalized_path).as_posix()
    if not target.exists() or not target.is_file():
        return {}
    return _page_payload(root, target, include_related=False)


def _extract_method_candidate_tokens(*values: str, limit: int = 48) -> List[str]:
    candidates: List[str] = []
    for raw_value in values:
        text = str(raw_value or "")
        if not text:
            continue
        for line in text.splitlines():
            if _NEGATIVE_METHOD_LINE_RE.search(line):
                continue
            for backtick_value in _BACKTICK_RE.findall(line):
                candidates.extend(_METHOD_TOKEN_RE.findall(backtick_value))
            candidates.extend(_METHOD_TOKEN_RE.findall(line))
    return _unique_strings(candidates, limit=limit)


def _extract_relevant_line_method_tokens(query: str, content: str, *, limit: int = 32) -> List[str]:
    terms = _query_match_terms(query)
    if not terms:
        return []
    candidates: List[str] = []
    for line in str(content or "").splitlines():
        if _NEGATIVE_METHOD_LINE_RE.search(line):
            continue
        lowered = line.lower()
        compact_lowered = re.sub(r"\s+", "", lowered)
        if not any(term and (term in lowered or re.sub(r"\s+", "", term) in compact_lowered) for term in terms):
            continue
        for backtick_value in _BACKTICK_RE.findall(line):
            candidates.extend(_METHOD_TOKEN_RE.findall(backtick_value))
        candidates.extend(_METHOD_TOKEN_RE.findall(line))
    return _unique_strings(candidates, limit=limit)


def _prioritize_method_tokens(tokens: Sequence[str], query: str) -> List[str]:
    query_terms = _ascii_query_terms(query)
    if not query_terms:
        return list(tokens or [])

    indexed = []
    for index, token in enumerate(tokens or []):
        lowered = str(token or "").lower()
        score = sum(1 for term in query_terms if term in lowered)
        indexed.append((score, index, token))
    indexed.sort(key=lambda item: (-item[0], item[1]))
    return [token for _score, _index, token in indexed]


def _method_payload_from_record(record: Dict[str, Any], *, reason: str) -> Dict[str, Any]:
    text = str(record.get("text") or "")
    qualified_symbol = str(record.get("qualified_symbol") or "").strip()
    declaration = str(record.get("declaration") or "").strip()
    raw_source_refs = record.get("source_refs") if isinstance(record.get("source_refs"), list) else []
    source_refs = [
        {
            "path": str(item.get("path") or "").strip(),
            "line_range": str(item.get("line_range") or "").strip(),
        }
        for item in raw_source_refs
        if isinstance(item, dict) and str(item.get("path") or "").strip()
    ]
    declaration_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().lower().startswith(("- declaration:", "- implementation:"))
    ]
    source_snippets = _source_snippets_for_record(record)
    content_lines = [text]
    if declaration:
        content_lines.append(f"- Verified declaration: `{declaration}`")
    for snippet in source_snippets:
        content_lines.append(
            "\n".join(
                [
                    f"- Source snippet ({snippet.get('role')}): `{snippet.get('path')}:{snippet.get('line_range')}`",
                    "```",
                    str(snippet.get("content") or ""),
                    "```",
                ]
            )
        )
    return {
        "symbol": qualified_symbol,
        "member_name": str(record.get("member_name") or "").strip(),
        "type_name": str(record.get("type_name") or "").strip(),
        "title": str(record.get("heading_path") or qualified_symbol).strip(),
        "path": f".runtime/methods_index.json#{qualified_symbol}" if qualified_symbol else ".runtime/methods_index.json",
        "reason": reason,
        "declaration": declaration,
        "source_refs": source_refs,
        "source_snippets": source_snippets,
        "declarations": declaration_lines[:4],
        "content": _clip_text("\n".join(content_lines), _METHOD_CONTENT_LIMIT),
    }


def _method_payload_from_search_result(
    result: Dict[str, Any],
    *,
    reason: str,
    methods_index: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    path_value = str(result.get("path") or "").strip()
    symbol = path_value.split("#", 1)[1].strip() if "#" in path_value else ""
    records = _resolve_method_records_for_symbols([symbol], methods_index)
    if records:
        payload = _method_payload_from_record(records[0], reason=reason)
        payload["score"] = int(result.get("score") or 0)
        return payload
    text = str(result.get("content") or result.get("excerpt") or "")
    declaration_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().lower().startswith(("- declaration:", "- implementation:"))
    ]
    return {
        "symbol": symbol,
        "title": str(result.get("title") or symbol).strip(),
        "path": path_value,
        "reason": reason,
        "score": int(result.get("score") or 0),
        "declaration": "",
        "source_refs": [],
        "source_snippets": [],
        "declarations": declaration_lines[:4],
        "content": _clip_text(text, _METHOD_CONTENT_LIMIT),
    }


def _append_method_payload(
    output: List[Dict[str, Any]],
    seen: set,
    payload: Dict[str, Any],
) -> None:
    symbol = str(payload.get("symbol") or "").strip()
    declaration = str(payload.get("declaration") or "").strip()
    path_value = str(payload.get("path") or "").strip()
    key = f"{symbol}\n{declaration}".strip().lower() if declaration else (symbol or path_value).lower()
    if not key or key in seen:
        return
    seen.add(key)
    output.append(payload)


def _build_method_declarations(
    root: Path,
    *,
    query: str,
    workflow_content: str,
    bundle_content: str = "",
    required_symbols: Sequence[str],
    linked_method_symbols: Sequence[str],
    verification_rules: Sequence[str],
) -> List[Dict[str, Any]]:
    methods_index = load_methods_index_for_root(root)
    if not methods_index:
        return []

    output: List[Dict[str, Any]] = []
    seen = set()
    curated_source_backed = any(
        str(rule or "").strip().lower() == "treat_this_page_as_source_backed_family_overview"
        for rule in verification_rules or []
    )
    if curated_source_backed:
        for record in _resolve_method_records_for_symbols(
            _unique_strings([*required_symbols, *linked_method_symbols], limit=80),
            methods_index,
        ):
            _append_method_payload(output, seen, _method_payload_from_record(record, reason="workflow_symbol"))
            if len(output) >= _MAX_METHOD_DECLARATIONS:
                return output
        return output

    method_context = "\n\n".join(
        part
        for part in (str(workflow_content or ""), str(bundle_content or ""))
        if part.strip()
    )
    candidate_tokens = _prioritize_method_tokens(
        _unique_strings(
            [
                *_extract_relevant_line_method_tokens(query, method_context, limit=32),
                *_extract_method_candidate_tokens(query, method_context, limit=48),
            ],
            limit=64,
        ),
        query,
    )
    for record in _resolve_method_records_for_symbols(candidate_tokens, methods_index):
        _append_method_payload(output, seen, _method_payload_from_record(record, reason="workflow_candidate"))
        if len(output) >= _MAX_METHOD_DECLARATIONS:
            return output

    for record in _resolve_method_records_for_symbols(
        _unique_strings([*required_symbols, *linked_method_symbols], limit=80),
        methods_index,
    ):
        _append_method_payload(output, seen, _method_payload_from_record(record, reason="workflow_symbol"))
        if len(output) >= _MAX_METHOD_DECLARATIONS:
            return output

    search_terms = _unique_strings([query, *candidate_tokens[:12]], limit=14)
    for term in search_terms:
        if len(output) >= _MAX_METHOD_DECLARATIONS:
            break
        for result in build_method_page_results_for_root(root, query=term, limit=3, include_content=True):
            _append_method_payload(
                output,
                seen,
                _method_payload_from_search_result(
                    result,
                    reason="method_search",
                    methods_index=methods_index,
                ),
            )
            if len(output) >= _MAX_METHOD_DECLARATIONS:
                break
    return output


def _bundle_page_payloads(root: Path, bundle_pages: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ordered = sorted(
        [item for item in bundle_pages or [] if isinstance(item, dict)],
        key=lambda item: (
            _BUNDLE_RELATION_PRIORITY.get(str(item.get("relation") or "").strip(), 99),
            str(item.get("path") or ""),
        ),
    )
    payloads: List[Dict[str, Any]] = []
    seen = set()
    for item in ordered:
        path_value = str(item.get("path") or "").strip()
        if not path_value:
            continue
        key = path_value.lower()
        if key in seen:
            continue
        seen.add(key)
        target = root / PurePosixPath(path_value).as_posix()
        if not target.exists() or not target.is_file():
            continue
        page = _page_payload(root, target, include_related=False)
        payloads.append(
            {
                "path": str(page.get("path") or path_value),
                "title": str(page.get("title") or ""),
                "kind": str(page.get("kind") or ""),
                "relation": str(item.get("relation") or "bundle_page"),
                "summary": str(page.get("summary") or ""),
                "content": _clip_text(str(page.get("content") or ""), _BUNDLE_CONTENT_LIMIT),
            }
        )
        if len(payloads) >= _MAX_BUNDLE_PAGES:
            break
    return payloads


def _build_answer_grounding(method_declarations: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    facts: List[Dict[str, Any]] = []
    for item in method_declarations or []:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol") or "").strip()
        declaration = str(item.get("declaration") or "").strip()
        source_refs = item.get("source_refs") if isinstance(item.get("source_refs"), list) else []
        source_snippets = item.get("source_snippets") if isinstance(item.get("source_snippets"), list) else []
        if not symbol and not declaration:
            continue
        facts.append(
            {
                "symbol": symbol,
                "declaration": declaration,
                "source_refs": [
                    {
                        "path": str(source_ref.get("path") or "").strip(),
                        "line_range": str(source_ref.get("line_range") or "").strip(),
                    }
                    for source_ref in source_refs
                    if isinstance(source_ref, dict) and str(source_ref.get("path") or "").strip()
                ],
                "source_snippets": [
                    {
                        "path": str(snippet.get("path") or "").strip(),
                        "line_range": str(snippet.get("line_range") or "").strip(),
                        "role": str(snippet.get("role") or "").strip(),
                        "content": _clip_text(str(snippet.get("content") or ""), 1400),
                    }
                    for snippet in source_snippets[:2]
                    if isinstance(snippet, dict) and (str(snippet.get("path") or "").strip() or str(snippet.get("content") or "").strip())
                ],
            }
        )
        if len(facts) >= 12:
            break

    return {
        "must": [
            "Verify API signatures, ref/out/% parameters, overloads, enum literals, and property-vs-method form from declarations.",
            "Use source snippets as the highest-priority evidence for concrete side effects and implementation behavior.",
        ],
        "should": [
            "Use workflow/howto/concept pages for the ordered procedure and API family choice.",
            "For .NET DLL usage, keep source declarations as evidence but write usage examples in C# unless the user explicitly asks for another language.",
            "Translate [OutAttribute] Type^% parameters to C# out arguments, and non-out Type^% object parameters to C# ref arguments.",
            "If workflow prose conflicts with declarations or source snippets, follow the code evidence.",
        ],
        "may": [
            "Use normal SDK reasoning for high-level explanation and sample structure when it does not change verified API signatures or source-backed behavior.",
            "Mark only genuinely missing or risky details as unverified; do not overuse unverified wording for ordinary procedural glue.",
        ],
        "facts": facts,
    }


def build_workflow_evidence_pack(
    root: Path,
    *,
    query: str = "",
    workflow_path: str = "",
    workflow_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    resolved_path = str(workflow_path or (workflow_result or {}).get("path") or "").strip()
    if not resolved_path:
        return {}

    entry = _workflow_entry_for_path(root, resolved_path)
    page = _workflow_page_payload(root, resolved_path)
    workflow_content = str(page.get("content") or entry.get("content") or (workflow_result or {}).get("content") or "")
    if not workflow_content:
        return {}

    verified_facts = _extract_section_yaml(workflow_content, "Verified Facts")
    entry_required_symbols = entry.get("required_symbols") if isinstance(entry.get("required_symbols"), list) else []
    fact_required_symbols = verified_facts.get("required_symbols") if isinstance(verified_facts.get("required_symbols"), list) else []
    required_symbols = _unique_strings([*fact_required_symbols, *entry_required_symbols], limit=80)
    entry_verification_rules = entry.get("verification_rules") if isinstance(entry.get("verification_rules"), list) else []
    fact_verification_rules = verified_facts.get("verification_rules") if isinstance(verified_facts.get("verification_rules"), list) else []
    verification_rules = _unique_strings([*fact_verification_rules, *entry_verification_rules], limit=32)
    bundle_pages = _bundle_page_payloads(
        root,
        entry.get("bundle_pages") if isinstance(entry.get("bundle_pages"), list) else [],
    )
    method_declarations = _build_method_declarations(
        root,
        query=str(query or ""),
        workflow_content=workflow_content,
        bundle_content="\n\n".join(
            str(item.get("content") or "")
            for item in bundle_pages[:_MAX_BUNDLE_PAGES]
            if isinstance(item, dict)
        ),
        required_symbols=required_symbols,
        linked_method_symbols=entry.get("linked_method_symbols") if isinstance(entry.get("linked_method_symbols"), list) else [],
        verification_rules=verification_rules,
    )
    source_anchors = _unique_strings(
        [
            *_SOURCE_ANCHOR_RE.findall(workflow_content),
            *[
                anchor
                for page_item in bundle_pages
                for anchor in _SOURCE_ANCHOR_RE.findall(str(page_item.get("content") or ""))
            ],
            *[
                anchor
                for method_item in method_declarations
                for anchor in _SOURCE_ANCHOR_RE.findall(str(method_item.get("content") or ""))
            ],
            *[
                f"{snippet.get('path')}:{_parse_start_line(str(snippet.get('line_range') or ''))}"
                for method_item in method_declarations
                for snippet in (method_item.get("source_snippets") if isinstance(method_item.get("source_snippets"), list) else [])
                if isinstance(snippet, dict) and str(snippet.get("path") or "").strip()
            ],
        ],
        limit=48,
    )

    workflow_family = str(entry.get("workflow_family") or verified_facts.get("workflow_family") or "").strip()
    return {
        "version": 1,
        "query": str(query or "").strip(),
        "workflow": {
            "path": resolved_path,
            "title": str(entry.get("title") or page.get("title") or (workflow_result or {}).get("title") or ""),
            "kind": "workflow",
            "summary": str(entry.get("summary") or page.get("summary") or (workflow_result or {}).get("summary") or ""),
            "workflow_family": workflow_family,
            "output_shape": str(entry.get("output_shape") or verified_facts.get("output_shape") or "").strip(),
            "required_symbols": required_symbols,
            "verification_rules": verification_rules,
            "content": _clip_text(workflow_content, _WORKFLOW_CONTENT_LIMIT),
        },
        "bundle_pages": bundle_pages,
        "method_declarations": method_declarations,
        "answer_grounding": _build_answer_grounding(method_declarations),
        "source_anchors": source_anchors,
        "answer_rules": [
            "Use the workflow as the routing authority.",
            "Use bundled pages for procedural context.",
            "Must verify API signatures, ref/out/% parameters, overloads, enum literals, and property-vs-method form from declarations.",
            "Should use source snippets for concrete side effects and implementation behavior.",
            "For .NET DLL usage, keep declarations as source evidence but answer with C# examples by default; translate [OutAttribute] by-ref parameters to C# out and non-out object by-ref parameters to C# ref.",
            "May use normal SDK reasoning for high-level procedure and sample structure when it does not change verified signatures or source-backed behavior.",
            "If a required signature or risky behavior is absent from this pack, state only that specific detail as unverified.",
        ],
    }


__all__ = ["build_workflow_evidence_pack"]

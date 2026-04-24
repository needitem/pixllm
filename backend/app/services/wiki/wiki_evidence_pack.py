import re
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .methods_index import build_method_page_results_for_root, load_methods_index_for_root
from .wiki_bundle import _extract_section_yaml
from .wiki_core import _SOURCE_ANCHOR_RE
from .wiki_manifest import _load_runtime_manifest_for_root, _resolve_method_records_for_symbols
from .wiki_pages import _page_payload


_METHOD_TOKEN_RE = re.compile(r"\b[A-Z][A-Za-z0-9_]*(?:\.[A-Z][A-Za-z0-9_]*)?\b")
_BACKTICK_RE = re.compile(r"`([^`]{2,160})`")

_WORKFLOW_CONTENT_LIMIT = 5600
_BUNDLE_CONTENT_LIMIT = 1600
_METHOD_CONTENT_LIMIT = 1200
_MAX_BUNDLE_PAGES = 4
_MAX_METHOD_DECLARATIONS = 14

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
        for backtick_value in _BACKTICK_RE.findall(text):
            candidates.extend(_METHOD_TOKEN_RE.findall(backtick_value))
        candidates.extend(_METHOD_TOKEN_RE.findall(text))
    return _unique_strings(candidates, limit=limit)


def _extract_relevant_line_method_tokens(query: str, content: str, *, limit: int = 32) -> List[str]:
    terms = _query_match_terms(query)
    if not terms:
        return []
    candidates: List[str] = []
    for line in str(content or "").splitlines():
        lowered = line.lower()
        if not any(term and term in lowered for term in terms):
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
    declaration_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().lower().startswith(("- declaration:", "- implementation:"))
    ]
    return {
        "symbol": qualified_symbol,
        "member_name": str(record.get("member_name") or "").strip(),
        "type_name": str(record.get("type_name") or "").strip(),
        "title": str(record.get("heading_path") or qualified_symbol).strip(),
        "path": f".runtime/methods_index.json#{qualified_symbol}" if qualified_symbol else ".runtime/methods_index.json",
        "reason": reason,
        "declarations": declaration_lines[:4],
        "content": _clip_text(text, _METHOD_CONTENT_LIMIT),
    }


def _method_payload_from_search_result(result: Dict[str, Any], *, reason: str) -> Dict[str, Any]:
    path_value = str(result.get("path") or "").strip()
    symbol = path_value.split("#", 1)[1].strip() if "#" in path_value else ""
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
        "declarations": declaration_lines[:4],
        "content": _clip_text(text, _METHOD_CONTENT_LIMIT),
    }


def _append_method_payload(
    output: List[Dict[str, Any]],
    seen: set,
    payload: Dict[str, Any],
) -> None:
    symbol = str(payload.get("symbol") or "").strip()
    path_value = str(payload.get("path") or "").strip()
    key = (symbol or path_value).lower()
    if not key or key in seen:
        return
    seen.add(key)
    output.append(payload)


def _build_method_declarations(
    root: Path,
    *,
    query: str,
    workflow_content: str,
    required_symbols: Sequence[str],
    linked_method_symbols: Sequence[str],
) -> List[Dict[str, Any]]:
    methods_index = load_methods_index_for_root(root)
    if not methods_index:
        return []

    output: List[Dict[str, Any]] = []
    seen = set()
    candidate_tokens = _prioritize_method_tokens(
        _unique_strings(
            [
                *_extract_relevant_line_method_tokens(query, workflow_content, limit=32),
                *_extract_method_candidate_tokens(query, workflow_content, limit=48),
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
            _append_method_payload(output, seen, _method_payload_from_search_result(result, reason="method_search"))
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
    workflow_content = str(entry.get("content") or page.get("content") or (workflow_result or {}).get("content") or "")
    if not workflow_content:
        return {}

    verified_facts = _extract_section_yaml(workflow_content, "Verified Facts")
    required_symbols = _unique_strings(
        entry.get("required_symbols") if isinstance(entry.get("required_symbols"), list) else verified_facts.get("required_symbols"),
        limit=80,
    )
    verification_rules = _unique_strings(
        entry.get("verification_rules") if isinstance(entry.get("verification_rules"), list) else verified_facts.get("verification_rules"),
        limit=32,
    )
    bundle_pages = _bundle_page_payloads(
        root,
        entry.get("bundle_pages") if isinstance(entry.get("bundle_pages"), list) else [],
    )
    method_declarations = _build_method_declarations(
        root,
        query=str(query or ""),
        workflow_content=workflow_content,
        required_symbols=required_symbols,
        linked_method_symbols=entry.get("linked_method_symbols") if isinstance(entry.get("linked_method_symbols"), list) else [],
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
        "source_anchors": source_anchors,
        "answer_rules": [
            "Use the workflow as the routing authority.",
            "Use bundled pages for procedural context.",
            "Use method_declarations as the signature allowlist for code examples.",
            "If required signatures are absent from this pack, state the missing detail as unverified.",
        ],
    }


__all__ = ["build_workflow_evidence_pack"]

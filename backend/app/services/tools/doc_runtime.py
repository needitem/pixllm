import asyncio
import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ... import config, wiki_config
from ..retrieval.service import run_retrieval
from ...core.policy import SecurityPolicy
from .access import register_code_search, register_doc_search, resolve_tool_user_context
from .code_runtime import read_code_lines
from .query_terms import extract_symbol_query_candidates
from .query_strategy import expand_line_window, parse_line_range
from .support import build_citations, clamp_int, dedupe_doc_items, normalize_doc_item, qdrant_point_id
from .wiki_runtime import search_wiki

logger = logging.getLogger(__name__)

_WIKI_SOURCE_REF_RE = re.compile(r"\b(Source/[^`:\s]+):(\d+)(?:-(\d+))?\b")
_BACKTICK_TOKEN_RE = re.compile(r"`([^`]+)`")
_TYPE_LIKE_RE = re.compile(r"^(?:[A-Z][A-Za-z0-9_]*|e[A-Z][A-Za-z0-9_]*)$")
_LOOKUP_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")
_LOOKUP_QUALIFIED_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)[.:]([A-Za-z_][A-Za-z0-9_]*)\b")
_SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
_METHODS_DOC_STEM_PREFIX = "Methods_T_"
_QUERY_FILLER_TOKENS = {
    "api",
    "bool",
    "csharp",
    "cpp",
    "code",
    "declaration",
    "example",
    "examples",
    "method",
    "methods",
    "path",
    "property",
    "ref",
    "signature",
    "string",
    "top",
}
_LOOKUP_HINT_TOKENS = {
    "api",
    "constructor",
    "declaration",
    "enum",
    "member",
    "method",
    "overload",
    "property",
    "ref",
    "signature",
}


def _normalize_wiki_id(value: str) -> str:
    raw = str(value or "").strip().lower()
    return raw or "engine"


def _wiki_root(wiki_id: str = "engine") -> Path:
    return Path(__file__).resolve().parents[3] / config.WIKI_PROFILE_DIR / "wiki" / _normalize_wiki_id(wiki_id)


def _manifest_file(wiki_id: str = "engine") -> Path:
    return _wiki_root(wiki_id) / ".runtime" / "manifest.json"


def _manifest_signature(wiki_id: str = "engine") -> str:
    path = _manifest_file(wiki_id)
    if not path.exists():
        return "missing"
    stat = path.stat()
    return f"{stat.st_mtime_ns}:{stat.st_size}"


@lru_cache(maxsize=16)
def _read_wiki_manifest_cached(wiki_id: str, signature: str) -> Dict[str, Any]:
    del signature
    path = _manifest_file(wiki_id)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _load_wiki_manifest(wiki_id: str = "engine") -> Dict[str, Any]:
    normalized_wiki_id = _normalize_wiki_id(wiki_id)
    return _read_wiki_manifest_cached(normalized_wiki_id, _manifest_signature(normalized_wiki_id))


def _normalize_lookup_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())


def _load_methods_api_index(wiki_id: str = "engine") -> List[Dict[str, Any]]:
    manifest = _load_wiki_manifest(wiki_id)
    records = manifest.get("methods_index")
    if isinstance(records, list) and records:
        return [record for record in records if isinstance(record, dict)]
    return _load_methods_api_index_legacy(_normalize_wiki_id(wiki_id))


@lru_cache(maxsize=16)
def _load_methods_lookup_bundle(wiki_id: str, signature: str) -> Dict[str, Any]:
    del signature
    records = _load_methods_api_index(wiki_id)
    type_lookup: Dict[str, str] = {}
    record_lookup: Dict[str, Dict[str, Any]] = {}
    for record in records:
        type_name = str(record.get("type_name") or "")
        qualified_type = str(record.get("qualified_type") or "")
        qualified_symbol = str(record.get("qualified_symbol") or "").strip()
        normalized_type_name = _normalize_lookup_token(type_name)
        normalized_qualified_type = _normalize_lookup_token(qualified_type)
        if normalized_type_name:
            type_lookup[normalized_type_name] = type_name
        if normalized_qualified_type:
            type_lookup[normalized_qualified_type] = qualified_type
        if qualified_symbol:
            record_lookup[qualified_symbol] = record
    return {
        "records": records,
        "type_lookup": type_lookup,
        "record_lookup": record_lookup,
    }


def _methods_lookup_bundle(wiki_id: str = "engine") -> Dict[str, Any]:
    normalized_wiki_id = _normalize_wiki_id(wiki_id)
    return _load_methods_lookup_bundle(normalized_wiki_id, _manifest_signature(normalized_wiki_id))


@lru_cache(maxsize=8)
def _load_methods_api_index_legacy(wiki_id: str = "engine") -> List[Dict[str, Any]]:
    root = _wiki_root(wiki_id) / "methods"
    if not root.exists():
        return []

    records: List[Dict[str, Any]] = []
    engine_wiki_root = root.parent
    for path in sorted(root.glob(f"{_METHODS_DOC_STEM_PREFIX}*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        lines = text.splitlines()
        section_starts = [
            index
            for index, raw_line in enumerate(lines)
            if _SECTION_HEADING_RE.match(str(raw_line or ""))
        ]
        stem = path.stem
        if not stem.startswith(_METHODS_DOC_STEM_PREFIX):
            continue
        qualified_type = stem[len(_METHODS_DOC_STEM_PREFIX) :].replace("_", ".")
        type_name = qualified_type.split(".")[-1]
        relative_doc_path = path.relative_to(engine_wiki_root).as_posix()

        for section_index, start in enumerate(section_starts):
            match = _SECTION_HEADING_RE.match(lines[start])
            member_name = str(match.group(1) if match else "").strip()
            if not member_name or member_name.lower() == "overview":
                continue
            end = section_starts[section_index + 1] if section_index + 1 < len(section_starts) else len(lines)
            section_lines = lines[start:end]
            section_text = "\n".join(section_lines).strip()
            if not section_text:
                continue
            source_refs = [
                {
                    "path": str(ref_match.group(1) or "").strip().replace("\\", "/"),
                    "line_range": (
                        f"{max(1, int(ref_match.group(2) or 1))}-{max(max(1, int(ref_match.group(2) or 1)), int(ref_match.group(3) or ref_match.group(2) or 1))}"
                    ),
                }
                for ref_match in _WIKI_SOURCE_REF_RE.finditer(section_text)
            ]
            records.append(
                {
                    "qualified_type": qualified_type,
                    "type_name": type_name,
                    "member_name": member_name,
                    "qualified_symbol": f"{qualified_type}.{member_name}",
                    "doc_path": relative_doc_path,
                    "heading_path": f"{qualified_type} Methods > {member_name}",
                    "text": section_text,
                    "source_refs": source_refs,
                }
            )
    return records


def _extract_lookup_targets(
    query: str,
    records: Sequence[Dict[str, Any]],
    type_lookup: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    source = str(query or "").strip()
    source = re.sub(r"(?<![A-Za-z0-9_])C\s*#", " csharp ", source, flags=re.IGNORECASE)
    source = re.sub(r"(?<![A-Za-z0-9_])C\s*\+\+", " cpp ", source, flags=re.IGNORECASE)
    lowered = source.lower()
    if type_lookup is None:
        type_lookup = {}
        for record in records or []:
            type_lookup[_normalize_lookup_token(record.get("type_name"))] = str(record.get("type_name") or "")
            type_lookup[_normalize_lookup_token(record.get("qualified_type"))] = str(record.get("qualified_type") or "")

    type_candidates: List[str] = []
    member_candidates: List[str] = []
    seen_types = set()
    seen_members = set()
    explicit_pairs = []

    for match in _LOOKUP_QUALIFIED_RE.finditer(source):
        explicit_pairs.append((str(match.group(1) or "").strip(), str(match.group(2) or "").strip()))

    raw_tokens = [str(token or "").strip() for token in _LOOKUP_TOKEN_RE.findall(source)]
    symbol_tokens = extract_symbol_query_candidates(source, max_candidates=8)
    for type_name, member_name in explicit_pairs:
        normalized_type = _normalize_lookup_token(type_name)
        normalized_member = _normalize_lookup_token(member_name)
        resolved_type = type_lookup.get(normalized_type, type_name)
        if resolved_type and normalized_type not in seen_types:
            type_candidates.append(resolved_type.split(".")[-1])
            seen_types.add(normalized_type)
        if member_name and normalized_member not in seen_members:
            member_candidates.append(member_name)
            seen_members.add(normalized_member)

    lookup_hints = any(token in lowered for token in _LOOKUP_HINT_TOKENS)
    for token in [*symbol_tokens, *raw_tokens]:
        normalized = _normalize_lookup_token(token)
        if not normalized or normalized in _QUERY_FILLER_TOKENS:
            continue
        resolved_type = type_lookup.get(normalized, "")
        if resolved_type:
            if normalized not in seen_types:
                type_candidates.append(resolved_type.split(".")[-1])
                seen_types.add(normalized)
            continue
        if normalized not in seen_members and (
            lookup_hints
            or explicit_pairs
            or _TYPE_LIKE_RE.match(token)
        ):
            member_candidates.append(token)
            seen_members.add(normalized)

    is_specific_lookup = bool(
        explicit_pairs
        or (lookup_hints and type_candidates and member_candidates)
        or (type_candidates and member_candidates and len(type_candidates) + len(member_candidates) <= 4)
    )
    return {
        "type_candidates": type_candidates[:4],
        "member_candidates": member_candidates[:6],
        "is_specific_lookup": is_specific_lookup,
    }


def _build_lookup_source_excerpt(record: Dict[str, Any], *, section_index: int) -> Dict[str, Any]:
    symbols = [
        str(record.get("type_name") or ""),
        str(record.get("member_name") or ""),
        str(record.get("qualified_symbol") or ""),
    ]
    return {
        "chunk_id": f"wiki:{record.get('doc_path')}#section-{section_index}",
        "doc_id": f"wiki:{record.get('doc_path')}",
        "source_url": str(record.get("doc_path") or ""),
        "file_path": str(record.get("doc_path") or ""),
        "heading_path": str(record.get("heading_path") or ""),
        "paragraph_range": f"section:{section_index}",
        "text": str(record.get("text") or ""),
        "truncated": False,
        "title": f"{record.get('qualified_type')} Methods",
        "symbols": [item for item in symbols if item],
        "tags": ["engine", "methods", "api"],
    }


def _load_workflow_manifest_index(wiki_id: str = "engine") -> List[Dict[str, Any]]:
    manifest = _load_wiki_manifest(wiki_id)
    records = manifest.get("workflow_index")
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, dict)]


@lru_cache(maxsize=16)
def _load_workflow_lookup_bundle(wiki_id: str, signature: str) -> Dict[str, Any]:
    del signature
    records = _load_workflow_manifest_index(wiki_id)
    path_lookup = {
        str(record.get("path") or "").strip(): record
        for record in records
        if str(record.get("path") or "").strip()
    }
    search_entries = []
    for record in records:
        search_entries.append(
            {
                "record": record,
                "title_key": _normalize_lookup_token(record.get("title")),
                "alias_keys": [_normalize_lookup_token(alias) for alias in record.get("aliases") or []],
                "symbol_keys": [
                    _normalize_lookup_token(symbol)
                    for symbol in [*(record.get("symbols") or []), *(record.get("required_symbols") or [])]
                ],
                "term_keys": [_normalize_lookup_token(term) for term in record.get("route_terms") or []],
            }
        )
    return {
        "records": records,
        "path_lookup": path_lookup,
        "search_entries": search_entries,
        "generated_at": str(_load_wiki_manifest(wiki_id).get("generated_at") or ""),
    }


def _workflow_lookup_bundle(wiki_id: str = "engine") -> Dict[str, Any]:
    normalized_wiki_id = _normalize_wiki_id(wiki_id)
    return _load_workflow_lookup_bundle(normalized_wiki_id, _manifest_signature(normalized_wiki_id))


def _score_manifest_workflow(query: str, record: Dict[str, Any]) -> int:
    normalized_query = _normalize_lookup_token(query)
    if not normalized_query:
        return 0
    score = 0
    title_key = _normalize_lookup_token(record.get("title"))
    if title_key and title_key in normalized_query:
        score += 24
    for alias in record.get("aliases") or []:
        alias_key = _normalize_lookup_token(alias)
        if alias_key and alias_key in normalized_query:
            score += 18
    for symbol in [*(record.get("symbols") or []), *(record.get("required_symbols") or [])]:
        symbol_key = _normalize_lookup_token(symbol)
        if symbol_key and symbol_key in normalized_query:
            score += 22
    for term in record.get("route_terms") or []:
        term_key = _normalize_lookup_token(term)
        if term_key and term_key in normalized_query:
            score += 8
    return score


def _build_manifest_workflow_rows(
    *,
    query: str,
    wiki_id: str,
    top_k: int,
    max_chars: int,
    workflow_bundle: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    workflow_bundle = workflow_bundle or _workflow_lookup_bundle(wiki_id)
    workflow_records = workflow_bundle.get("records") if isinstance(workflow_bundle.get("records"), list) else []
    if not workflow_records:
        return []
    generated_at = str(workflow_bundle.get("generated_at") or "")
    ranked = [
        (entry.get("record"), _score_manifest_workflow(query, entry.get("record") or {}))
        for entry in (workflow_bundle.get("search_entries") or [])
    ]
    ranked = [item for item in ranked if item[1] > 0]
    ranked.sort(key=lambda item: item[1], reverse=True)
    results: List[Dict[str, Any]] = []
    for index, (record, score) in enumerate(ranked[: max(1, min(top_k, 4))], start=1):
        text = str(record.get("content") or "")[:max(400, clamp_int(max_chars, 400, 12000))]
        title = str(record.get("title") or record.get("path") or "").strip()
        path = str(record.get("path") or "").strip()
        symbols = _unique_preserve_order([
            *(record.get("symbols") or []),
            *(record.get("required_symbols") or []),
        ])
        results.append(
            {
                "chunk_id": f"wiki:{wiki_id}:{path}#manifest",
                "doc_id": f"wiki:{wiki_id}:{path}",
                "wiki_id": wiki_id,
                "source_url": f"{wiki_id}/{path}",
                "file_path": path,
                "heading_path": f"{title} > Manifest",
                "paragraph_range": "manifest",
                "text": text,
                "truncated": len(text) < len(str(record.get("content") or "")),
                "updated_at": generated_at,
                "source_kind": "wiki",
                "document_type": "wiki",
                "score": score,
                "title": title,
                "symbols": symbols,
                "tags": [str(item or "").strip() for item in record.get("tags") or [] if str(item or "").strip()],
            }
        )
    return results


def _match_manifest_method_records(
    *,
    query: str,
    workflow_rows: Sequence[Dict[str, Any]],
    wiki_id: str,
    max_records: int,
    workflow_bundle: Optional[Dict[str, Any]] = None,
    methods_bundle: Optional[Dict[str, Any]] = None,
    query_targets: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    methods_bundle = methods_bundle or _methods_lookup_bundle(wiki_id)
    methods_index = methods_bundle.get("records") or []
    if not methods_index:
        return []
    workflow_lookup = (workflow_bundle or _workflow_lookup_bundle(wiki_id)).get("path_lookup") or {}
    record_lookup = methods_bundle.get("record_lookup") or {}
    query_targets = query_targets or _extract_lookup_targets(
        query,
        methods_index,
        methods_bundle.get("type_lookup") or {},
    )
    explicit_type_keys = {
        _normalize_lookup_token(item)
        for item in query_targets.get("type_candidates") or []
        if _normalize_lookup_token(item)
    }
    explicit_member_keys = {
        _normalize_lookup_token(item)
        for item in query_targets.get("member_candidates") or []
        if _normalize_lookup_token(item)
    }
    explicit_lookup = bool(query_targets.get("is_specific_lookup"))

    selected: List[Dict[str, Any]] = []
    seen = set()
    for row in workflow_rows or []:
        workflow_path = _source_file_path(row)
        manifest_entry = workflow_lookup.get(workflow_path)
        if not manifest_entry:
            continue
        for qualified_symbol in manifest_entry.get("linked_method_symbols") or []:
            record = record_lookup.get(str(qualified_symbol or "").strip())
            if not record:
                continue
            type_key = _normalize_lookup_token(record.get("type_name") or record.get("qualified_type"))
            member_key = _normalize_lookup_token(record.get("member_name"))
            if explicit_lookup and explicit_type_keys and type_key not in explicit_type_keys:
                continue
            if explicit_lookup and explicit_member_keys and member_key not in explicit_member_keys:
                continue
            lookup_key = str(record.get("qualified_symbol") or "").strip().lower()
            if not lookup_key or lookup_key in seen:
                continue
            seen.add(lookup_key)
            selected.append(record)
            if len(selected) >= max_records:
                return selected
    return selected


def _symbol_type_and_member(symbol: str) -> Tuple[str, str]:
    raw = str(symbol or "").strip().replace("::", ".")
    if not raw:
        return "", ""
    parts = [part for part in raw.split(".") if part]
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    return "", parts[-1] if parts else ""


def _matches_query_targets(symbol: str, query_targets: Dict[str, Any]) -> bool:
    type_name, member_name = _symbol_type_and_member(symbol)
    normalized_type = _normalize_lookup_token(type_name)
    normalized_member = _normalize_lookup_token(member_name)
    query_type_keys = {
        _normalize_lookup_token(item)
        for item in query_targets.get("type_candidates") or []
        if _normalize_lookup_token(item)
    }
    query_member_keys = {
        _normalize_lookup_token(item)
        for item in query_targets.get("member_candidates") or []
        if _normalize_lookup_token(item)
    }
    if query_type_keys and normalized_type not in query_type_keys:
        return False
    if query_member_keys and normalized_member not in query_member_keys:
        return False
    return bool(query_type_keys or query_member_keys)


def _build_manifest_slot_bundle(
    *,
    query: str,
    workflow_rows: Sequence[Dict[str, Any]],
    method_records: Sequence[Dict[str, Any]],
    wiki_id: str,
    workflow_bundle: Optional[Dict[str, Any]] = None,
    methods_bundle: Optional[Dict[str, Any]] = None,
    query_targets: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    workflow_lookup = (workflow_bundle or _workflow_lookup_bundle(wiki_id)).get("path_lookup") or {}
    workflow_entries = [
        workflow_lookup.get(_source_file_path(row))
        for row in workflow_rows or []
        if workflow_lookup.get(_source_file_path(row))
    ]
    workflow_entries = [entry for entry in workflow_entries if isinstance(entry, dict)]
    if not workflow_entries:
        return None

    methods_bundle = methods_bundle or _methods_lookup_bundle(wiki_id)
    methods_index = methods_bundle.get("records") or []
    query_targets = query_targets or _extract_lookup_targets(query, methods_index, methods_bundle.get("type_lookup") or {}) if methods_index else {
        "type_candidates": [],
        "member_candidates": [],
        "is_specific_lookup": False,
    }
    explicit_lookup = bool(query_targets.get("is_specific_lookup"))

    required_slots: List[str] = ["workflow"]
    filled_slots = {"workflow"} if workflow_rows else set()
    selected_symbols: List[str] = []
    if explicit_lookup:
        for entry in workflow_entries:
            fact_symbols = _unique_preserve_order([
                str(item.get("symbol") or "").strip()
                for item in entry.get("required_facts") or []
                if isinstance(item, dict) and str(item.get("symbol") or "").strip()
            ])
            linked_symbols = _unique_preserve_order([
                *fact_symbols,
                *(entry.get("linked_method_symbols") or []),
                *(entry.get("required_symbols") or []),
            ])
            selected_symbols.extend(
                symbol for symbol in linked_symbols
                if _matches_query_targets(symbol, query_targets)
            )

    selected_symbols = _unique_preserve_order(selected_symbols)
    if selected_symbols:
        required_slots.extend([f"symbol:{symbol}" for symbol in selected_symbols])
    else:
        required_slots.append("method_or_anchor")

    matched_symbols = {
        _normalize_lookup_token(record.get("qualified_symbol") or "")
        for record in method_records or []
        if _normalize_lookup_token(record.get("qualified_symbol") or "")
    }
    matched_symbols.update(
        _normalize_lookup_token(f"{record.get('type_name')}.{record.get('member_name')}")
        for record in method_records or []
        if str(record.get("type_name") or "").strip() and str(record.get("member_name") or "").strip()
    )
    for symbol in selected_symbols:
        if _normalize_lookup_token(symbol) in matched_symbols:
            filled_slots.add(f"symbol:{symbol}")

    if "method_or_anchor" in required_slots and (
        method_records
        or extract_wiki_source_anchors(workflow_rows)
    ):
        filled_slots.add("method_or_anchor")

    required_symbols = _unique_preserve_order([
        symbol
        for entry in workflow_entries
        for symbol in (entry.get("required_symbols") or [])
        if str(symbol or "").strip()
    ])
    verification_rules = _unique_preserve_order([
        rule
        for entry in workflow_entries
        for rule in (entry.get("verification_rules") or [])
        if str(rule or "").strip()
    ])
    forbidden_answer_patterns = _unique_preserve_order([
        pattern
        for entry in workflow_entries
        for pattern in (entry.get("forbidden_answer_patterns") or [])
        if str(pattern or "").strip()
    ])
    required_facts: List[Dict[str, Any]] = []
    seen_fact_keys = set()
    for entry in workflow_entries:
        for item in entry.get("required_facts") or []:
            if not isinstance(item, dict):
                continue
            symbol = str(item.get("symbol") or "").strip()
            source = str(item.get("source") or "").strip()
            declaration = str(item.get("declaration") or "").strip()
            declaration_candidates = item.get("declaration_candidates") if isinstance(item.get("declaration_candidates"), list) else None
            if not symbol:
                continue
            fact_key = (
                symbol.lower(),
                source.lower(),
                declaration.lower(),
                json.dumps(declaration_candidates, ensure_ascii=False, sort_keys=True) if declaration_candidates is not None else "",
            )
            if fact_key in seen_fact_keys:
                continue
            seen_fact_keys.add(fact_key)
            required_facts.append(
                {
                    "symbol": symbol,
                    "declaration": declaration or None,
                    "declaration_candidates": declaration_candidates,
                    "source": source or None,
                }
            )

    required_unique = _unique_preserve_order(required_slots)
    filled_unique = [slot for slot in required_unique if slot in filled_slots]
    missing_slots = [slot for slot in required_unique if slot not in filled_slots]
    return {
        "required_slots": required_unique,
        "filled_slots": filled_unique,
        "missing_slots": missing_slots,
        "slots_complete": len(missing_slots) == 0,
        "workflow_paths": _unique_preserve_order([_source_file_path(row) for row in workflow_rows if _source_file_path(row)]),
        "method_paths": _unique_preserve_order([
            str(record.get("doc_path") or "").strip()
            for record in method_records or []
            if str(record.get("doc_path") or "").strip()
        ]),
        "required_symbols": required_symbols,
        "verification_rules": verification_rules,
        "forbidden_answer_patterns": forbidden_answer_patterns,
        "required_facts": required_facts,
    }


def _unique_preserve_order(values: Sequence[str]) -> List[str]:
    output: List[str] = []
    seen = set()
    for item in values or []:
        normalized = str(item or "").strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(normalized)
    return output


def build_exact_api_lookup_summary(query: str, wiki_id: str = "engine") -> Optional[Dict[str, Any]]:
    records = _load_methods_api_index(wiki_id)
    if not records:
        return None

    targets = _extract_lookup_targets(query, records)
    type_candidates = targets["type_candidates"]
    member_candidates = targets["member_candidates"]
    if not targets["is_specific_lookup"]:
        return None

    normalized_types = {_normalize_lookup_token(item) for item in type_candidates}
    normalized_members = {_normalize_lookup_token(item) for item in member_candidates}
    exact_records = [
        record
        for record in records
        if (
            not normalized_types
            or _normalize_lookup_token(record.get("type_name")) in normalized_types
            or _normalize_lookup_token(record.get("qualified_type")) in normalized_types
        )
        and (
            normalized_members
            and _normalize_lookup_token(record.get("member_name")) in normalized_members
        )
    ]

    if exact_records:
        selected_records = exact_records[:4]
        return {
            "mode": "exact_api_lookup",
            "status": "exact_match",
            "type_candidates": type_candidates,
            "member_candidates": member_candidates,
            "matched_api": {
                "qualified_symbol": str(selected_records[0].get("qualified_symbol") or ""),
                "type_name": str(selected_records[0].get("type_name") or ""),
                "member_name": str(selected_records[0].get("member_name") or ""),
                "source_url": str(selected_records[0].get("doc_path") or ""),
                "heading_path": str(selected_records[0].get("heading_path") or ""),
            },
            "related_apis": [],
            "negative_evidence": "",
            "source_records": selected_records,
        }

    related_records = _match_manifest_method_records(
        query=query,
        workflow_rows=_build_manifest_workflow_rows(
            query=query,
            wiki_id=wiki_id,
            top_k=4,
            max_chars=4000,
        ),
        wiki_id=wiki_id,
        max_records=5,
    )

    missing_type = type_candidates[0] if type_candidates else ""
    missing_member = member_candidates[0] if member_candidates else ""
    if missing_type and missing_member:
        negative_evidence = (
            f"No exact verified API match found for {missing_type}.{missing_member} in the indexed engine methods."
        )
    elif missing_member:
        negative_evidence = (
            f"No exact verified API match found for member {missing_member} in the indexed engine methods."
        )
    else:
        negative_evidence = "No exact verified API match found in the indexed engine methods."

    return {
        "mode": "exact_api_lookup",
        "status": "no_exact_match",
        "type_candidates": type_candidates,
        "member_candidates": member_candidates,
        "matched_api": {},
        "related_apis": [
            {
                "qualified_symbol": str(record.get("qualified_symbol") or ""),
                "type_name": str(record.get("type_name") or ""),
                "member_name": str(record.get("member_name") or ""),
                "source_url": str(record.get("doc_path") or ""),
                "heading_path": str(record.get("heading_path") or ""),
            }
            for record in related_records[:5]
        ],
        "negative_evidence": negative_evidence,
        "source_records": related_records[:5],
    }


async def search_docs(
    redis,
    search_svc,
    embed_model,
    query: str,
    filters: Optional[Dict[str, Any]],
    top_k: int,
    collection: Optional[str] = None,
    session_id: Optional[str] = None,
    use_reranker: Optional[bool] = None,
    run_retrieval_fn=run_retrieval,
) -> Dict[str, Any]:
    gate = await SecurityPolicy.check_search_gate(redis, session_id)
    if not gate["allow"]:
        return {"query": query, "top_k": clamp_int(top_k, 1, 50), "results": [], "query_time_ms": 0.0, "reason": gate["reason"]}

    capped_top_k = clamp_int(top_k, 1, 50)
    req = SimpleNamespace(
        message=query,
        query=query,
        top_k=capped_top_k,
        collection=collection or config.EVIDENCE_DEFAULT_COLLECTION,
        filters=filters or {},
        language_filter=(filters or {}).get("language") if isinstance(filters, dict) else None,
        module_filter=(filters or {}).get("module") if isinstance(filters, dict) else None,
        use_reranker=bool(use_reranker) if use_reranker is not None else False,
        evidence_mode=None,
    )
    results, _, elapsed_ms = await asyncio.to_thread(
        run_retrieval_fn,
        search_svc,
        req,
        embed_model,
    )
    docs = [normalize_doc_item(row) for row in results]
    await register_doc_search(redis, session_id, docs)
    return {"query": query, "top_k": capped_top_k, "results": docs, "query_time_ms": elapsed_ms}


async def open_doc_chunks(
    redis,
    search_svc,
    chunk_ids: Iterable[str],
    max_chars: int,
    collection: Optional[str] = None,
    session_id: Optional[str] = None,
    explicit_reference: bool = False,
) -> Dict[str, Any]:
    capped_chars = clamp_int(max_chars, 200, 12000)
    cleaned_ids = [str(x).strip() for x in chunk_ids if str(x).strip()]
    access = await SecurityPolicy.check_doc_chunk_access(redis, session_id, cleaned_ids, explicit_reference)
    if not access["allow"]:
        return {"chunks": [], "missing_chunk_ids": cleaned_ids, "unknown_chunk_ids": access.get("unknown_chunk_ids", []), "max_chars": capped_chars, "used_chars": 0, "reason": access["reason"]}

    qdrant_ids = [qdrant_point_id(x) for x in cleaned_ids]
    if not cleaned_ids:
        return {"chunks": [], "missing_chunk_ids": [], "unknown_chunk_ids": [], "max_chars": capped_chars, "used_chars": 0}

    try:
        points = search_svc.qdrant.retrieve(
            collection_name=collection or config.EVIDENCE_DEFAULT_COLLECTION,
            ids=qdrant_ids,
            with_payload=True,
        )
    except Exception:
        points = []

    chunks = []
    found_ids = set()
    used_chars = 0
    for point in points:
        point_id = str(getattr(point, "id", ""))
        found_ids.add(point_id)
        payload = getattr(point, "payload", {}) or {}
        text = payload.get("text", "")
        if not text:
            continue
        remaining = capped_chars - used_chars
        if remaining <= 0:
            break
        clipped = text[:remaining]
        used_chars += len(clipped)
        chunks.append(
            {
                "chunk_id": point_id,
                "doc_id": payload.get("document_id"),
                "source_url": payload.get("source_url") or payload.get("source_file") or payload.get("file_path"),
                "heading_path": payload.get("heading_path"),
                "updated_at": payload.get("updated_at"),
                "paragraph_range": payload.get("paragraph_range") or (
                    f"chunk:{payload.get('chunk_index')}" if payload.get("chunk_index") is not None else None
                ),
                "text": clipped,
                "truncated": len(clipped) < len(text),
            }
        )

    missing = [cid for cid in cleaned_ids if cid not in found_ids]
    return {"chunks": chunks, "missing_chunk_ids": missing, "unknown_chunk_ids": access.get("unknown_chunk_ids", []), "max_chars": capped_chars, "used_chars": used_chars}


async def get_doc_metadata(doc_store, doc_id: str) -> Dict[str, Any]:
    document = await doc_store.get_document(doc_id)
    if not document:
        return {"doc_id": doc_id, "found": False}
    current_revision = await doc_store.get_current_revision(doc_id)
    revisions = await doc_store.list_revisions(doc_id, limit=10)
    return {"doc_id": doc_id, "found": True, "document": document, "current_revision": current_revision, "recent_revisions": revisions}


def _source_file_path(row: Dict[str, Any]) -> str:
    return str(row.get("file_path") or row.get("source_url") or "").strip().replace("\\", "/")


def _is_workflow_row(row: Dict[str, Any]) -> bool:
    path = _source_file_path(row)
    if path.startswith("workflows/"):
        return True
    if "/workflows/" in path:
        return True
    return False


def _match_method_records_from_candidates(
    *,
    query: str,
    workflow_rows: Sequence[Dict[str, Any]],
    max_records: int,
    wiki_id: str = "engine",
    query_targets: Optional[Dict[str, Any]] = None,
    methods_bundle: Optional[Dict[str, Any]] = None,
    workflow_bundle: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    manifest_records = _match_manifest_method_records(
        query=query,
        workflow_rows=workflow_rows,
        wiki_id=wiki_id,
        max_records=max_records,
        workflow_bundle=workflow_bundle,
        methods_bundle=methods_bundle,
        query_targets=query_targets,
    )
    if manifest_records:
        return manifest_records

    methods_bundle = methods_bundle or _methods_lookup_bundle(wiki_id)
    records = methods_bundle.get("records") or []
    if not records:
        return []

    query_targets = query_targets or _extract_lookup_targets(query, records, methods_bundle.get("type_lookup") or {})

    exact_lookup = build_exact_api_lookup_summary(query, wiki_id=wiki_id)
    if exact_lookup and exact_lookup.get("source_records"):
        return list(exact_lookup.get("source_records") or [])[:max_records]
    return []


def _select_workflow_slot_records(
    *,
    query_targets: Dict[str, Any],
    method_records: Sequence[Dict[str, Any]],
    max_records: int = 3,
) -> List[Dict[str, Any]]:
    selected: List[Dict[str, Any]] = []
    seen = set()

    def add_record(record: Dict[str, Any]) -> None:
        key = str(record.get("qualified_symbol") or "").strip().lower()
        if not key or key in seen:
            return
        seen.add(key)
        selected.append(record)

    explicit_type_keys = {
        _normalize_lookup_token(item)
        for item in query_targets.get("type_candidates") or []
        if _normalize_lookup_token(item)
    }
    explicit_member_keys = {
        _normalize_lookup_token(item)
        for item in query_targets.get("member_candidates") or []
        if _normalize_lookup_token(item)
    }
    explicit_lookup = bool(query_targets.get("is_specific_lookup"))

    if explicit_lookup and (explicit_type_keys or explicit_member_keys):
        for record in method_records or []:
            type_key = _normalize_lookup_token(record.get("type_name") or record.get("qualified_type"))
            member_key = _normalize_lookup_token(record.get("member_name"))
            if explicit_type_keys and type_key not in explicit_type_keys:
                continue
            if explicit_member_keys and member_key not in explicit_member_keys:
                continue
            add_record(record)
            if len(selected) >= max_records:
                return selected
        return selected

    for record in method_records or []:
        add_record(record)
        if len(selected) >= max_records:
            return selected
    return selected


def _build_workflow_slot_bundle(
    *,
    query: str,
    workflow_rows: Sequence[Dict[str, Any]],
    method_records: Sequence[Dict[str, Any]],
    wiki_id: str = "engine",
    workflow_bundle: Optional[Dict[str, Any]] = None,
    methods_bundle: Optional[Dict[str, Any]] = None,
    query_targets: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    manifest_slot_status = _build_manifest_slot_bundle(
        query=query,
        workflow_rows=workflow_rows,
        method_records=method_records,
        wiki_id=wiki_id,
        workflow_bundle=workflow_bundle,
        methods_bundle=methods_bundle,
        query_targets=query_targets,
    )
    if manifest_slot_status is not None:
        return manifest_slot_status

    methods_bundle = methods_bundle or _methods_lookup_bundle(wiki_id)
    methods_index = methods_bundle.get("records") or []
    query_targets = query_targets or _extract_lookup_targets(query, methods_index, methods_bundle.get("type_lookup") or {}) if methods_index else {
        "type_candidates": [],
        "member_candidates": [],
        "is_specific_lookup": False,
    }
    workflow_symbols = {
        _normalize_lookup_token(item)
        for item in extract_doc_symbol_candidates(workflow_rows, max_candidates=16)
        if _normalize_lookup_token(item)
    }
    slot_records = _select_workflow_slot_records(
        query_targets=query_targets,
        method_records=method_records,
        max_records=3,
    )
    required_slots: List[str] = ["workflow"]
    filled_slots = set()
    if workflow_rows:
        filled_slots.add("workflow")

    type_candidates = _unique_preserve_order(query_targets.get("type_candidates") or [])
    member_candidates = _unique_preserve_order(query_targets.get("member_candidates") or [])
    explicit_slot_targets = bool(query_targets.get("is_specific_lookup")) and bool(type_candidates or member_candidates)
    if explicit_slot_targets and member_candidates:
        for item in type_candidates:
            required_slots.append(f"type:{item}")
        for item in member_candidates:
            required_slots.append(f"member:{item}")
    elif explicit_slot_targets and type_candidates:
        for item in type_candidates:
            required_slots.append(f"type:{item}")
    elif slot_records:
        for record in slot_records:
            type_name = str(record.get("type_name") or "").strip()
            member_name = str(record.get("member_name") or "").strip()
            if type_name:
                required_slots.append(f"type:{type_name}")
            if member_name:
                required_slots.append(f"member:{member_name}")
    else:
        required_slots.append("method_or_anchor")

    method_type_keys = {
        _normalize_lookup_token(record.get("type_name"))
        for record in method_records or []
        if _normalize_lookup_token(record.get("type_name"))
    }
    method_member_keys = {
        _normalize_lookup_token(record.get("member_name"))
        for record in method_records or []
        if _normalize_lookup_token(record.get("member_name"))
    }

    for type_name in type_candidates:
        type_key = _normalize_lookup_token(type_name)
        if type_key and (type_key in workflow_symbols or type_key in method_type_keys):
            filled_slots.add(f"type:{type_name}")

    for member_name in member_candidates:
        member_key = _normalize_lookup_token(member_name)
        if member_key and member_key in method_member_keys:
            filled_slots.add(f"member:{member_name}")

    for record in slot_records:
        type_name = str(record.get("type_name") or "").strip()
        member_name = str(record.get("member_name") or "").strip()
        if type_name:
            filled_slots.add(f"type:{type_name}")
        if member_name:
            filled_slots.add(f"member:{member_name}")

    if "method_or_anchor" in required_slots and (
        method_records
        or extract_wiki_source_anchors(workflow_rows)
    ):
        filled_slots.add("method_or_anchor")

    required_unique = _unique_preserve_order(required_slots)
    filled_unique = [slot for slot in required_unique if slot in filled_slots]
    missing_slots = [slot for slot in required_unique if slot not in filled_slots]
    return {
        "required_slots": required_unique,
        "filled_slots": filled_unique,
        "missing_slots": missing_slots,
        "slots_complete": len(missing_slots) == 0,
        "workflow_paths": _unique_preserve_order([_source_file_path(row) for row in workflow_rows if _source_file_path(row)]),
        "method_paths": _unique_preserve_order([
            str(record.get("doc_path") or "").strip()
            for record in method_records or []
            if str(record.get("doc_path") or "").strip()
        ]),
        "required_symbols": [],
        "verification_rules": [],
        "forbidden_answer_patterns": [],
        "required_facts": [],
    }


def _build_workflow_first_bundle_uncached(
    *,
    query: str,
    top_k: int,
    doc_open_limit: int,
    max_chars: int,
    explicit_wiki_id: str,
) -> Dict[str, Any]:
    normalized_wiki_id = _normalize_wiki_id(explicit_wiki_id or "engine")
    workflow_lookup_bundle = _workflow_lookup_bundle(normalized_wiki_id)
    methods_bundle = _methods_lookup_bundle(normalized_wiki_id)
    methods_index = methods_bundle.get("records") or []
    query_targets = _extract_lookup_targets(query, methods_index, methods_bundle.get("type_lookup") or {})
    workflow_search_limit = max(min(top_k, 20), min(max(4, doc_open_limit * 3), 20))
    wiki_rows = _build_manifest_workflow_rows(
        query=query,
        wiki_id=normalized_wiki_id,
        top_k=workflow_search_limit,
        max_chars=max_chars,
        workflow_bundle=workflow_lookup_bundle,
    )
    if not wiki_rows:
        wiki_rows = list(
            search_wiki(
                query=query,
                top_k=workflow_search_limit,
                max_chars=max_chars,
                wiki_id=explicit_wiki_id,
            ).get("results", [])
            or []
        )
    workflow_rows = [row for row in wiki_rows if _is_workflow_row(row)][:1]
    if not workflow_rows:
        return {
            "sources": [],
            "slot_status": {
                "required_slots": ["workflow"],
                "filled_slots": [],
                "missing_slots": ["workflow"],
                "slots_complete": False,
                "workflow_paths": [],
                "method_paths": [],
            },
        }

    primary_workflow_rows = workflow_rows[:1]
    if query_targets.get("is_specific_lookup"):
        related_records = _match_method_records_from_candidates(
            query=query,
            workflow_rows=primary_workflow_rows,
            max_records=max(1, doc_open_limit - len(workflow_rows)),
            wiki_id=normalized_wiki_id,
            query_targets=query_targets,
            methods_bundle=methods_bundle,
            workflow_bundle=workflow_lookup_bundle,
        )
    else:
        related_records = []
    method_rows = [
        _build_lookup_source_excerpt(record, section_index=index + 1)
        for index, record in enumerate(related_records[: max(0, doc_open_limit - len(workflow_rows))])
    ]
    sources = merge_doc_sources([workflow_rows, method_rows])[:doc_open_limit]
    slot_status = _build_workflow_slot_bundle(
        query=query,
        workflow_rows=primary_workflow_rows,
        method_records=related_records,
        wiki_id=normalized_wiki_id,
        workflow_bundle=workflow_lookup_bundle,
        methods_bundle=methods_bundle,
        query_targets=query_targets,
    )
    return {
        "sources": sources,
        "slot_status": slot_status,
    }


@lru_cache(maxsize=64)
def _build_workflow_first_bundle_cached(
    wiki_id: str,
    manifest_signature: str,
    query: str,
    top_k: int,
    doc_open_limit: int,
    max_chars: int,
) -> Dict[str, Any]:
    del manifest_signature
    return _build_workflow_first_bundle_uncached(
        query=query,
        top_k=top_k,
        doc_open_limit=doc_open_limit,
        max_chars=max_chars,
        explicit_wiki_id=wiki_id,
    )


def _build_workflow_first_bundle(
    *,
    query: str,
    top_k: int,
    doc_open_limit: int,
    max_chars: int,
    explicit_wiki_id: str,
) -> Dict[str, Any]:
    normalized_wiki_id = _normalize_wiki_id(explicit_wiki_id or "engine")
    return _build_workflow_first_bundle_cached(
        normalized_wiki_id,
        _manifest_signature(normalized_wiki_id),
        str(query or ""),
        int(top_k),
        int(doc_open_limit),
        int(max_chars),
    )


async def collect_sources(
    *,
    redis,
    search_svc,
    embed_model,
    session_id: str,
    query: str,
    filters: Optional[Dict[str, Any]],
    top_k: int,
    doc_open_limit: int,
    max_chars: int,
    active_collection: str,
    search_only: bool,
    response_type: str,
    workflow_first: bool = False,
    workflow_bundle: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    rt = str(response_type or "").strip().lower()
    explicit_wiki_id = ""
    if isinstance(filters, dict):
        explicit_wiki_id = str(filters.get("wiki_id") or "").strip().lower()

    code_first_types = {
        "code_explain",
        "code_review",
        "bug_fix",
        "refactor",
        "troubleshooting",
    }
    wiki_first_types = set(wiki_config.routing_doc_first_response_types()) | {
        "api_lookup",
        "code_generate",
        "compare",
        "design_review",
        "migration",
        "general",
        "doc_lookup",
    }
    wiki_priority = "code_first" if rt in code_first_types else "wiki_first" if rt in wiki_first_types else "wiki_first"

    if workflow_first and isinstance(workflow_bundle, dict):
        workflow_bundle_data = workflow_bundle
    elif workflow_first:
        workflow_bundle_data = _build_workflow_first_bundle(
            query=query,
            top_k=top_k,
            doc_open_limit=doc_open_limit,
            max_chars=max_chars,
            explicit_wiki_id=explicit_wiki_id,
        )
    else:
        workflow_bundle_data = {"sources": [], "slot_status": {}}

    wiki_rows = list(workflow_bundle_data.get("sources") or []) if workflow_first else []
    if not wiki_rows:
        wiki_rows = list(
            search_wiki(
                query=query,
                top_k=min(top_k, doc_open_limit),
                max_chars=max_chars,
                wiki_id=explicit_wiki_id,
            ).get("results", [])
            or []
        )

    doc_rows: List[Dict[str, Any]] = []
    if not bool((workflow_bundle_data.get("slot_status") or {}).get("slots_complete")):
        doc_rows = list(
            (
                await search_docs(
                    redis,
                    search_svc,
                    embed_model,
                    query=query,
                    filters=filters,
                    top_k=top_k,
                    collection=active_collection,
                    session_id=session_id,
                    use_reranker=str(response_type or "").strip().lower() in {"api_lookup", "code_generate"},
                )
            ).get("results", [])
            or []
        )
    strong_wiki_coverage = len(wiki_rows) >= min(2, max(1, doc_open_limit // 2))
    if search_only:
        if wiki_priority == "code_first":
            return merge_doc_sources([doc_rows, wiki_rows])[:doc_open_limit]
        return merge_doc_sources([wiki_rows, doc_rows])[:doc_open_limit]

    remaining = max(0, doc_open_limit - len(wiki_rows[:doc_open_limit]))
    if wiki_priority != "code_first" and strong_wiki_coverage:
        remaining = min(remaining, 2)
    chunk_ids = [
        row.get("chunk_id")
        for row in doc_rows
        if row.get("chunk_id") and not str(row.get("chunk_id") or "").startswith("wiki:")
    ][:remaining]
    opened = await open_doc_chunks(
        redis,
        search_svc,
        chunk_ids=chunk_ids,
        max_chars=max_chars,
        collection=active_collection,
        session_id=session_id,
        explicit_reference=False,
    )
    if wiki_priority == "code_first":
        return merge_doc_sources([opened.get("chunks", []), doc_rows, wiki_rows])[:doc_open_limit]
    return merge_doc_sources([wiki_rows, opened.get("chunks", []), doc_rows])[:doc_open_limit]


def extract_wiki_source_anchors(doc_chunks: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    anchors: List[Dict[str, Any]] = []
    seen = set()
    for chunk_index, chunk in enumerate(doc_chunks or []):
        text = str(chunk.get("text") or "")
        if not text:
            continue
        page_symbols = extract_doc_symbol_candidates([chunk], max_candidates=12)
        for line_index, raw_line in enumerate(text.splitlines()):
            line = str(raw_line or "").strip()
            if not line:
                continue
            lowered = line.lower()
            evidence_type = "reference"
            if "declaration:" in lowered or "type declaration:" in lowered:
                evidence_type = "declaration"
            elif "implementation:" in lowered:
                evidence_type = "implementation"
            line_symbols = _extract_line_symbols(line) or page_symbols
            for match in _WIKI_SOURCE_REF_RE.finditer(line):
                path = str(match.group(1) or "").strip().replace("\\", "/")
                start_line = max(1, int(match.group(2) or 1))
                end_line = max(start_line, int(match.group(3) or match.group(2) or start_line))
                key = (path, start_line, end_line, evidence_type)
                if key in seen:
                    continue
                seen.add(key)
                anchors.append(
                    {
                        "path": path,
                        "line_range": f"{start_line}-{end_line}",
                        "evidence_type": evidence_type,
                        "source_url": chunk.get("source_url"),
                        "heading_path": chunk.get("heading_path"),
                        "symbols": list(line_symbols),
                        "_chunk_index": chunk_index,
                        "_line_index": line_index,
                    }
                )
    return anchors


def _anchor_priority(anchor: Dict[str, Any]) -> int:
    evidence_type = str(anchor.get("evidence_type") or "").strip().lower()
    if evidence_type == "implementation":
        return 0
    if evidence_type == "declaration":
        return 1
    return 2


def prioritize_wiki_source_anchors(
    anchors: Sequence[Dict[str, Any]],
    *,
    max_candidates: int,
) -> List[Dict[str, Any]]:
    pending = list(anchors or [])
    ordered: List[Dict[str, Any]] = []
    covered_symbols = set()

    while pending and len(ordered) < max_candidates:
        scored: List[Tuple[int, int, int, int, int]] = []
        for index, anchor in enumerate(pending):
            symbols = [
                str(item or "").strip()
                for item in anchor.get("symbols") or []
                if str(item or "").strip()
            ]
            novelty = len([item for item in symbols if item.lower() not in covered_symbols])
            scored.append(
                (
                    novelty,
                    -_anchor_priority(anchor),
                    -int(anchor.get("_chunk_index") or 0),
                    -int(anchor.get("_line_index") or 0),
                    -index,
                )
            )
        best_index = max(range(len(pending)), key=lambda idx: scored[idx])
        best_anchor = pending.pop(best_index)
        ordered.append(best_anchor)
        for symbol in best_anchor.get("symbols") or []:
            normalized = str(symbol or "").strip().lower()
            if normalized:
                covered_symbols.add(normalized)

    if len(ordered) >= max_candidates:
        return ordered[:max_candidates]

    remainder = sorted(
        pending,
        key=lambda item: (
            _anchor_priority(item),
            int(item.get("_chunk_index") or 0),
            int(item.get("_line_index") or 0),
        ),
    )
    ordered.extend(remainder[: max(0, max_candidates - len(ordered))])
    return ordered[:max_candidates]


def _window_overlap_ratio(left_range: str, right_range: str) -> float:
    left_start, left_end = parse_line_range(str(left_range or "1-1"))
    right_start, right_end = parse_line_range(str(right_range or "1-1"))
    left_span = max(1, left_end - left_start + 1)
    right_span = max(1, right_end - right_start + 1)
    overlap_start = max(left_start, right_start)
    overlap_end = min(left_end, right_end)
    if overlap_end < overlap_start:
        return 0.0
    overlap_span = overlap_end - overlap_start + 1
    return overlap_span / max(1, min(left_span, right_span))


def windows_overlap_strongly(
    existing_windows: Sequence[Dict[str, Any]],
    candidate_window: Dict[str, Any],
    *,
    threshold: float = 0.6,
) -> bool:
    candidate_path = str(candidate_window.get("path") or "").strip()
    candidate_range = str(candidate_window.get("line_range") or candidate_window.get("lineRange") or "").strip()
    if not candidate_path or not candidate_range:
        return False
    for existing in existing_windows or []:
        existing_path = str(existing.get("path") or "").strip()
        existing_range = str(existing.get("line_range") or existing.get("lineRange") or "").strip()
        if existing_path != candidate_path or not existing_range:
            continue
        if _window_overlap_ratio(existing_range, candidate_range) >= threshold:
            return True
    return False


def merge_code_windows(groups: Sequence[Sequence[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    seen = set()
    for group in groups or []:
        for row in group or []:
            key = (str(row.get("path") or "").strip(), str(row.get("line_range") or "").strip())
            if not key[0] or key in seen:
                continue
            if windows_overlap_strongly(merged, row):
                continue
            seen.add(key)
            merged.append(row)
    return merged


def merge_doc_sources(groups: Sequence[Sequence[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    for group in groups or []:
        merged.extend(list(group or []))
    return dedupe_doc_items(merged)


def should_skip_broad_code_evidence(
    *,
    workflow_first: bool,
    response_type: str,
    workflow_bundle: Optional[Dict[str, Any]],
    wiki_code_windows: Sequence[Dict[str, Any]],
) -> bool:
    if not workflow_first:
        return False
    normalized_response_type = str(response_type or "").strip().lower()
    if normalized_response_type not in {"general", "doc_lookup", "compare", "design_review", "migration"}:
        return False
    slot_status = workflow_bundle.get("slot_status") if isinstance(workflow_bundle, dict) else {}
    if not bool((slot_status or {}).get("slots_complete")):
        return False
    return len(list(wiki_code_windows or [])) >= 4


def _unique_strings(values: Iterable[str], *, limit: Optional[int] = None) -> List[str]:
    output: List[str] = []
    seen = set()
    for item in values or []:
        normalized = str(item or "").strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(normalized)
        if limit is not None and len(output) >= limit:
            break
    return output


def _extract_line_symbols(line: str) -> List[str]:
    tokens: List[str] = []
    for raw_token in _BACKTICK_TOKEN_RE.findall(str(line or "")):
        normalized = str(raw_token or "").replace("::", ".")
        for part in normalized.split("."):
            candidate = str(part or "").strip()
            if _TYPE_LIKE_RE.match(candidate):
                tokens.append(candidate)
    return _unique_strings(tokens)


def extract_doc_symbol_candidates(
    doc_chunks: Sequence[Dict[str, Any]],
    *,
    max_candidates: int = 12,
) -> List[str]:
    candidates: List[str] = []
    for chunk in doc_chunks or []:
        for raw_symbol in chunk.get("symbols") or []:
            normalized = str(raw_symbol or "").replace("::", ".")
            for part in normalized.split("."):
                candidate = str(part or "").strip()
                if _TYPE_LIKE_RE.match(candidate):
                    candidates.append(candidate)
        for raw_line in str(chunk.get("text") or "").splitlines():
            candidates.extend(_extract_line_symbols(raw_line))
    return _unique_strings(candidates, limit=max_candidates)


def wiki_anchor_window_budget(
    *,
    doc_chunks: Sequence[Dict[str, Any]],
    response_type: str,
    code_window_cap: int,
) -> int:
    capped = clamp_int(code_window_cap, 1, 32)
    normalized_response_type = str(response_type or "").strip().lower()
    workflow_only = bool(doc_chunks) and all(_is_workflow_row(chunk) for chunk in doc_chunks)
    if workflow_only and normalized_response_type in {"general", "doc_lookup", "compare", "design_review", "migration"}:
        return min(capped, 6)
    return capped


async def collect_wiki_anchor_code_windows(
    *,
    redis,
    session_id: str,
    code_tools,
    doc_chunks: Sequence[Dict[str, Any]],
    max_chars: int,
    max_line_span: int,
    response_type: str,
    code_window_cap: int,
    search_only: bool,
) -> List[Dict[str, Any]]:
    anchor_budget = wiki_anchor_window_budget(
        doc_chunks=doc_chunks,
        response_type=response_type,
        code_window_cap=code_window_cap,
    )
    anchors = prioritize_wiki_source_anchors(
        extract_wiki_source_anchors(doc_chunks),
        max_candidates=anchor_budget,
    )
    if not anchors or code_tools is None:
        return []

    if search_only:
        await register_code_search(redis, session_id, anchors)
        return []

    windows: List[Dict[str, Any]] = []
    seen = set()
    per_path_count: Dict[str, int] = {}
    per_path_cap = 1 if anchor_budget <= 6 else 2
    max_windows = min(clamp_int(code_window_cap, 1, 24), max(6, len(anchors)))

    for anchor in anchors:
        if len(windows) >= max_windows:
            break
        path = str(anchor.get("path") or "").strip()
        if not path or per_path_count.get(path, 0) >= per_path_cap:
            continue
        start_line, end_line = parse_line_range(str(anchor.get("line_range") or "1-1"))
        start_line, end_line = expand_line_window(start_line, end_line, response_type, max_line_span)
        window = read_code_lines(
            code_tools,
            path=path,
            start_line=start_line,
            end_line=end_line,
            max_line_span=max_line_span,
            max_chars=max_chars,
        )
        if not window.get("found"):
            continue
        key = (str(window.get("path") or "").strip(), str(window.get("line_range") or "").strip())
        if key in seen:
            continue
        if windows_overlap_strongly(windows, window):
            continue
        seen.add(key)
        per_path_count[path] = per_path_count.get(path, 0) + 1
        window["evidence_type"] = str(anchor.get("evidence_type") or "reference")
        if anchor.get("source_url"):
            window["source_url"] = anchor.get("source_url")
        if anchor.get("heading_path"):
            window["heading_path"] = anchor.get("heading_path")
        windows.append(window)

    if windows:
        await register_code_search(redis, session_id, windows)
    return windows


async def lookup_sources_and_code(
    *,
    redis,
    search_svc=None,
    embed_model=None,
    code_tools=None,
    session_id: str,
    user_id: Optional[str],
    query: str,
    filters: Optional[Dict[str, Any]],
    top_k: int,
    limit: int,
    max_chars: int,
    max_line_span: int,
    response_type: str,
    workflow_first: bool,
    search_only: bool,
    collection: Optional[str],
    collect_code_evidence_async,
    state=None,
) -> Dict[str, Any]:
    total_started_at = perf_counter()
    timings_ms: Dict[str, float] = {}

    def record_timing(stage: str, started_at: float) -> None:
        timings_ms[stage] = round((perf_counter() - started_at) * 1000, 2)

    if state is not None:
        search_svc = search_svc if search_svc is not None else getattr(state, "search_svc", None)
        embed_model = embed_model if embed_model is not None else getattr(state, "embed_model", None)
        code_tools = code_tools if code_tools is not None else getattr(state, "code_tools", None)

    stage_started_at = perf_counter()
    await resolve_tool_user_context(redis, session_id=session_id, user_id=user_id)
    record_timing("resolve_user_context", stage_started_at)

    capped_top_k = clamp_int(top_k, 1, 50)
    capped_limit = clamp_int(limit, 1, 50)
    doc_open_limit = min(capped_limit, clamp_int(config.CHAT_TOOL_DOC_OPEN_LIMIT, 1, 50))
    code_window_cap = clamp_int(config.CHAT_TOOL_CODE_MAX_WINDOWS, 4, 24)
    active_collection = collection or config.EVIDENCE_DEFAULT_COLLECTION
    normalized_wiki_id = _normalize_wiki_id(str(filters.get("wiki_id") or "").strip() if isinstance(filters, dict) else "engine")

    if str(response_type or "").strip().lower() in {"api_lookup", "exact_api_lookup"}:
        stage_started_at = perf_counter()
        lookup_summary = build_exact_api_lookup_summary(query, wiki_id=normalized_wiki_id)
        record_timing("exact_lookup_summary", stage_started_at)
        if lookup_summary is not None:
            source_records = list(lookup_summary.get("source_records") or [])[:doc_open_limit]
            stage_started_at = perf_counter()
            exact_sources = [
                _build_lookup_source_excerpt(record, section_index=index + 1)
                for index, record in enumerate(source_records)
            ]
            record_timing("build_exact_sources", stage_started_at)
            stage_started_at = perf_counter()
            exact_code_windows = await collect_wiki_anchor_code_windows(
                redis=redis,
                session_id=session_id,
                code_tools=code_tools,
                doc_chunks=exact_sources,
                max_chars=max_chars,
                max_line_span=max_line_span,
                response_type=response_type,
                code_window_cap=code_window_cap,
                search_only=search_only,
            )
            record_timing("exact_wiki_anchor_windows", stage_started_at)
            stage_started_at = perf_counter()
            citations = build_citations(exact_sources, exact_code_windows)
            record_timing("build_citations", stage_started_at)
            timings_ms["total"] = round((perf_counter() - total_started_at) * 1000, 2)
            return {
                "query": query,
                "sources": exact_sources,
                "code_windows": exact_code_windows,
                "citations": citations,
                "lookup_summary": {
                    key: value
                    for key, value in lookup_summary.items()
                    if key != "source_records"
                },
                "timings_ms": timings_ms,
            }

    stage_started_at = perf_counter()
    workflow_bundle = _build_workflow_first_bundle(
        query=query,
        top_k=capped_top_k,
        doc_open_limit=doc_open_limit,
        max_chars=max_chars,
        explicit_wiki_id=normalized_wiki_id,
    ) if workflow_first else {"slot_status": {}}
    record_timing("build_workflow_bundle", stage_started_at)

    stage_started_at = perf_counter()
    sources = await collect_sources(
        redis=redis,
        search_svc=search_svc,
        embed_model=embed_model,
        session_id=session_id,
        query=query,
        filters=filters,
        top_k=capped_top_k,
        doc_open_limit=doc_open_limit,
        max_chars=max_chars,
        active_collection=active_collection,
        search_only=search_only,
        response_type=response_type,
        workflow_first=workflow_first,
        workflow_bundle=workflow_bundle,
    )
    record_timing("collect_sources", stage_started_at)
    stage_started_at = perf_counter()
    doc_symbol_candidates = extract_doc_symbol_candidates(sources, max_candidates=12)
    record_timing("extract_doc_symbols", stage_started_at)
    stage_started_at = perf_counter()
    wiki_code_windows = await collect_wiki_anchor_code_windows(
        redis=redis,
        session_id=session_id,
        code_tools=code_tools,
        doc_chunks=sources,
        max_chars=max_chars,
        max_line_span=max_line_span,
        response_type=response_type,
        code_window_cap=code_window_cap,
        search_only=search_only,
    )
    record_timing("collect_wiki_anchor_code_windows", stage_started_at)
    if should_skip_broad_code_evidence(
        workflow_first=workflow_first,
        response_type=response_type,
        workflow_bundle=workflow_bundle,
        wiki_code_windows=wiki_code_windows,
    ):
        searched_code_windows = []
        timings_ms["collect_code_evidence"] = 0.0
    else:
        stage_started_at = perf_counter()
        searched_code_windows = await collect_code_evidence_async(
            redis=redis,
            code_tools=code_tools,
            session_id=session_id,
            query=query,
            extra_query_candidates=doc_symbol_candidates,
            capped_limit=capped_limit,
            max_chars=max_chars,
            max_line_span=max_line_span,
            response_type=response_type,
            search_only=search_only,
            code_window_cap=code_window_cap,
        )
        record_timing("collect_code_evidence", stage_started_at)
    stage_started_at = perf_counter()
    code_windows = merge_code_windows([wiki_code_windows, searched_code_windows])
    record_timing("merge_code_windows", stage_started_at)
    stage_started_at = perf_counter()
    citations = build_citations(sources, code_windows)
    record_timing("build_citations", stage_started_at)
    timings_ms["total"] = round((perf_counter() - total_started_at) * 1000, 2)
    if timings_ms["total"] >= 2000:
        logger.info(
            "lookup_sources_and_code_timing",
            extra={
                "query": query[:200],
                "response_type": str(response_type or ""),
                "workflow_first": bool(workflow_first),
                "timings_ms": timings_ms,
                "source_count": len(sources),
                "code_window_count": len(code_windows),
            },
        )

    return {
        "query": query,
        "sources": sources,
        "code_windows": code_windows,
        "citations": citations,
        "workflow_bundle": workflow_bundle.get("slot_status") if workflow_first else {},
        "timings_ms": timings_ms,
    }

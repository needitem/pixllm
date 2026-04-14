import re
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ... import config
from ..retrieval.service import run_retrieval
from ...core.policy import SecurityPolicy
from .access import register_code_search, register_doc_search, resolve_tool_user_context
from .code_runtime import read_code_lines
from .query_terms import extract_symbol_query_candidates
from .query_strategy import expand_line_window, parse_line_range
from .support import build_citations, clamp_int, dedupe_doc_items, normalize_doc_item, qdrant_point_id
from .wiki_runtime import search_wiki

_WIKI_SOURCE_REF_RE = re.compile(r"\b(Source/[^`:\s]+):(\d+)(?:-(\d+))?\b")
_BACKTICK_TOKEN_RE = re.compile(r"`([^`]+)`")
_TYPE_LIKE_RE = re.compile(r"^(?:[A-Z][A-Za-z0-9_]*|e[A-Z][A-Za-z0-9_]*)$")
_LOOKUP_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")
_LOOKUP_QUALIFIED_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)[.:]([A-Za-z_][A-Za-z0-9_]*)\b")
_SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
_WORKFLOW_STEP_RE = re.compile(r"^\s*(\d+)\.\s+(.*)$")
_STEP_OUTPUT_TYPE_RE = re.compile(r"\bto get\s+([A-Z][A-Za-z0-9_]*)\b", re.IGNORECASE)
_METHODS_DOC_STEM_PREFIX = "Methods_T_"
_QUERY_FILLER_TOKENS = {
    "api",
    "bool",
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


def _methods_wiki_root() -> Path:
    return Path(__file__).resolve().parents[3] / ".profiles" / "wiki" / "engine" / "methods"


def _workflow_wiki_root() -> Path:
    return _methods_wiki_root().parent / "workflows"


def _normalize_lookup_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())


@lru_cache(maxsize=1)
def _load_methods_api_index() -> List[Dict[str, Any]]:
    root = _methods_wiki_root()
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
) -> Dict[str, Any]:
    source = str(query or "").strip()
    lowered = source.lower()
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


def _extract_workflow_member_candidates(step_text: str, known_types: Dict[str, str]) -> List[Dict[str, str]]:
    candidates: List[Dict[str, str]] = []
    seen = set()

    def _append(member_name: str, type_name: str = "") -> None:
        normalized_member = _normalize_lookup_token(member_name)
        normalized_type = _normalize_lookup_token(type_name)
        key = (normalized_type, normalized_member)
        if not normalized_member or key in seen:
            return
        seen.add(key)
        candidates.append({
            "type_name": str(type_name or "").strip(),
            "member_name": str(member_name or "").strip(),
        })

    for raw_token in _BACKTICK_TOKEN_RE.findall(str(step_text or "")):
        token = str(raw_token or "").strip()
        if not token:
            continue
        qualified_match = _LOOKUP_QUALIFIED_RE.search(token)
        if qualified_match:
            _append(qualified_match.group(2), qualified_match.group(1))
            continue
        call_match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", token)
        if call_match:
            member_name = str(call_match.group(1) or "").strip()
            if _normalize_lookup_token(member_name) not in known_types:
                _append(member_name)
            continue
        if _TYPE_LIKE_RE.match(token) and _normalize_lookup_token(token) not in known_types:
            _append(token)

    for call_match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", str(step_text or "")):
        member_name = str(call_match.group(1) or "").strip()
        if _normalize_lookup_token(member_name) not in known_types:
            _append(member_name)

    return candidates


@lru_cache(maxsize=1)
def _load_workflow_api_steps() -> List[Dict[str, Any]]:
    methods_index = _load_methods_api_index()
    workflow_root = _workflow_wiki_root()
    if not workflow_root.exists() or not methods_index:
        return []

    known_types = {}
    member_to_records: Dict[str, List[Dict[str, Any]]] = {}
    qualified_to_record: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for record in methods_index:
        known_types[_normalize_lookup_token(record.get("type_name"))] = str(record.get("type_name") or "")
        known_types[_normalize_lookup_token(record.get("qualified_type"))] = str(record.get("type_name") or "")
        member_to_records.setdefault(_normalize_lookup_token(record.get("member_name")), []).append(record)
        qualified_to_record[(
            _normalize_lookup_token(record.get("type_name")),
            _normalize_lookup_token(record.get("member_name")),
        )] = record

    steps: List[Dict[str, Any]] = []
    for path in sorted(workflow_root.glob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        active_types: List[str] = []
        relative_doc_path = path.relative_to(workflow_root.parent).as_posix()

        for index, raw_line in enumerate(lines):
            match = _WORKFLOW_STEP_RE.match(str(raw_line or ""))
            if not match:
                continue
            step_text = str(match.group(2) or "").strip()
            explicit_types = _unique_preserve_order([
                known_types.get(_normalize_lookup_token(token), "")
                for token in extract_symbol_query_candidates(step_text, max_candidates=12)
            ])
            produced_types = _unique_preserve_order([
                known_types.get(_normalize_lookup_token(group_match.group(1)), str(group_match.group(1) or "").strip())
                for group_match in _STEP_OUTPUT_TYPE_RE.finditer(step_text)
            ])
            member_candidates = _extract_workflow_member_candidates(step_text, known_types)
            resolved_records: List[Dict[str, Any]] = []

            preferred_types = _unique_preserve_order([*explicit_types, *active_types])
            for candidate in member_candidates:
                explicit_type = known_types.get(_normalize_lookup_token(candidate.get("type_name")), str(candidate.get("type_name") or "").strip())
                member_name = str(candidate.get("member_name") or "").strip()
                normalized_member = _normalize_lookup_token(member_name)
                if not normalized_member:
                    continue
                if explicit_type:
                    record = qualified_to_record.get((
                        _normalize_lookup_token(explicit_type),
                        normalized_member,
                    ))
                    if record:
                        resolved_records.append(record)
                        continue
                method_records = member_to_records.get(normalized_member, [])
                selected = next(
                    (
                        record
                        for preferred_type in preferred_types
                        for record in method_records
                        if _normalize_lookup_token(record.get("type_name")) == _normalize_lookup_token(preferred_type)
                    ),
                    None,
                )
                if selected is None and len(method_records) == 1:
                    selected = method_records[0]
                if selected is not None:
                    resolved_records.append(selected)

            steps.append({
                "doc_path": relative_doc_path,
                "line_index": index,
                "text": step_text,
                "explicit_types": explicit_types,
                "produced_types": produced_types,
                "resolved_records": _unique_preserve_order([
                    str(record.get("qualified_symbol") or "")
                    for record in resolved_records
                ]),
                "record_lookup": {
                    str(record.get("qualified_symbol") or ""): record
                    for record in resolved_records
                },
            })
            active_types = _unique_preserve_order([*produced_types, *explicit_types, *active_types])[:8]
    return steps


def _derive_workflow_related_records(
    *,
    type_candidates: Sequence[str],
    member_candidates: Sequence[str],
) -> List[Dict[str, Any]]:
    type_keys = {_normalize_lookup_token(item) for item in type_candidates or [] if _normalize_lookup_token(item)}
    member_keys = {_normalize_lookup_token(item) for item in member_candidates or [] if _normalize_lookup_token(item)}
    if not type_keys and not member_keys:
        return []

    related_records: List[Dict[str, Any]] = []
    seen = set()
    for step in _load_workflow_api_steps():
        explicit_keys = {_normalize_lookup_token(item) for item in step.get("explicit_types") or []}
        produced_keys = {_normalize_lookup_token(item) for item in step.get("produced_types") or []}
        text_key = _normalize_lookup_token(step.get("text") or "")
        if not (
            type_keys.intersection(explicit_keys)
            or type_keys.intersection(produced_keys)
            or any(member_key and member_key in text_key for member_key in member_keys)
        ):
            continue
        for qualified_symbol in step.get("resolved_records") or []:
            record = (step.get("record_lookup") or {}).get(qualified_symbol)
            if not record:
                continue
            key = str(record.get("qualified_symbol") or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            related_records.append(record)
    return related_records


def build_exact_api_lookup_summary(query: str) -> Optional[Dict[str, Any]]:
    records = _load_methods_api_index()
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

    related_records = _derive_workflow_related_records(
        type_candidates=type_candidates,
        member_candidates=member_candidates,
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
        collection=collection or config.RAG_DEFAULT_COLLECTION,
        filters=filters or {},
        language_filter=(filters or {}).get("language") if isinstance(filters, dict) else None,
        module_filter=(filters or {}).get("module") if isinstance(filters, dict) else None,
        use_reranker=bool(use_reranker) if use_reranker is not None else False,
        evidence_mode=None,
    )
    results, _, elapsed_ms = run_retrieval_fn(search_svc, req, embed_model)
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
            collection_name=collection or config.RAG_DEFAULT_COLLECTION,
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
) -> List[Dict[str, Any]]:
    wiki_rows = list(search_wiki(query=query, top_k=min(top_k, doc_open_limit), max_chars=max_chars).get("results", []) or [])

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
    if search_only:
        return merge_doc_sources([wiki_rows, doc_rows])[:doc_open_limit]

    remaining = max(0, doc_open_limit - len(wiki_rows[:doc_open_limit]))
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
    anchors = prioritize_wiki_source_anchors(
        extract_wiki_source_anchors(doc_chunks),
        max_candidates=clamp_int(code_window_cap, 1, 32),
    )
    if not anchors or code_tools is None:
        return []

    if search_only:
        await register_code_search(redis, session_id, anchors)
        return []

    windows: List[Dict[str, Any]] = []
    seen = set()
    per_path_count: Dict[str, int] = {}
    per_path_cap = 2
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
    search_only: bool,
    collection: Optional[str],
    collect_code_evidence_async,
    state=None,
) -> Dict[str, Any]:
    if state is not None:
        search_svc = search_svc if search_svc is not None else getattr(state, "search_svc", None)
        embed_model = embed_model if embed_model is not None else getattr(state, "embed_model", None)
        code_tools = code_tools if code_tools is not None else getattr(state, "code_tools", None)

    await resolve_tool_user_context(redis, session_id=session_id, user_id=user_id)

    capped_top_k = clamp_int(top_k, 1, 50)
    capped_limit = clamp_int(limit, 1, 50)
    doc_open_limit = min(capped_limit, clamp_int(config.CHAT_TOOL_DOC_OPEN_LIMIT, 1, 50))
    code_window_cap = clamp_int(config.CHAT_TOOL_CODE_MAX_WINDOWS, 4, 24)
    active_collection = collection or config.RAG_DEFAULT_COLLECTION

    if str(response_type or "").strip().lower() in {"api_lookup", "exact_api_lookup"}:
        lookup_summary = build_exact_api_lookup_summary(query)
        if lookup_summary is not None:
            source_records = list(lookup_summary.get("source_records") or [])[:doc_open_limit]
            exact_sources = [
                _build_lookup_source_excerpt(record, section_index=index + 1)
                for index, record in enumerate(source_records)
            ]
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
            return {
                "query": query,
                "sources": exact_sources,
                "code_windows": exact_code_windows,
                "citations": build_citations(exact_sources, exact_code_windows),
                "lookup_summary": {
                    key: value
                    for key, value in lookup_summary.items()
                    if key != "source_records"
                },
            }

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
    )
    doc_symbol_candidates = extract_doc_symbol_candidates(sources, max_candidates=12)
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
    code_windows = merge_code_windows([wiki_code_windows, searched_code_windows])

    return {
        "query": query,
        "sources": sources,
        "code_windows": code_windows,
        "citations": build_citations(sources, code_windows),
    }

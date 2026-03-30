import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from ...utils.encoding import TEXT_ENCODING_FALLBACKS, decode_bytes

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def normalize_feedback_rating(rating: int) -> int:
    return clamp_int(rating, 1, 5)


def normalize_heading_path(value: Any) -> str:
    if isinstance(value, list):
        return " > ".join(str(x).strip() for x in value if str(x).strip())
    return str(value or "").strip()


def normalize_doc_item(item: Dict[str, Any], doc_updated_at: Optional[str] = None) -> Dict[str, Any]:
    payload = item.get("payload", {}) if isinstance(item, dict) else {}
    source_url = payload.get("source_url") or payload.get("source_file") or payload.get("file_path")
    paragraph_range = payload.get("paragraph_range")
    if paragraph_range is None and payload.get("chunk_index") is not None:
        paragraph_range = f"chunk:{payload.get('chunk_index')}"

    return {
        "chunk_id": str(item.get("id")),
        "doc_id": payload.get("document_id"),
        "source_url": source_url,
        "heading_path": payload.get("heading_path"),
        "chunk_index": payload.get("chunk_index"),
        "updated_at": payload.get("updated_at") or doc_updated_at,
        "paragraph_range": paragraph_range,
        "text": payload.get("text", ""),
        "score": item.get("combined_score", item.get("dense_score")),
    }


def doc_chunk_id(doc_item: Dict[str, Any]) -> str:
    return str(doc_item.get("chunk_id") or "").strip()


def dedupe_doc_items(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()
    for row in rows:
        chunk_id = doc_chunk_id(row)
        if not chunk_id or chunk_id in seen:
            continue
        seen.add(chunk_id)
        out.append(row)
    return out


def seed_doc_candidates(rows: Sequence[Dict[str, Any]], max_seed_docs: int) -> List[Dict[str, Any]]:
    seeds: List[Dict[str, Any]] = []
    seen_docs: Set[str] = set()
    cap = clamp_int(max_seed_docs, 1, 10)
    for row in rows:
        doc_id = str(row.get("doc_id") or "").strip()
        if not doc_id or doc_id in seen_docs:
            continue
        seen_docs.add(doc_id)
        seeds.append(row)
        if len(seeds) >= cap:
            break
    return seeds


def neighbor_rank(seed: Dict[str, Any], candidate: Dict[str, Any]) -> float:
    score = 0.0
    seed_heading = normalize_heading_path(seed.get("heading_path"))
    cand_heading = normalize_heading_path(candidate.get("heading_path"))
    if seed_heading and cand_heading and seed_heading == cand_heading:
        score += 4.0

    seed_idx = seed.get("chunk_index")
    cand_idx = candidate.get("chunk_index")
    if isinstance(seed_idx, int) and isinstance(cand_idx, int):
        score += max(0.0, 3.0 - (0.5 * abs(seed_idx - cand_idx)))
    elif cand_heading:
        score += 0.5
    return score


def expand_doc_neighbors_for_seed(
    state,
    seed: Dict[str, Any],
    existing_chunk_ids: Set[str],
    per_doc_expansion: int,
    collection_name: str,
) -> List[Dict[str, Any]]:
    doc_id = str(seed.get("doc_id") or "").strip()
    if not doc_id:
        return []

    per_doc_cap = clamp_int(per_doc_expansion, 1, 8)
    fetch_limit = min(96, max(16, per_doc_cap * 12))
    try:
        points, _ = state.search_svc.qdrant.scroll(
            collection_name=collection_name,
            scroll_filter={"must": [{"key": "document_id", "match": {"value": doc_id}}]},
            with_payload=True,
            with_vectors=False,
            limit=fetch_limit,
        )
    except Exception:
        return []

    candidates: List[Dict[str, Any]] = []
    for point in points or []:
        payload = getattr(point, "payload", {}) or {}
        item = normalize_doc_item({"id": getattr(point, "id", ""), "payload": payload})
        chunk_id = doc_chunk_id(item)
        if not chunk_id or chunk_id in existing_chunk_ids:
            continue
        candidates.append(item)

    candidates.sort(key=lambda row: (neighbor_rank(seed, row), float(row.get("score") or 0.0)), reverse=True)
    selected = candidates[:per_doc_cap]
    for row in selected:
        cid = doc_chunk_id(row)
        if cid:
            existing_chunk_ids.add(cid)
    return selected


def expand_doc_neighbors(
    state,
    doc_results: Sequence[Dict[str, Any]],
    max_seed_docs: int,
    per_doc_expansion: int,
    collection_name: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    seeds = seed_doc_candidates(doc_results, max_seed_docs=max_seed_docs)
    if not seeds:
        return [], {"seed_doc_count": 0, "expanded_chunk_count": 0}

    existing_chunk_ids = {doc_chunk_id(row) for row in doc_results if doc_chunk_id(row)}
    expanded: List[Dict[str, Any]] = []
    for seed in seeds:
        expanded.extend(
            expand_doc_neighbors_for_seed(
                state=state,
                seed=seed,
                existing_chunk_ids=existing_chunk_ids,
                per_doc_expansion=per_doc_expansion,
                collection_name=collection_name,
            )
        )

    expanded = dedupe_doc_items(expanded)
    return expanded, {"seed_doc_count": len(seeds), "expanded_chunk_count": len(expanded)}


def normalize_citation_items(items: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()

    for raw in items:
        key = (
            raw.get("kind"),
            raw.get("doc_id"),
            raw.get("chunk_id"),
            raw.get("path"),
            raw.get("line_range"),
            raw.get("source_url"),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "kind": raw.get("kind") or "generic",
                "doc_id": raw.get("doc_id"),
                "chunk_id": raw.get("chunk_id"),
                "source_url": raw.get("source_url"),
                "heading_path": raw.get("heading_path"),
                "updated_at": raw.get("updated_at"),
                "paragraph_range": raw.get("paragraph_range"),
                "path": raw.get("path"),
                "line_range": raw.get("line_range"),
                "note": raw.get("note"),
            }
        )

    return out


def parse_query_or_regex(text: str) -> Tuple[str, bool]:
    q = (text or "").strip()
    if q.startswith("re:"):
        return q[3:].strip(), True
    if len(q) >= 3 and q.startswith("/") and q.endswith("/"):
        return q[1:-1], True
    return q, False


def qdrant_point_id(value: str) -> Any:
    text = (value or "").strip()
    if text.isdigit():
        return int(text)
    return text


def is_subpath(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False


def decode_file(raw: bytes) -> str:
    return decode_bytes(raw, TEXT_ENCODING_FALLBACKS)


def build_citations(doc_chunks: Sequence[Dict[str, Any]], code_windows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    citation_items: List[Dict[str, Any]] = []
    for chunk in doc_chunks:
        citation_items.append(
            {
                "kind": "doc",
                "doc_id": chunk.get("doc_id"),
                "chunk_id": chunk.get("chunk_id"),
                "source_url": chunk.get("source_url"),
                "heading_path": chunk.get("heading_path"),
                "updated_at": chunk.get("updated_at"),
                "paragraph_range": chunk.get("paragraph_range"),
            }
        )
    for window in code_windows:
        citation_items.append(
            {
                "kind": "code",
                "path": window.get("path"),
                "line_range": window.get("line_range"),
            }
        )
    return normalize_citation_items(citation_items)


def is_safe_regex(pattern: str) -> bool:
    raw = str(pattern or "").strip()
    if not raw:
        return False
    if len(raw) > 256:
        return False
    danger = [r"\([^)]*[+*][^)]*\)[+*]", r"\+\+", r"\*\*", r"\{\d+,\d*}\{"]
    for token in danger:
        if re.search(token, raw):
            return False
    return True


async def submit_feedback(redis_client, question: str, answer: str, rating: int, tags: Sequence[str]) -> Dict[str, Any]:
    normalized_tags = []
    for tag in tags:
        normalized = re.sub(r"\s+", "_", str(tag or "").strip().lower())
        if normalized and normalized not in normalized_tags:
            normalized_tags.append(normalized)

    payload = {
        "question": question,
        "answer": answer,
        "rating": normalize_feedback_rating(rating),
        "tags": normalized_tags,
        "created_at": utc_now_iso(),
    }

    stored = False
    if redis_client is not None:
        try:
            await redis_client.rpush("tool_api:feedback", json.dumps(payload, ensure_ascii=False))
            stored = True
        except Exception:
            stored = False

    return {"accepted": True, "stored": stored, "feedback": payload}

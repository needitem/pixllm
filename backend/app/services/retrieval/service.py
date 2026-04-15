import re
import time
from typing import Dict, List

from ... import config, wiki_config
from ..search.filters import apply_module_filter
from .query_rewrite import build_query_rewrite


def encode_query(embed_model, query: str):
    out = embed_model.encode(
        [query],
        batch_size=1,
        max_length=8192,
        return_dense=True,
        return_sparse=True,
    )
    dense = out["dense_vecs"][0].tolist()
    sparse_raw_list = out.get("lexical_weights") or out.get("sparse_vecs")
    sparse = None
    if sparse_raw_list is not None:
        sparse_raw = sparse_raw_list[0]
        if isinstance(sparse_raw, dict):
            indices = [int(i) for i in sparse_raw.keys()]
            values = [float(v) for v in sparse_raw.values()]
            sparse = {"indices": indices, "values": values}
        elif hasattr(sparse_raw, "indices"):
            idx = sparse_raw.indices
            val = sparse_raw.values
            sparse = {
                "indices": idx.tolist() if hasattr(idx, "tolist") else list(idx),
                "values": val.tolist() if hasattr(val, "tolist") else list(val),
            }
    return dense, sparse


def run_retrieval(search_svc, request, embed_model):
    t0 = time.perf_counter()
    raw_query = getattr(request, "message", None) or getattr(request, "query", None) or ""
    query_text = str(raw_query or "").strip()
    query_rewrite_enabled = wiki_config.retrieval_query_rewrite_enabled()
    query_rewrite_max_candidates = wiki_config.retrieval_query_rewrite_max_candidates()
    rewrite_plan = build_query_rewrite(
        query_text,
        max_candidates=query_rewrite_max_candidates if query_rewrite_enabled else 1,
    )
    query_candidates = [c.query for c in rewrite_plan.candidates] or [query_text]

    filters = {}
    language_filter = getattr(request, "language_filter", None)
    if language_filter:
        filters["language"] = language_filter
    req_filters = getattr(request, "filters", None)
    if isinstance(req_filters, dict):
        for k, v in req_filters.items():
            if k not in ("must", "should", "must_not"):
                filters[k] = v
    use_reranker = getattr(request, "use_reranker", False)
    collection = getattr(request, "collection", None) or config.EVIDENCE_DEFAULT_COLLECTION

    def _search(candidate_query: str, candidate_dense, candidate_sparse, active_filters):
        qdrant_filters = active_filters if active_filters else None
        if use_reranker:
            return search_svc.rerank_search(
                collection=collection,
                query=candidate_query,
                dense_vec=candidate_dense,
                sparse_vec=candidate_sparse,
                top_k=request.top_k,
                filters=qdrant_filters,
            )
        return search_svc.vector_search(
            collection=collection,
            dense_vec=candidate_dense,
            sparse_vec=candidate_sparse,
            top_k=request.top_k,
            filters=qdrant_filters,
            query_text=candidate_query,
        )

    def _run_candidate_searches(active_filters):
        by_id: Dict[str, Dict] = {}
        ordered: List[Dict] = []
        for candidate_index, candidate_query in enumerate(query_candidates):
            candidate_dense, candidate_sparse = encode_query(embed_model, candidate_query)
            candidate_results = _search(candidate_query, candidate_dense, candidate_sparse, active_filters)
            for result_index, item in enumerate(candidate_results or []):
                key = str(item.get("id") or f"__candidate_{candidate_index}_{result_index}")
                if key in by_id:
                    continue
                by_id[key] = item
                ordered.append(item)
        return ordered

    results = _run_candidate_searches(filters)

    module_filter = getattr(request, "module_filter", None)
    results = apply_module_filter(results, module_filter)
    max_per_source = int(getattr(request, "max_per_source", 0) or 0)
    if max_per_source <= 0:
        max_per_source = 2
    results = dedupe_results(results, max_per_source=max_per_source)

    elapsed = (time.perf_counter() - t0) * 1000
    return results, [], elapsed


def run_code_tool_retrieval(code_tools, request):
    if code_tools is None:
        return [], 0.0

    raw_query = getattr(request, "message", None) or getattr(request, "query", None) or ""
    if not raw_query.strip():
        return [], 0.0

    top_k = int(getattr(request, "top_k", config.CODE_SEARCH_MAX_RESULTS))
    language_filter = getattr(request, "language_filter", None)

    return code_tools.search(
        query=raw_query,
        top_k=top_k,
        repo_filter=None,
        language_filter=language_filter,
    )


def _normalize_chunk_text(text: str) -> str:
    t = (text or "").strip().lower()
    if not t:
        return ""
    t = re.sub(r"\s+", " ", t)
    if len(t) > 700:
        t = t[:420] + " ... " + t[-220:]
    return t


def dedupe_results(results: List[Dict], max_per_source: int = 2) -> List[Dict]:
    if not results:
        return []

    per_source: Dict[str, int] = {}
    seen_fingerprints = set()
    deduped: List[Dict] = []

    # Preserve upstream ordering from the vector search or reranker. Scores may
    # still inform that ordering upstream, but this stage should not amplify
    # their importance by re-sorting again.
    for item in results:
        payload = item.get("payload", {}) if isinstance(item, dict) else {}
        source = str(payload.get("source_file") or payload.get("file_path") or item.get("id") or "")
        source = source.replace("\\", "/")
        if per_source.get(source, 0) >= max_per_source:
            continue

        chunk_norm = _normalize_chunk_text(str(payload.get("text") or ""))
        if chunk_norm:
            fingerprint = f"{source}::{chunk_norm}"
            if fingerprint in seen_fingerprints:
                continue
            seen_fingerprints.add(fingerprint)

        per_source[source] = per_source.get(source, 0) + 1
        deduped.append(item)

    return deduped

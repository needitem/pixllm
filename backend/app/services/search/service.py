import re
from typing import Dict, List, Optional, Tuple

from qdrant_client import QdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
    SparseVector as QdrantSparseVector,
)

from .reranker import RerankerService


class SearchService:
    def __init__(
        self,
        qdrant_url: str,
    ):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.reranker = None
        try:
            self.reranker = RerankerService()
        except Exception:
            pass

    def vector_search(
        self,
        collection: str,
        dense_vec: List[float],
        sparse_vec: Optional[Dict],
        top_k: int = 5,
        filters: Optional[Dict] = None,
        query_text: Optional[str] = None,
    ) -> List[Dict]:
        dense_weight, sparse_weight = self._score_weights(query_text)

        qdrant_filter = None
        if filters:
            conditions = [FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filters.items()]
            qdrant_filter = Filter(must=conditions)

        dense_response = self.qdrant.query_points(
            collection_name=collection,
            query=dense_vec,
            using="dense",
            limit=top_k * 2,
            query_filter=qdrant_filter,
            with_payload=True,
        )
        dense = dense_response.points

        sparse = []
        if sparse_vec:
            if isinstance(sparse_vec, dict) and "indices" in sparse_vec and "values" in sparse_vec:
                sv = QdrantSparseVector(indices=sparse_vec["indices"], values=sparse_vec["values"])
            else:
                sv = sparse_vec
            sparse_response = self.qdrant.query_points(
                collection_name=collection,
                query=sv,
                using="sparse",
                limit=top_k * 2,
                query_filter=qdrant_filter,
                with_payload=True,
            )
            sparse = sparse_response.points

        merged = {}
        for r in dense:
            merged[r.id] = {
                "id": r.id,
                "payload": r.payload,
                "dense_score": r.score,
                "sparse_score": 0.0,
                "combined_score": r.score * dense_weight,
            }
        for r in sparse:
            if r.id in merged:
                merged[r.id]["sparse_score"] = r.score
                merged[r.id]["combined_score"] = merged[r.id]["dense_score"] * dense_weight + r.score * sparse_weight
            else:
                merged[r.id] = {
                    "id": r.id,
                    "payload": r.payload,
                    "dense_score": 0.0,
                    "sparse_score": r.score,
                    "combined_score": r.score * sparse_weight,
                }

        ranked = list(merged.values())
        self._apply_identifier_boost(ranked, query_text)
        self._apply_phrase_boost(ranked, query_text)
        return sorted(ranked, key=lambda x: x["combined_score"], reverse=True)[:top_k]

    def rerank_search(
        self,
        collection: str,
        query: str,
        dense_vec: List[float],
        sparse_vec: Optional[Dict] = None,
        top_k: int = 5,
        filters: Optional[Dict] = None,
        use_reranker: bool = True,
    ) -> List[Dict]:
        candidates = self.vector_search(
            collection,
            dense_vec,
            sparse_vec,
            top_k=top_k * 2,
            filters=filters,
            query_text=query,
        )

        if use_reranker and self.reranker and candidates:
            docs = [c.get("payload", {}).get("text", "") for c in candidates]
            ranked = self.reranker.rerank(query, docs, top_k=top_k)
            return [candidates[idx] for idx, _score in ranked if idx < len(candidates)]

        return candidates[:top_k]

    def _score_weights(self, query_text: Optional[str]) -> Tuple[float, float]:
        q = (query_text or "").lower()
        symbol_hits = 0
        if re.search(r"[A-Z][a-z]+[A-Z][A-Za-z0-9_]*", query_text or ""):
            symbol_hits += 1
        if any(tok in q for tok in ["::", "_", ".", "(", ")"]):
            symbol_hits += 1
        if any(c.isdigit() for c in q):
            symbol_hits += 1

        if symbol_hits >= 1:
            return 0.45, 0.55
        return 0.7, 0.3

    def _apply_identifier_boost(self, results: List[Dict], query_text: Optional[str]) -> None:
        identifiers = self._extract_identifiers(query_text)
        if not identifiers:
            return

        for item in results:
            payload = item.get("payload", {}) if isinstance(item, dict) else {}
            haystack_parts = [
                payload.get("file_path", ""),
                payload.get("source_file", ""),
                payload.get("text", ""),
                payload.get("class_name", ""),
                payload.get("fqn", ""),
                " ".join(payload.get("symbols", []) or []),
            ]
            haystack = "\n".join([str(p) for p in haystack_parts if p]).lower()

            matched = 0
            for ident in identifiers:
                if ident in haystack:
                    matched += 1

            if matched:
                item["combined_score"] += min(0.24, 0.08 * matched)

    def _apply_phrase_boost(self, results: List[Dict], query_text: Optional[str]) -> None:
        phrases = self._extract_phrase_candidates(query_text)
        if not phrases:
            return

        for item in results:
            payload = item.get("payload", {}) if isinstance(item, dict) else {}
            body = str(payload.get("text") or "")
            if not body:
                continue
            haystack = re.sub(r"\s+", " ", body).strip().lower()
            if not haystack:
                continue

            exact_hits = 0
            token_hits = 0
            for phrase in phrases:
                normalized_phrase = re.sub(r"\s+", " ", phrase).strip().lower()
                if not normalized_phrase:
                    continue
                if normalized_phrase in haystack:
                    exact_hits += 1
                    continue
                tokens = [t for t in normalized_phrase.split(" ") if t]
                if len(tokens) >= 2 and all(t in haystack for t in tokens):
                    token_hits += 1

            if exact_hits or token_hits:
                item["combined_score"] += min(0.45, 0.18 * exact_hits + 0.06 * token_hits)

    def _extract_phrase_candidates(self, query_text: Optional[str]) -> List[str]:
        q = (query_text or "").strip()
        if not q:
            return []

        candidates: List[str] = []
        for m in re.finditer(r'"([^"\\]+)"|\'([^\'\\]+)\'', q):
            phrase = (m.group(1) or m.group(2) or "").strip()
            if phrase:
                candidates.append(phrase)

        normalized_q = re.sub(r"\s+", " ", q).strip()
        if " " in normalized_q and len(normalized_q) >= 4:
            candidates.append(normalized_q)

        seen = set()
        out: List[str] = []
        for phrase in candidates:
            key = phrase.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(phrase)
        return out

    def _extract_identifiers(self, query_text: Optional[str]) -> List[str]:
        q = (query_text or "").strip()
        if not q:
            return []

        tokens = set()
        for tok in re.findall(r"\b[A-Za-z][A-Za-z0-9_]{2,}\b", q):
            if any(c.isupper() for c in tok[1:]) or "_" in tok or any(c.isdigit() for c in tok):
                tokens.add(tok.lower())

        return sorted(tokens)

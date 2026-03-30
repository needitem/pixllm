from typing import List, Tuple

from FlagEmbedding import FlagReranker


class RerankerService:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.model = FlagReranker(model_name, use_fp16=True)

    def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Tuple[int, float]]:
        scores = self.model.compute_score([[query, doc] for doc in documents])
        if isinstance(scores, float):
            scores = [scores]
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

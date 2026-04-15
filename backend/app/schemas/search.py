from typing import Dict, Optional, Literal
from pydantic import BaseModel

from .. import config


class SearchRequest(BaseModel):
    query: str
    collection: str = config.EVIDENCE_DEFAULT_COLLECTION
    source_mode: Literal["docs", "code"] = "docs"
    top_k: int = 10
    page: int = 1
    per_page: int = 10
    max_per_source: int = 0
    use_reranker: bool = False
    filters: Optional[Dict] = None
    language_filter: Optional[str] = None
    module_filter: Optional[str] = None

from typing import List, Optional

from pydantic import BaseModel


class WikiContextRequest(BaseModel):
    wiki_id: str


class WikiRebuildIndexRequest(BaseModel):
    wiki_id: str


class WikiSearchRequest(BaseModel):
    wiki_id: str
    query: Optional[str] = None
    limit: int = 12
    include_content: bool = False
    kind: Optional[str] = None


class WikiReadPageRequest(BaseModel):
    wiki_id: str
    path: str


class WikiWritePageRequest(BaseModel):
    wiki_id: str
    path: str
    content: str
    title: Optional[str] = None
    kind: Optional[str] = None


class WikiLintRequest(BaseModel):
    wiki_id: str
    repair: bool = False


class WikiWritebackRequest(BaseModel):
    wiki_id: str
    query: str
    answer: str
    title: Optional[str] = None
    category: str = "analysis"
    path: Optional[str] = None
    source_paths: List[str] = []

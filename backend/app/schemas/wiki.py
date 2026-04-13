from typing import List, Optional

from pydantic import BaseModel


class WikiBootstrapRequest(BaseModel):
    wiki_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    overwrite: bool = False
    user_id: Optional[str] = None


class WikiContextRequest(BaseModel):
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
    user_id: Optional[str] = None


class WikiAppendLogRequest(BaseModel):
    wiki_id: str
    title: str
    body_lines: List[str] = []
    kind: str = "update"
    user_id: Optional[str] = None

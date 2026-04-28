from typing import Optional

from pydantic import BaseModel


class SourceListRequest(BaseModel):
    path: Optional[str] = None
    depth: int = 1
    limit: int = 200


class SourceGlobRequest(BaseModel):
    pattern: str = "**/*"
    limit: int = 200


class SourceGrepRequest(BaseModel):
    pattern: str
    path_glob: Optional[str] = None
    regex: bool = False
    case_sensitive: bool = False
    limit: int = 50
    context: int = 2


class SourceSymbolSearchRequest(BaseModel):
    query: str
    limit: int = 20


class SourceSearchRequest(BaseModel):
    query: Optional[str] = None
    limit: int = 12
    include_content: bool = False
    kind: Optional[str] = None


class SourceReadRequest(BaseModel):
    path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None


class SourceAnswerRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    llm_base_url: Optional[str] = None
    session_id: Optional[str] = None
    max_tokens: int = 4096
    max_llm_calls: int = 12
    enable_thinking: bool = False

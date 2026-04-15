from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class UserContextRequest(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    groups: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)
    org_path: List[str] = Field(default_factory=list)
    workspace: Optional[str] = None
    session_id: Optional[str] = None


class CheckAccessRequest(BaseModel):
    user_id: Optional[str] = None
    action: str = "read"
    resource: str = "generic"
    resource_ids: List[str] = Field(default_factory=list)
    resource_id: Optional[str] = None


class SearchDocsRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    top_k: int = Field(default=50, ge=1, le=50)
    use_reranker: Optional[bool] = None
    session_id: Optional[str] = None


class OpenDocChunksRequest(BaseModel):
    chunk_ids: List[str] = Field(default_factory=list)
    max_chars: int = Field(default=4000, ge=200, le=12000)
    session_id: Optional[str] = None


class GetDocMetadataRequest(BaseModel):
    doc_id: str


class ListRepoFilesRequest(BaseModel):
    glob: str = "**/*"
    limit: int = Field(default=100, ge=1, le=500)
    session_id: Optional[str] = None


class SvnRepoRequest(BaseModel):
    workspace_path: str
    session_id: Optional[str] = None


class SvnStatusRequest(BaseModel):
    workspace_path: str
    path_filter: Optional[str] = None
    limit: int = Field(default=200, ge=1, le=500)
    session_id: Optional[str] = None


class SvnDiffRequest(BaseModel):
    workspace_path: str
    path_filter: Optional[str] = None
    max_chars: int = Field(default=12000, ge=200, le=20000)
    session_id: Optional[str] = None


class RunBuildRequest(BaseModel):
    workspace_path: str
    tool: Literal["msbuild", "dotnet", "cmake", "ninja", "custom"]
    project_or_solution: Optional[str] = None
    target: Optional[str] = None
    configuration: Optional[str] = None
    args: List[str] = Field(default_factory=list)
    timeout_sec: int = Field(default=600, ge=1, le=3600)
    max_chars: int = Field(default=12000, ge=500, le=40000)
    session_id: Optional[str] = None


class SearchCodeRequest(BaseModel):
    query_or_regex: str
    path_filter: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)
    session_id: Optional[str] = None


class ReadCodeRequest(BaseModel):
    path: str
    start_line: int = Field(default=1, ge=1)
    end_line: int = Field(default=200, ge=1)
    session_id: Optional[str] = None


class LookupSourcesAndCodeRequest(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    query: str
    filters: Optional[Dict[str, Any]] = None
    response_type: str = "general"
    workflow_first: bool = False
    top_k: int = Field(default=50, ge=1, le=50)
    limit: int = Field(default=50, ge=1, le=50)
    max_chars: int = Field(default=4000, ge=200, le=12000)
    max_line_span: int = Field(default=200, ge=1, le=500)


class CitationItem(BaseModel):
    kind: Literal["doc", "code", "generic"] = "generic"
    doc_id: Optional[str] = None
    chunk_id: Optional[str] = None
    source_url: Optional[str] = None
    heading_path: Optional[str] = None
    updated_at: Optional[str] = None
    paragraph_range: Optional[str] = None
    path: Optional[str] = None
    line_range: Optional[str] = None
    note: Optional[str] = None


class CiteBundleRequest(BaseModel):
    items: List[CitationItem] = Field(default_factory=list)


class SubmitFeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: int
    tags: List[str] = Field(default_factory=list)

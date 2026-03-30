from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .. import config


class ChatAttachment(BaseModel):
    kind: str = "file"
    name: str = ""
    path: str = ""
    content_type: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionBudget(BaseModel):
    max_steps: Optional[int] = None
    max_tool_calls: Optional[int] = None
    max_duration_sec: Optional[int] = None


class ExecutionRetryPolicy(BaseModel):
    max_attempts: int = 1
    retry_backoff_ms: int = 0
    retry_on_timeout: bool = True
    retry_on_runtime_error: bool = True


class ChatRequest(BaseModel):
    message: str
    model: str = config.VLLM_MODEL
    conversation_id: Optional[str] = None
    collection: str = config.RAG_DEFAULT_COLLECTION
    top_k: int = 50
    use_reranker: bool = False
    language_filter: Optional[str] = None
    module_filter: Optional[str] = None
    workspace_id: Optional[str] = None
    task_type: Optional[str] = None
    goal: Optional[str] = None
    client_metadata: Dict[str, Any] = Field(default_factory=dict)
    attachments: List[ChatAttachment] = Field(default_factory=list)
    approval_mode: str = "manual"
    budget: Optional[ExecutionBudget] = None
    tool_scope: List[str] = Field(default_factory=list)
    retry_policy: Optional[ExecutionRetryPolicy] = None
    resume_run_id: Optional[str] = None
    resume_from_task_key: Optional[str] = None
    resume_from_step_key: Optional[str] = None


class IntentVerifyRequest(BaseModel):
    message: str
    model: Optional[str] = None
    workspace_id: Optional[str] = None
    task_type: Optional[str] = None
    goal: Optional[str] = None
    client_metadata: Dict[str, Any] = Field(default_factory=dict)
    attachments: List[ChatAttachment] = Field(default_factory=list)
    approval_mode: str = "manual"
    budget: Optional[ExecutionBudget] = None
    tool_scope: List[str] = Field(default_factory=list)
    retry_policy: Optional[ExecutionRetryPolicy] = None
    resume_run_id: Optional[str] = None
    resume_from_task_key: Optional[str] = None
    resume_from_step_key: Optional[str] = None

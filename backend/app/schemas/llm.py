from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .. import config


class LlmChatMessage(BaseModel):
    role: str
    content: str


class LlmChatCompletionRequest(BaseModel):
    model: str = config.VLLM_MODEL
    messages: List[LlmChatMessage] = Field(default_factory=list)
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    tool_choice: Optional[Any] = None
    max_tokens: int = 1200
    temperature: float = 0.2
    response_format: Optional[str] = None
    stop: List[str] = Field(default_factory=list)


class LlmChatCompletionResponse(BaseModel):
    text: str = ""
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    finish_reason: str = ""
    usage: Dict[str, Any] = Field(default_factory=dict)


class LlmTokenizeRequest(BaseModel):
    model: str = config.VLLM_MODEL
    messages: List[LlmChatMessage] = Field(default_factory=list)
    return_token_strs: bool = False


class LlmTokenizeResponse(BaseModel):
    count: int = 0
    max_model_len: int = 0
    tokens: List[int] = Field(default_factory=list)
    token_strs: List[str] = Field(default_factory=list)

from dataclasses import dataclass
from typing import Any, Dict, Optional, TYPE_CHECKING

from .... import config
from ..react.engine import run_react_chat_generation
from ..workspace_analysis import collect_workspace_snapshot
from .base import ChatExecutionBackends, SourcesCallback, StatusCallback, TokenCallback, ToolCallback

if TYPE_CHECKING:
    from ..preparation import PreparedChatExecution


@dataclass
class DefaultReasoningBackend:
    chat_deps: Any

    async def run_react_generation(
        self,
        prepared: "PreparedChatExecution",
        *,
        status_callback: StatusCallback = None,
        token_callback: TokenCallback = None,
        sources_callback: SourcesCallback = None,
        tool_callback: ToolCallback = None,
    ) -> Dict[str, Any]:
        return await run_react_chat_generation(
            chat_deps=self.chat_deps,
            req=prepared.req,
            clean_message=prepared.clean_message,
            response_type=prepared.resolved.response_type,
            intent_source=str(prepared.intent_resolution.get("source") or ""),
            intent_confidence=float(prepared.intent_resolution.get("confidence", 0.0) or 0.0),
            retrieval_bias=str(prepared.intent_resolution.get("retrieval_bias") or ""),
            answer_style=str(prepared.intent_resolution.get("answer_style") or ""),
            question_contract=dict(prepared.intent_resolution.get("question_contract") or {}),
            history_messages=prepared.history_messages,
            model_name=prepared.req.model or config.VLLM_MODEL,
            max_tokens=prepared.max_tokens,
            temperature=prepared.temperature,
            system_prompt_seed=prepared.resolved.system_prompt,
            session_id=prepared.session_id,
            progress_callback=status_callback,
            token_callback=token_callback,
            sources_callback=sources_callback,
            tool_callback=tool_callback,
        )


@dataclass
class DefaultWorkspaceBackend:
    redis: Any
    code_tools: Any

    async def collect_snapshot(
        self,
        prepared: "PreparedChatExecution",
        *,
        workspace_path: str,
        path_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await collect_workspace_snapshot(
            redis=self.redis,
            code_tools=self.code_tools,
            workspace_path=workspace_path,
            session_id=prepared.session_id,
            path_filter=path_filter,
        )


def build_default_chat_backends(chat_deps: Any) -> ChatExecutionBackends:
    return ChatExecutionBackends(
        reasoning=DefaultReasoningBackend(chat_deps=chat_deps),
        workspace=DefaultWorkspaceBackend(redis=chat_deps.redis, code_tools=chat_deps.code_tools),
    )

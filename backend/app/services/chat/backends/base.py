from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ..preparation import PreparedChatExecution


StatusCallback = Optional[Callable[[Dict[str, Any]], Awaitable[None] | None]]
TokenCallback = Optional[Callable[[str], Awaitable[None] | None]]
SourcesCallback = Optional[Callable[[List[Dict[str, Any]]], Awaitable[None] | None]]
ToolCallback = Optional[Callable[[str, Dict[str, Any], str], Awaitable[None] | None]]


class ReasoningBackendProtocol(Protocol):
    async def run_react_generation(
        self,
        prepared: "PreparedChatExecution",
        *,
        status_callback: StatusCallback = None,
        token_callback: TokenCallback = None,
        sources_callback: SourcesCallback = None,
        tool_callback: ToolCallback = None,
    ) -> Dict[str, Any]:
        ...


class WorkspaceBackendProtocol(Protocol):
    async def collect_snapshot(
        self,
        prepared: "PreparedChatExecution",
        *,
        workspace_path: str,
        path_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        ...


@dataclass
class ChatExecutionBackends:
    reasoning: ReasoningBackendProtocol
    workspace: WorkspaceBackendProtocol

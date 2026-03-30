"""
Tool registry for the ReAct agent loop.

Each tool is registered with a name, callable, description, parameter schema,
and an output character cap.  The registry generates both:
  - A text prompt block (fallback / debug)
  - An OpenAI-compatible `tools` JSON schema for native function calling
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ToolParam:
    name: str
    type: str           # "string", "integer", "array", "boolean"
    description: str
    required: bool = True
    default: Any = None
    items_type: str = "string"   # for type == "array"


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: List[ToolParam] = field(default_factory=list)
    func: Optional[Callable[..., Coroutine]] = None
    max_output_chars: int = 4000   # per-tool output cap


class ToolRegistry:
    """Register tools and produce LLM-readable schema (text or OpenAI JSON)."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        func: Callable[..., Coroutine],
        description: str,
        parameters: Optional[List[ToolParam]] = None,
        max_output_chars: int = 4000,
    ) -> None:
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters or [],
            func=func,
            max_output_chars=max_output_chars,
        )

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    # ------------------------------------------------------------------
    # OpenAI native function calling schema
    # ------------------------------------------------------------------

    def get_openai_tools_schema(self) -> List[Dict[str, Any]]:
        """Return an OpenAI-compatible `tools` list for chat.completions.create()."""
        tools = []
        for tool in self._tools.values():
            properties: Dict[str, Any] = {}
            required_fields: List[str] = []

            for p in tool.parameters:
                if p.type == "array":
                    prop = {
                        "type": "array",
                        "description": p.description,
                        "items": {"type": p.items_type},
                    }
                else:
                    prop = {"type": p.type, "description": p.description}
                    if p.default is not None and not p.required:
                        prop["default"] = p.default
                properties[p.name] = prop
                if p.required:
                    required_fields.append(p.name)

            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": properties,
                            "required": required_fields,
                        },
                    },
                }
            )
        return tools

    # ------------------------------------------------------------------
    # Fallback text prompt (used when model does not support tool calling)
    # ------------------------------------------------------------------

    def get_tools_prompt(self) -> str:
        """Generate a text block listing all tools (fallback for non-tool-call models)."""
        if not self._tools:
            return ""

        lines: List[str] = []
        for tool in self._tools.values():
            params_desc = []
            for p in tool.parameters:
                req = " (required)" if p.required else f" (optional, default={p.default})"
                params_desc.append(f"  - {p.name} ({p.type}){req}: {p.description}")
            params_block = "\n".join(params_desc) if params_desc else "  (no parameters)"
            lines.append(f"### {tool.name}\n{tool.description}\nParameters:\n{params_block}")

        return "\n\n".join(lines)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a registered tool by name and return a string observation."""
        tool = self._tools.get(tool_name)
        if tool is None:
            return f"Error: unknown tool '{tool_name}'. Available: {', '.join(self._tools.keys())}"
        if tool.func is None:
            return f"Error: tool '{tool_name}' has no implementation"

        try:
            result = await tool.func(**tool_input)
            if isinstance(result, str):
                raw = result
            elif isinstance(result, (dict, list)):
                raw = json.dumps(result, ensure_ascii=False, default=str)
            else:
                raw = str(result)
        except TypeError as exc:
            return f"Error calling {tool_name}: {exc}"
        except Exception as exc:
            logger.warning("Tool execution error: %s(%s)", tool_name, tool_input, exc_info=True)
            return f"Error: {type(exc).__name__}: {str(exc)[:200]}"

        # Per-tool output cap
        cap = max(500, int(tool.max_output_chars))
        if len(raw) > cap:
            raw = raw[:cap] + f"\n... (truncated at {cap} chars)"
        return raw

import json
from typing import Any, Dict, List, Optional

from ... import config
from ...envelopes import ApiError
from . import service as source_service


def _to_text(value: Any) -> str:
    return str(value or "").strip()


def _clip(value: Any, limit: int = 4000) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return f"{text[: max(0, limit - 15)]}\n...[truncated]"


def _safe_int(value: Any, default: int, low: int, high: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        parsed = default
    return max(low, min(parsed, high))


def _normalize_tool_args(params: Any) -> Dict[str, Any]:
    if isinstance(params, dict):
        return params
    if isinstance(params, str):
        try:
            parsed = json.loads(params) if params.strip() else {}
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {"pattern": params}
    return {}


def _ensure_model_server(value: str) -> str:
    base = _to_text(value).rstrip("/") or _to_text(config.LLM_BASE_URL).rstrip("/")
    if not base:
        raise ApiError("LLM_BASE_URL_MISSING", "llm_base_url is required for source answer")
    return base if base.endswith("/v1") else f"{base}/v1"


def _compact_symbol(item: Dict[str, Any]) -> Dict[str, Any]:
    declaration = _to_text(item.get("declaration"))
    return {
        "symbol": _to_text(item.get("symbol")),
        "type_name": _to_text(item.get("type_name")),
        "member_name": _to_text(item.get("member_name")),
        "declaration": declaration,
        "path": _to_text(item.get("path")),
        "source_refs": item.get("source_refs") if isinstance(item.get("source_refs"), list) else [],
        "score": int(item.get("score") or 0),
    }


def _json_for_model(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _message_content(message: Dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(_to_text(item.get("text") if isinstance(item, dict) else item) for item in content)
    return _to_text(content)


def _message_has_tool_request(message: Dict[str, Any]) -> bool:
    return bool(message.get("function_call") or message.get("tool_calls"))


def _is_tool_result_message(message: Dict[str, Any]) -> bool:
    return _to_text(message.get("role")).lower() in {"function", "tool", "observation"}


def _extract_final_answer(messages: List[Dict[str, Any]]) -> str:
    saw_tool_result_after_candidate = False
    for message in reversed(messages or []):
        role = _to_text(message.get("role")).lower()
        if _is_tool_result_message(message):
            saw_tool_result_after_candidate = True
            continue
        if role != "assistant":
            continue
        if _message_has_tool_request(message):
            saw_tool_result_after_candidate = True
            continue
        content = _message_content(message).strip()
        if content:
            if saw_tool_result_after_candidate:
                return ""
            return content
    return ""


def _build_system_prompt() -> str:
    return "\n".join(
        [
            "You are the PIXLLM backend source agent.",
            "Inspect the source tree with ls/glob/grep/read/symbol tools, then answer from what you found.",
            "Choose the search path yourself from the available source tools.",
            "Use the user's requested language for examples. If source declarations use another binding syntax, adapt conservatively from observed signatures.",
            "Do not invent methods, properties, enum literals, or owner types. Concrete API calls must be backed by source tools.",
            "If the source is insufficient, state the specific missing piece instead of filling it with a guessed API.",
            "Keep tool/search details out of the final answer unless the user asks for logs.",
        ]
    )


class _TraceRecorder:
    def __init__(self) -> None:
        self.items: List[Dict[str, Any]] = []

    def append(self, tool: str, arguments: Dict[str, Any], result: Dict[str, Any], phase: str = "tool") -> None:
        self.items.append(
            {
                "phase": phase,
                "tool": tool,
                "input": arguments,
                "ok": result.get("ok", True) is not False,
                "summary": {
                    "path": _to_text(result.get("path")),
                    "pattern": _to_text(result.get("pattern")),
                    "query": _to_text(result.get("query")),
                    "total": result.get("total"),
                    "error": _to_text(result.get("error")),
                },
                "observation": result,
            }
        )


def _make_tools(trace: _TraceRecorder):
    try:
        from qwen_agent.tools.base import BaseTool
    except Exception as exc:
        raise ApiError(
            "QWEN_AGENT_UNAVAILABLE",
            f"qwen-agent is not available in backend python: {exc}",
            status_code=500,
        ) from exc

    class SourceOverviewTool(BaseTool):
        name = "source_overview"
        description = "Return source root, file count, top-level directories, and index status."
        parameters = {"type": "object", "properties": {}, "required": []}

        def call(self, params: Any, **kwargs: Any) -> str:
            del params, kwargs
            result = source_service.get_context()
            trace.append("source_overview", {}, result)
            return _json_for_model(result)

    class SourceLsTool(BaseTool):
        name = "source_ls"
        description = "List source directories/files under RAW_SOURCE_ROOT."
        parameters = {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Optional Source/... directory"},
                "depth": {"type": "integer", "description": "Directory recursion depth"},
                "limit": {"type": "integer", "description": "Maximum returned entries"},
            },
            "required": [],
        }

        def call(self, params: Any, **kwargs: Any) -> str:
            del kwargs
            arguments = _normalize_tool_args(params)
            result = source_service.list_source(
                _to_text(arguments.get("path") or arguments.get("pattern")),
                depth=_safe_int(arguments.get("depth"), 1, 0, 8),
                limit=_safe_int(arguments.get("limit"), 200, 1, 1000),
            )
            trace.append("source_ls", arguments, result)
            return _json_for_model(result)

    class SourceGlobTool(BaseTool):
        name = "source_glob"
        description = "Find source files by glob pattern."
        parameters = {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern relative to Source/"},
                "limit": {"type": "integer", "description": "Maximum returned files"},
            },
            "required": ["pattern"],
        }

        def call(self, params: Any, **kwargs: Any) -> str:
            del kwargs
            arguments = _normalize_tool_args(params)
            result = source_service.glob_source(
                _to_text(arguments.get("pattern")) or "**/*",
                limit=_safe_int(arguments.get("limit"), 200, 1, 1000),
            )
            trace.append("source_glob", arguments, result)
            return _json_for_model(result)

    class SourceGrepTool(BaseTool):
        name = "source_grep"
        description = "Search source text across files."
        parameters = {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Literal text or regex"},
                "path_glob": {"type": "string", "description": "Optional file glob filter"},
                "regex": {"type": "boolean", "description": "Treat pattern as regex"},
                "case_sensitive": {"type": "boolean", "description": "Case-sensitive search"},
                "limit": {"type": "integer", "description": "Maximum matches"},
                "context": {"type": "integer", "description": "Context lines around each match"},
            },
            "required": ["pattern"],
        }

        def call(self, params: Any, **kwargs: Any) -> str:
            del kwargs
            arguments = _normalize_tool_args(params)
            result = source_service.grep_source(
                _to_text(arguments.get("pattern")),
                path_glob=_to_text(arguments.get("path_glob")),
                regex=bool(arguments.get("regex")),
                case_sensitive=bool(arguments.get("case_sensitive")),
                limit=_safe_int(arguments.get("limit"), 50, 1, 500),
                context=_safe_int(arguments.get("context"), 2, 0, 8),
            )
            trace.append("source_grep", arguments, result)
            return _json_for_model(result)

    class SourceReadTool(BaseTool):
        name = "source_read"
        description = "Read a source file span or indexed symbol target returned by a source tool."
        parameters = {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Source/... path or .runtime/methods_index.json#Symbol"},
                "start_line": {"type": "integer", "description": "Optional start line"},
                "end_line": {"type": "integer", "description": "Optional end line"},
            },
            "required": ["path"],
        }

        def call(self, params: Any, **kwargs: Any) -> str:
            del kwargs
            arguments = _normalize_tool_args(params)
            result = source_service.read_source(
                _to_text(arguments.get("path") or arguments.get("pattern")),
                start_line=arguments.get("start_line"),
                end_line=arguments.get("end_line"),
            )
            if not result:
                result = {"ok": False, "error": "source_path_not_found", "path": _to_text(arguments.get("path"))}
            else:
                result = {**result, "content": _clip(result.get("content"), 6000)}
            trace.append("source_read", arguments, result)
            return _json_for_model(result)

    class SourceSymbolSearchTool(BaseTool):
        name = "source_symbol_search"
        description = "Search generated declarations by symbol or declaration text."
        parameters = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Symbol/type/member/declaration terms"},
                "limit": {"type": "integer", "description": "Maximum returned symbols"},
            },
            "required": ["query"],
        }

        def call(self, params: Any, **kwargs: Any) -> str:
            del kwargs
            arguments = _normalize_tool_args(params)
            result = source_service.symbol_search(
                _to_text(arguments.get("query") or arguments.get("pattern")),
                limit=_safe_int(arguments.get("limit"), 20, 1, 100),
            )
            result = {
                **result,
                "results": [_compact_symbol(item) for item in result.get("results", [])[: _safe_int(arguments.get("limit"), 20, 1, 100)]],
            }
            trace.append("source_symbol_search", arguments, result)
            return _json_for_model(result)

    return [
        SourceOverviewTool(),
        SourceLsTool(),
        SourceGlobTool(),
        SourceGrepTool(),
        SourceReadTool(),
        SourceSymbolSearchTool(),
    ]


def answer_source_question(
    *,
    prompt: str,
    model: Optional[str] = None,
    llm_base_url: Optional[str] = None,
    session_id: Optional[str] = None,
    max_tokens: int = 4096,
    max_llm_calls: int = 12,
    enable_thinking: bool = False,
) -> Dict[str, Any]:
    normalized_prompt = _to_text(prompt)
    if not normalized_prompt:
        raise ApiError("EMPTY_PROMPT", "prompt is required")

    try:
        from qwen_agent.agents import Assistant
        import qwen_agent.agents.fncall_agent as fncall_agent
    except Exception as exc:
        raise ApiError(
            "QWEN_AGENT_UNAVAILABLE",
            f"qwen-agent is not available in backend python: {exc}",
            status_code=500,
        ) from exc

    trace = _TraceRecorder()
    fncall_agent.MAX_LLM_CALL_PER_RUN = _safe_int(max_llm_calls, 12, 1, 40)
    completion_token_budget = _safe_int(max_tokens, 4096, 256, 16384)
    model_cfg = {
        "model": _to_text(model) or config.DEFAULT_MODEL,
        "model_server": _ensure_model_server(llm_base_url or ""),
        "api_key": "EMPTY",
        "generate_cfg": {
            "temperature": 0.2,
            "max_tokens": completion_token_budget,
            "max_input_tokens": max(4096, min(24000, 32768 - completion_token_budget - 1024)),
            "extra_body": {
                "top_k": 20,
                "chat_template_kwargs": {"enable_thinking": bool(enable_thinking)},
            },
        },
    }
    bot = Assistant(
        llm=model_cfg,
        system_message=_build_system_prompt(),
        function_list=_make_tools(trace),
    )
    messages = [{"role": "user", "content": normalized_prompt}]

    last_messages: List[Dict[str, Any]] = []
    last_answer = ""
    for responses in bot.run(messages=messages):
        last_messages = responses or []
        answer = _extract_final_answer(last_messages)
        if answer:
            last_answer = answer

    final_answer = _extract_final_answer(last_messages) or last_answer
    if not final_answer:
        raise ApiError("LLM_EMPTY_ANSWER", "backend source agent did not produce an answer", status_code=502)

    return {
        "answer": final_answer,
        "session_id": _to_text(session_id),
        "model": model_cfg["model"],
        "llm_base_url": model_cfg["model_server"],
        "trace": trace.items,
        "summary": f"Completed by backend source agent with {len(trace.items)} source tool observations.",
        "usage": {
            "tool_calls": len(trace.items),
            "completion_calls": 1,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
    }

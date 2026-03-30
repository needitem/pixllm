"""
ReAct-style agent loop with OpenAI native function calling.

Execution modes (auto-detected):
  1. Native tool calling  — model returns finish_reason="tool_calls"
     Multiple tool_calls in one response are executed in PARALLEL via asyncio.gather.
  2. Text JSON fallback   — model returns plain JSON with "action"/"answer" keys
     Used when vLLM is configured without tool-call support or model doesn't emit tool_calls.
"""

import asyncio
import json
import logging
import re
from inspect import isawaitable
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .... import rag_config
from ....core.llm_utils import safe_chat_completion_create
from ...tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


async def _maybe_await_callback(callback, *args, **kwargs) -> None:
    if callback is None:
        return
    result = callback(*args, **kwargs)
    if isawaitable(result):
        await result


async def _run_answer_validator(answer_validator, answer: str, round_idx: int) -> Dict[str, Any]:
    if answer_validator is None:
        return {"ok": True, "answer": answer}
    result = answer_validator(answer, round_idx)
    if isawaitable(result):
        result = await result
    if not isinstance(result, dict):
        return {"ok": True, "answer": answer}
    if "answer" not in result:
        result["answer"] = answer
    if "ok" not in result:
        result["ok"] = True
    return result


async def _run_round_controller(round_controller, round_idx: int) -> Dict[str, Any]:
    if round_controller is None:
        return {}
    result = round_controller(round_idx)
    if isawaitable(result):
        result = await result
    return result if isinstance(result, dict) else {}


def _truncate_observation_for_prompt(observation: Any, max_chars: int = 2500) -> str:
    raw = str(observation or "")
    if len(raw) <= max_chars:
        return raw
    keep = max(128, max_chars - 128)
    return raw[:keep] + "\n...[truncated for prompt]..."


def _is_observation_message(message: Dict[str, Any]) -> bool:
    role = str(message.get("role") or "").strip().lower()
    if role == "tool":
        return True
    if role != "user":
        return False
    content = str(message.get("content") or "")
    return content.startswith("Observation")


_CONTROL_MESSAGE_PREFIXES = (
    "Retrieval is still in progress.",
    "More evidence is needed before answering.",
    "The draft answer is not grounded enough yet.",
    "The drafted answer still contains claims",
    "Tool call limit reached.",
    "Do not call unknown tools.",
    "If you are ready to answer, use the final answer field",
    "You must include either an \"action\"",
    "Unknown tool ",
    "Maximum rounds reached.",
    "Retrieval is exhausted.",
)


def _is_overlay_message(message: Dict[str, Any]) -> bool:
    return str(message.get("role") or "").strip().lower() == "user" and str(message.get("content") or "").startswith("[Local Workspace Evidence]")


def _is_control_message(message: Dict[str, Any]) -> bool:
    if str(message.get("role") or "").strip().lower() != "user":
        return False
    content = str(message.get("content") or "")
    return any(content.startswith(prefix) for prefix in _CONTROL_MESSAGE_PREFIXES)


def _compact_plain_text(text: Any, max_chars: int) -> str:
    raw = " ".join(str(text or "").split())
    if len(raw) <= max_chars:
        return raw
    return raw[: max(32, max_chars - 24)] + "...[truncated]"


def _summarize_tool_calls_for_prompt(message: Dict[str, Any], *, max_chars: int) -> str:
    pieces: List[str] = []
    content = _compact_plain_text(message.get("content"), min(max_chars, 320))
    if content:
        pieces.append(content)
    for item in list(message.get("tool_calls") or [])[:3]:
        function = dict(item.get("function") or {}) if isinstance(item, dict) else {}
        name = str(function.get("name") or "").strip()
        arguments = _compact_plain_text(function.get("arguments"), 160)
        if name:
            pieces.append(f"{name}({arguments})" if arguments else name)
    summary = " | ".join(piece for piece in pieces if piece)
    return _compact_plain_text(summary or "[assistant tool call]", max_chars)


def _normalize_message_for_prompt(message: Dict[str, Any], *, recent: bool) -> Optional[Dict[str, Any]]:
    role = str(message.get("role") or "").strip().lower()
    if role not in {"user", "assistant", "tool"}:
        return None

    if _is_overlay_message(message):
        return {
            "role": "user",
            "content": _compact_plain_text(message.get("content"), 1600 if recent else 800),
        }
    if _is_control_message(message):
        return {
            "role": "user",
            "content": _compact_plain_text(message.get("content"), 420 if recent else 180),
        }
    if role == "assistant" and list(message.get("tool_calls") or []):
        return {
            "role": "assistant",
            "content": _summarize_tool_calls_for_prompt(message, max_chars=520 if recent else 220),
        }
    if role == "tool":
        return {
            "role": "user",
            "content": "Observation: " + _compact_plain_text(message.get("content"), 1200 if recent else 240),
        }
    if _is_observation_message(message):
        return {
            "role": "user",
            "content": _compact_plain_text(message.get("content"), 1200 if recent else 240),
        }

    return {
        "role": role,
        "content": _compact_plain_text(message.get("content"), 1400 if recent else 420),
    }


def _compact_working_messages(
    messages: List[Dict[str, Any]],
    *,
    max_chars: int = 16000,
    max_messages: int = 22,
    keep_recent_messages: int = 10,
    keep_recent_dialogue: int = 4,
    keep_recent_control: int = 2,
) -> List[Dict[str, Any]]:
    if not messages:
        return []

    latest_overlay_idx = -1
    control_indices: List[int] = []
    dialogue_indices: List[int] = []
    user_dialogue_indices: List[int] = []
    for idx, item in enumerate(messages):
        if _is_overlay_message(item):
            latest_overlay_idx = idx
        elif _is_control_message(item):
            control_indices.append(idx)
        elif str(item.get("role") or "").strip().lower() in {"user", "assistant"} and not _is_observation_message(item):
            dialogue_indices.append(idx)
            if str(item.get("role") or "").strip().lower() == "user":
                user_dialogue_indices.append(idx)

    essential_indices = {len(messages) - 1}
    if latest_overlay_idx >= 0:
        essential_indices.add(latest_overlay_idx)
    essential_indices.update(control_indices[-keep_recent_control:])
    essential_indices.update(dialogue_indices[-keep_recent_dialogue:])
    essential_indices.update(user_dialogue_indices[-2:])

    normalized_rows: List[Dict[str, Any]] = []
    recent_cutoff = max(0, len(messages) - keep_recent_messages)
    for idx, item in enumerate(messages):
        if _is_overlay_message(item) and idx != latest_overlay_idx:
            continue
        if _is_control_message(item) and idx not in essential_indices:
            continue
        normalized = _normalize_message_for_prompt(item, recent=(idx >= recent_cutoff or idx in essential_indices))
        if not normalized or not str(normalized.get("content") or "").strip():
            continue
        normalized_rows.append(
            {
                "original_idx": idx,
                "essential": idx in essential_indices,
                "message": normalized,
            }
        )

    while len(normalized_rows) > max_messages:
        removable_idx = next((i for i, row in enumerate(normalized_rows) if not bool(row.get("essential"))), 0)
        normalized_rows.pop(removable_idx)

    def _total_chars(rows: List[Dict[str, Any]]) -> int:
        return sum(len(str(dict(row.get("message") or {}).get("content") or "")) for row in rows)

    if _total_chars(normalized_rows) > max_chars:
        for row in normalized_rows:
            if bool(row.get("essential")):
                continue
            row["message"]["content"] = _compact_plain_text(row["message"].get("content"), 180)
        while _total_chars(normalized_rows) > max_chars and len(normalized_rows) > 6:
            removable_idx = next((i for i, row in enumerate(normalized_rows) if not bool(row.get("essential"))), None)
            if removable_idx is None:
                break
            normalized_rows.pop(removable_idx)

    if _total_chars(normalized_rows) > max_chars:
        for row in normalized_rows[:-4]:
            row["message"]["content"] = _compact_plain_text(row["message"].get("content"), 240)

    return [dict(row.get("message") or {}) for row in normalized_rows]


_RESERVED_ANSWER_ACTIONS = {"answer", "final_answer", "respond", "response"}


def _is_reserved_answer_action(name: str) -> bool:
    return str(name or "").strip().lower() in _RESERVED_ANSWER_ACTIONS


def _extract_answer_candidate(*payloads: Any) -> str:
    preferred_keys = ("answer", "final_answer", "response", "content", "text", "message")
    for payload in payloads:
        if isinstance(payload, str) and payload.strip():
            return payload.strip()
        if not isinstance(payload, dict):
            continue
        for key in preferred_keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for nested_key in ("input", "arguments", "action_input"):
            nested = payload.get(nested_key)
            if isinstance(nested, dict):
                nested_value = _extract_answer_candidate(nested)
                if nested_value:
                    return nested_value
    return ""


def _compute_round_max_tokens(max_tokens: int) -> int:
    requested = max(256, int(max_tokens or 2048))
    return max(512, min(requested, 1536))


def _compute_final_max_tokens(max_tokens: int) -> int:
    requested = max(256, int(max_tokens or 2048))
    return max(1024, min(requested, 4096))


# ---------------------------------------------------------------------------
# Fallback system prompt (only used in text-JSON mode)
# ---------------------------------------------------------------------------

REACT_SYSTEM_TEMPLATE = """You are a helpful technical assistant.
You have access to the following tools to gather information before answering.

{tools_block}

## Response format
You MUST respond in JSON. Follow one of these two formats:

**When you need to use a tool:**
```json
{{
  "thought": "<your reasoning>",
  "action": "<tool_name>",
  "input": {{ <tool parameters> }}
}}
```

**When you are ready to give a final answer:**
```json
{{
  "thought": "<your reasoning>",
  "answer": "<your complete answer in Korean>"
}}
```

## Rules
- Gather sufficient evidence before answering. Use tools as needed.
- You may call multiple tools in sequence across turns.
- When enough evidence is collected, produce `answer`.
- Answer in Korean.
- Never fabricate information not found in tool results.
- Default to grounded prose. Do not include code blocks unless the exact snippet came from a directly read grounded result.
- If a claim depends on a specific file path, symbol, or code block that is not grounded yet, call another tool instead of writing a placeholder or a "needs confirmation" note.
- Never emit literal placeholders like `[grounding-required]`.
- If tool results are insufficient, say so honestly.
{extra_instructions}
"""

# System prompt used when native tool calling is active (no need for format instructions)
REACT_NATIVE_SYSTEM_TEMPLATE = """You are a helpful technical assistant.
Use the provided tools to gather relevant information before answering.

## Rules
- Call tools as needed to collect sufficient evidence.
- When you have enough information, produce a final answer in Korean.
- Never fabricate information not found in tool results.
- Default to grounded prose. Do not include code blocks unless the exact snippet came from a directly read grounded result.
- If a claim depends on a specific file path, symbol, or code block that is not grounded yet, call another tool instead of writing a placeholder or a "needs confirmation" note.
- Never emit literal placeholders like `[grounding-required]`.
- If tool results are insufficient, say so honestly.
{extra_instructions}
"""


# ---------------------------------------------------------------------------
# JSON extraction helper (fallback mode only)
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from a response that may contain markdown fences or extra text."""
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    m = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    return json.loads(text[start: i + 1])
                except json.JSONDecodeError:
                    start = -1

    return None


def _extract_textual_tool_calls(text: str) -> List[Dict[str, Any]]:
    """Extract tool-call payloads embedded as <tool_call>...</tool_call> blocks."""
    raw = str(text or "").strip()
    if not raw:
        return []

    matches = re.findall(r"<tool_call>\s*(\{[\s\S]*?\})\s*</tool_call>", raw, flags=re.IGNORECASE)
    calls: List[Dict[str, Any]] = []
    for block in matches:
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            continue
        tool_name = str(parsed.get("name") or parsed.get("action") or "").strip()
        tool_input = parsed.get("arguments", parsed.get("input", parsed.get("action_input", {})))
        if not tool_name:
            continue
        if not isinstance(tool_input, dict):
            tool_input = {}
        calls.append({"name": tool_name, "input": tool_input})
    return calls


async def _execute_textual_tool_calls(
    registry: ToolRegistry,
    textual_calls: List[Dict[str, Any]],
    on_tool_call: Optional[Callable[[str, Dict, str], None]],
    *,
    round_idx: int,
) -> List[Dict[str, Any]]:
    """Execute tool calls recovered from assistant text content."""

    async def _run_one(idx: int, item: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = str(item.get("name") or "").strip()
        tool_input = dict(item.get("input") or {})
        observation = await registry.execute(tool_name, tool_input)
        await _maybe_await_callback(on_tool_call, tool_name, tool_input, observation)
        return {
            "tool_call_id": f"textual-{round_idx}-{idx}",
            "tool_name": tool_name,
            "tool_input": tool_input,
            "observation": observation,
        }

    return await asyncio.gather(*[_run_one(idx, item) for idx, item in enumerate(textual_calls)])


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def build_system_prompt(
    registry: ToolRegistry,
    orchestration_prompt: str = "",
    extra_instructions: str = "",
    native_tool_calling: bool = True,
) -> str:
    """Create the system prompt with tool descriptions."""
    if orchestration_prompt:
        extra_instructions = f"{orchestration_prompt}\n{extra_instructions}"

    if native_tool_calling:
        return REACT_NATIVE_SYSTEM_TEMPLATE.format(extra_instructions=extra_instructions)

    tools_block = registry.get_tools_prompt()
    return REACT_SYSTEM_TEMPLATE.format(tools_block=tools_block, extra_instructions=extra_instructions)


# ---------------------------------------------------------------------------
# Parallel tool execution helper
# ---------------------------------------------------------------------------

async def _execute_tool_calls_parallel(
    registry: ToolRegistry,
    tool_calls: List[Any],           # openai ToolCall objects
    on_tool_call: Optional[Callable[[str, Dict, str], None]],
) -> List[Dict[str, Any]]:
    """Execute multiple tool calls concurrently and return observation records."""

    async def _run_one(tc) -> Dict[str, Any]:
        tool_name: str = tc.function.name
        try:
            tool_input = json.loads(tc.function.arguments or "{}")
        except json.JSONDecodeError:
            tool_input = {}
        if not isinstance(tool_input, dict):
            tool_input = {}

        observation = await registry.execute(tool_name, tool_input)
        await _maybe_await_callback(on_tool_call, tool_name, tool_input, observation)
        return {
            "tool_call_id": tc.id,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "observation": observation,
        }

    return await asyncio.gather(*[_run_one(tc) for tc in tool_calls])


# ---------------------------------------------------------------------------
# Main ReAct loop
# ---------------------------------------------------------------------------

async def run_react_loop(
    *,
    llm_call: Callable,
    registry: ToolRegistry,
    messages: List[Dict[str, str]],
    system_prompt: str,
    max_rounds: Optional[int] = None,
    max_tool_calls: Optional[int] = None,
    on_thought: Optional[Callable[[str], None]] = None,
    on_tool_call: Optional[Callable[[str, Dict, str], None]] = None,
    round_controller: Optional[Callable[[int], Awaitable[Dict[str, Any]] | Dict[str, Any]]] = None,
    answer_readiness_checker: Optional[Callable[[str, int], Awaitable[Dict[str, Any]] | Dict[str, Any]]] = None,
    answer_validator: Optional[Callable[[str, int], Awaitable[Dict[str, Any]] | Dict[str, Any]]] = None,
    phase_log=None,
    openai_client=None,
    model_name: Optional[str] = None,
    max_tokens: int = 2048,
    temperature: float = 0.2,
    completion_extra_body: Optional[Dict[str, Any]] = None,
    timeout_sec: Optional[float] = None,
) -> Dict[str, Any]:
    if max_rounds is None:
        max_rounds = rag_config.react_max_rounds()
    if max_tool_calls is None:
        max_tool_calls = rag_config.react_max_tool_calls()
    if timeout_sec is None:
        timeout_sec = rag_config.react_timeout_sec() or None
    else:
        timeout_sec = float(timeout_sec) if float(timeout_sec or 0) > 0 else None

    round_limit_enabled = int(max_rounds or 0) > 0
    tool_call_limit_enabled = int(max_tool_calls or 0) > 0
    use_native = openai_client is not None and model_name

    thoughts: List[str] = []
    tool_calls_log: List[Dict[str, Any]] = []
    working_messages: List[Dict[str, Any]] = list(messages)
    total_tool_calls = 0
    last_round_instruction = ''
    round_max_tokens = _compute_round_max_tokens(max_tokens)
    final_max_tokens = _compute_final_max_tokens(max_tokens)

    openai_tools_schema = registry.get_openai_tools_schema() if use_native else None

    async def _loop_body() -> Dict[str, Any]:
        nonlocal total_tool_calls
        nonlocal last_round_instruction

        round_idx = 0
        forced_final_prompt = ''

        def _tool_limit_hit(extra_calls: int = 0) -> bool:
            if not tool_call_limit_enabled:
                return False
            return total_tool_calls + int(extra_calls or 0) > int(max_tool_calls or 0)

        async def _finalize_answer_candidate(answer_text: str, assistant_content: str) -> Optional[Dict[str, Any]]:
            candidate = str(answer_text or "").strip()
            if not candidate:
                return None
            readiness = await _run_answer_validator(answer_readiness_checker, candidate, round_idx)
            if not bool(readiness.get('ok')):
                working_messages.append({'role': 'assistant', 'content': assistant_content or candidate})
                working_messages.append({
                    'role': 'user',
                    'content': str(
                        readiness.get('feedback')
                        or 'More evidence is needed before answering. Use more tools to close the remaining evidence gaps.'
                    ),
                })
                return None
            candidate = str(readiness.get('answer') or candidate)
            validation = await _run_answer_validator(answer_validator, candidate, round_idx)
            if not bool(validation.get('ok')):
                working_messages.append({'role': 'assistant', 'content': assistant_content or candidate})
                working_messages.append({
                    'role': 'user',
                    'content': str(
                        validation.get('feedback')
                        or 'The draft answer is not grounded enough yet. Use more tools to verify the missing file, symbol, or code span before answering.'
                    ),
                })
                return None
            return {
                'answer': str(validation.get('answer') or candidate),
                'thoughts': thoughts,
                'tool_calls': tool_calls_log,
                'rounds': round_idx + 1,
            }

        while True:
            if round_limit_enabled and round_idx >= int(max_rounds or 0):
                break

            round_control = await _run_round_controller(round_controller, round_idx)
            round_instruction = str(round_control.get('message') or '').strip()
            if round_instruction and round_instruction != last_round_instruction:
                working_messages.append({'role': 'user', 'content': round_instruction})
                last_round_instruction = round_instruction
            if bool(round_control.get('force_answer')) or bool(round_control.get('stop')):
                forced_final_prompt = round_instruction
                break

            if use_native:
                try:
                    prompt_messages = _compact_working_messages(working_messages)
                    _msgs = (
                        [{'role': 'system', 'content': system_prompt}] + prompt_messages
                        if prompt_messages and prompt_messages[0].get('role') != 'system'
                        else prompt_messages
                    )
                    completion = await asyncio.to_thread(
                        safe_chat_completion_create,
                        client=openai_client,
                        model=model_name,
                        messages=_msgs,
                        tools=openai_tools_schema,
                        tool_choice='auto',
                        max_tokens=round_max_tokens,
                        temperature=temperature,
                        **({'extra_body': completion_extra_body} if completion_extra_body else {}),
                    )
                except Exception as exc:
                    logger.error('LLM call failed in native ReAct round %d: %s', round_idx, exc)
                    return _error_result(thoughts, tool_calls_log, round_idx, str(exc))

                choice = completion.choices[0]
                finish_reason = choice.finish_reason
                msg = choice.message
                raw_content = str(msg.content or '')
                parsed_content = _extract_json(raw_content) if raw_content else None
                textual_tool_calls = _extract_textual_tool_calls(raw_content) if raw_content else []

                if msg.content:
                    thought_text = (
                        str(parsed_content.get('thought') or '').strip()
                        if isinstance(parsed_content, dict)
                        else str(msg.content)
                    )
                    thoughts.append(thought_text or str(msg.content))
                    await _maybe_await_callback(on_thought, thought_text or str(msg.content))

                if not msg.tool_calls and textual_tool_calls:
                    executable_textual_calls: List[Dict[str, Any]] = []
                    reserved_answer = ''
                    invalid_tool_names: List[str] = []
                    for item in textual_tool_calls:
                        tool_name = str(item.get('name') or '').strip()
                        if _is_reserved_answer_action(tool_name):
                            reserved_answer = reserved_answer or _extract_answer_candidate(item.get('input'), item)
                            continue
                        if registry.get_tool(tool_name) is None:
                            invalid_tool_names.append(tool_name)
                            continue
                        executable_textual_calls.append(item)

                    if reserved_answer and not executable_textual_calls:
                        answer_result = await _finalize_answer_candidate(reserved_answer, raw_content)
                        if answer_result is not None:
                            return answer_result
                        round_idx += 1
                        continue

                    if invalid_tool_names and not executable_textual_calls:
                        working_messages.append({'role': 'assistant', 'content': raw_content})
                        working_messages.append({
                            'role': 'user',
                            'content': (
                                'Do not call unknown tools. The available tools are: '
                                + ', '.join(registry.list_tools())
                                + '. If you are ready to respond, use the final answer format instead of an action named "answer".'
                            ),
                        })
                        round_idx += 1
                        continue

                    textual_tool_calls = executable_textual_calls
                    if _tool_limit_hit(len(textual_tool_calls)):
                        working_messages.append({'role': 'assistant', 'content': raw_content})
                        working_messages.append({'role': 'user', 'content': 'Tool call limit reached. Please produce an answer now based on the evidence you have gathered.'})
                        round_idx += 1
                        continue

                    results = await _execute_textual_tool_calls(
                        registry,
                        textual_tool_calls,
                        on_tool_call,
                        round_idx=round_idx,
                    )
                    total_tool_calls += len(results)

                    if phase_log is not None:
                        for res in results:
                            phase_log.retrieve(tool=res['tool_name'], round=round_idx, result_count=1)

                    working_messages.append({'role': 'assistant', 'content': raw_content})
                    for res in results:
                        prompt_observation = _truncate_observation_for_prompt(res['observation'])
                        tool_calls_log.append({
                            'round': round_idx,
                            'tool': res['tool_name'],
                            'input': res['tool_input'],
                            'output_preview': res['observation'][:500],
                        })
                        working_messages.append({
                            'role': 'user',
                            'content': f"Observation ({res['tool_name']}):\n{prompt_observation}",
                        })
                    round_idx += 1
                    continue

                if not msg.tool_calls and isinstance(parsed_content, dict):
                    final_answer = parsed_content.get('answer', parsed_content.get('final_answer'))
                    answer_result = await _finalize_answer_candidate(str(final_answer or ''), msg.content or raw_content or str(final_answer or ''))
                    if answer_result is not None:
                        return answer_result

                    action = parsed_content.get('action', '')
                    action_input = parsed_content.get('input', parsed_content.get('action_input', {}))
                    if _is_reserved_answer_action(action):
                        answer_candidate = _extract_answer_candidate(action_input, parsed_content)
                        answer_result = await _finalize_answer_candidate(answer_candidate, msg.content or raw_content or answer_candidate)
                        if answer_result is not None:
                            return answer_result
                        working_messages.append({'role': 'assistant', 'content': msg.content or raw_content or str(parsed_content)})
                        working_messages.append({
                            'role': 'user',
                            'content': 'If you are ready to answer, use the final answer field instead of an action named "answer". Otherwise call one of the available tools.',
                        })
                        round_idx += 1
                        continue
                    if action:
                        if _tool_limit_hit():
                            working_messages.append({'role': 'assistant', 'content': msg.content or ''})
                            working_messages.append({'role': 'user', 'content': 'Tool call limit reached. Please produce an answer now based on the evidence you have gathered.'})
                            round_idx += 1
                            continue

                        if not isinstance(action_input, dict):
                            action_input = {}
                        if registry.get_tool(action) is None:
                            working_messages.append({'role': 'assistant', 'content': msg.content or raw_content or ''})
                            working_messages.append({
                                'role': 'user',
                                'content': (
                                    f'Unknown tool "{action}". '
                                    + 'Available tools: '
                                    + ', '.join(registry.list_tools())
                                    + '. If you are ready to respond, use the final answer field instead of an action.'
                                ),
                            })
                            round_idx += 1
                            continue

                        observation = await registry.execute(action, action_input)
                        prompt_observation = _truncate_observation_for_prompt(observation)
                        total_tool_calls += 1

                        if phase_log is not None:
                            phase_log.retrieve(tool=action, round=round_idx, result_count=1)

                        tool_calls_log.append({
                            'round': round_idx,
                            'tool': action,
                            'input': action_input,
                            'output_preview': observation[:500],
                        })
                        if on_tool_call:
                            await _maybe_await_callback(on_tool_call, action, action_input, observation)

                        working_messages.append({'role': 'assistant', 'content': msg.content or ''})
                        working_messages.append({'role': 'user', 'content': f'Observation:\n{prompt_observation}'})
                        round_idx += 1
                        continue

                executable_tool_calls = []
                if msg.tool_calls:
                    reserved_answer = ''
                    invalid_tool_names = []
                    for tc in msg.tool_calls:
                        tool_name = str(tc.function.name or '').strip()
                        if _is_reserved_answer_action(tool_name):
                            try:
                                tool_input = json.loads(tc.function.arguments or "{}")
                            except json.JSONDecodeError:
                                tool_input = {}
                            reserved_answer = reserved_answer or _extract_answer_candidate(tool_input)
                            continue
                        if registry.get_tool(tool_name) is None:
                            invalid_tool_names.append(tool_name)
                            continue
                        executable_tool_calls.append(tc)

                    if reserved_answer and not executable_tool_calls:
                        answer_result = await _finalize_answer_candidate(reserved_answer, raw_content)
                        if answer_result is not None:
                            return answer_result
                        round_idx += 1
                        continue

                    if invalid_tool_names and not executable_tool_calls:
                        working_messages.append({'role': 'assistant', 'content': msg.content or raw_content or ''})
                        working_messages.append({
                            'role': 'user',
                            'content': (
                                'Do not call unknown tools. The available tools are: '
                                + ', '.join(registry.list_tools())
                                + '.'
                            ),
                        })
                        round_idx += 1
                        continue
                else:
                    executable_tool_calls = []

                if finish_reason == 'stop' or not executable_tool_calls:
                    answer = msg.content or ''
                    if isinstance(parsed_content, dict) and isinstance(parsed_content.get('answer'), str):
                        answer = parsed_content['answer']
                    answer_result = await _finalize_answer_candidate(answer, msg.content or raw_content or answer)
                    if answer_result is not None:
                        return answer_result
                    round_idx += 1
                    continue

                if _tool_limit_hit(len(executable_tool_calls)):
                    working_messages.append({
                        'role': 'assistant',
                        'content': msg.content or '',
                        'tool_calls': [
                            {
                                'id': tc.id,
                                'type': 'function',
                                'function': {'name': tc.function.name, 'arguments': tc.function.arguments},
                            }
                            for tc in executable_tool_calls
                        ],
                    })
                    working_messages.append({'role': 'user', 'content': 'Tool call limit reached. Please produce an answer now based on the evidence you have gathered.'})
                    round_idx += 1
                    continue

                results = await _execute_tool_calls_parallel(registry, executable_tool_calls, on_tool_call)
                total_tool_calls += len(results)

                if phase_log is not None:
                    for res in results:
                        phase_log.retrieve(tool=res['tool_name'], round=round_idx, result_count=1)

                working_messages.append({
                    'role': 'assistant',
                    'content': msg.content or '',
                    'tool_calls': [
                        {
                            'id': tc.id,
                            'type': 'function',
                            'function': {'name': tc.function.name, 'arguments': tc.function.arguments},
                        }
                        for tc in executable_tool_calls
                    ],
                })
                for res in results:
                    prompt_observation = _truncate_observation_for_prompt(res['observation'])
                    working_messages.append({
                        'role': 'tool',
                        'tool_call_id': res['tool_call_id'],
                        'content': prompt_observation,
                    })
                    tool_calls_log.append({
                        'round': round_idx,
                        'tool': res['tool_name'],
                        'input': res['tool_input'],
                        'output_preview': res['observation'][:500],
                    })
                round_idx += 1
                continue

            try:
                raw_response = await llm_call(_compact_working_messages(working_messages), system_prompt)
            except Exception as exc:
                logger.error('LLM call failed in fallback ReAct round %d: %s', round_idx, exc)
                return _error_result(thoughts, tool_calls_log, round_idx, str(exc))

            parsed = _extract_json(raw_response)
            if parsed is None:
                logger.warning('ReAct round %d: non-JSON response, treating as final answer', round_idx)
                answer_result = await _finalize_answer_candidate(raw_response, raw_response)
                if answer_result is not None:
                    return answer_result
                round_idx += 1
                continue

            thought = parsed.get('thought', '')
            if thought:
                thoughts.append(thought)
                await _maybe_await_callback(on_thought, thought)

            final_answer = parsed.get('answer', parsed.get('final_answer'))
            answer_result = await _finalize_answer_candidate(str(final_answer or ''), raw_response)
            if answer_result is not None:
                return answer_result

            action = parsed.get('action', '')
            action_input = parsed.get('input', parsed.get('action_input', {}))
            if _is_reserved_answer_action(action):
                answer_candidate = _extract_answer_candidate(action_input, parsed)
                answer_result = await _finalize_answer_candidate(answer_candidate, raw_response)
                if answer_result is not None:
                    return answer_result
                working_messages.append({'role': 'assistant', 'content': raw_response})
                working_messages.append({
                    'role': 'user',
                    'content': 'If you are ready to answer, use the final answer field instead of an action named "answer". Otherwise call one of the available tools.',
                })
                round_idx += 1
                continue

            if not action:
                working_messages.append({'role': 'assistant', 'content': raw_response})
                working_messages.append({'role': 'user', 'content': 'You must include either an "action" to call a tool or an "answer" to respond. Please try again.'})
                round_idx += 1
                continue

            if _tool_limit_hit():
                working_messages.append({'role': 'assistant', 'content': raw_response})
                working_messages.append({'role': 'user', 'content': 'Tool call limit reached. Please produce an answer now based on the evidence you have gathered.'})
                round_idx += 1
                continue

            if not isinstance(action_input, dict):
                action_input = {}
            if registry.get_tool(action) is None:
                working_messages.append({'role': 'assistant', 'content': raw_response})
                working_messages.append({
                    'role': 'user',
                    'content': (
                        f'Unknown tool "{action}". '
                        + 'Available tools: '
                        + ', '.join(registry.list_tools())
                        + '. If you are ready to respond, use the final answer field instead of an action.'
                    ),
                })
                round_idx += 1
                continue

            observation = await registry.execute(action, action_input)
            prompt_observation = _truncate_observation_for_prompt(observation)
            total_tool_calls += 1

            if phase_log is not None:
                phase_log.retrieve(tool=action, round=round_idx, result_count=1)

            tool_calls_log.append({'round': round_idx, 'tool': action, 'input': action_input, 'output_preview': observation[:500]})
            await _maybe_await_callback(on_tool_call, action, action_input, observation)

            working_messages.append({'role': 'assistant', 'content': raw_response})
            working_messages.append({'role': 'user', 'content': f'Observation:\n{prompt_observation}'})
            round_idx += 1

        if forced_final_prompt:
            working_messages.append({
                'role': 'user',
                'content': (
                    forced_final_prompt
                    + '\n\nRetrieval is exhausted. Do not call more tools. Produce the final answer now based on all evidence gathered. '
                    + 'If the evidence is still insufficient, state explicitly that the relevant code evidence could not be found after exhaustive retrieval.'
                ),
            })
        else:
            working_messages.append({'role': 'user', 'content': 'Maximum rounds reached. Please produce an answer now based on all evidence gathered.'})
        try:
            if use_native:
                prompt_messages = _compact_working_messages(working_messages)
                _final_msgs = (
                    [{'role': 'system', 'content': system_prompt}] + prompt_messages
                    if prompt_messages and prompt_messages[0].get('role') != 'system'
                    else prompt_messages
                )
                completion = await asyncio.to_thread(
                    safe_chat_completion_create,
                    client=openai_client,
                    model=model_name,
                    messages=_final_msgs,
                    max_tokens=final_max_tokens,
                    temperature=temperature,
                )
                answer = completion.choices[0].message.content or ''
            else:
                raw_final = await llm_call(_compact_working_messages(working_messages), system_prompt)
                parsed_final = _extract_json(raw_final)
                answer = ''
                if parsed_final:
                    answer = parsed_final.get('answer', parsed_final.get('final_answer', '')) or ''
                if not answer:
                    answer = raw_final

            readiness = await _run_answer_validator(answer_readiness_checker, answer, round_idx)
            if not bool(readiness.get('ok', True)):
                return {
                    'answer': '',
                    'thoughts': thoughts,
                    'tool_calls': tool_calls_log,
                    'rounds': round_idx,
                    'error': str(
                        readiness.get('feedback')
                        or 'More evidence is still needed before answering.'
                    ),
                }
            if isinstance(readiness, dict) and str(readiness.get('answer') or '').strip():
                answer = str(readiness.get('answer') or answer)
            validation = await _run_answer_validator(answer_validator, answer, round_idx)
            if not bool(validation.get('ok', True)):
                return {
                    'answer': '',
                    'thoughts': thoughts,
                    'tool_calls': tool_calls_log,
                    'rounds': round_idx,
                    'error': str(
                        validation.get('feedback')
                        or 'The final answer draft is not grounded enough to return.'
                    ),
                }
            if isinstance(validation, dict) and str(validation.get('answer') or '').strip():
                answer = str(validation.get('answer') or answer)
            return {'answer': answer, 'thoughts': thoughts, 'tool_calls': tool_calls_log, 'rounds': round_idx}
        except Exception as exc:
            return _error_result(thoughts, tool_calls_log, round_idx, str(exc))

    try:
        if timeout_sec:
            return await asyncio.wait_for(_loop_body(), timeout=timeout_sec)
        return await _loop_body()
    except asyncio.TimeoutError:
        logger.warning('ReAct loop timed out after %.0fs', timeout_sec)
        return _error_result(thoughts, tool_calls_log, int(max_rounds or 0), f'ReAct loop timed out after {timeout_sec}s')

def _error_result(thoughts, tool_calls_log, rounds, error_msg) -> Dict[str, Any]:
    return {
        "answer": "",
        "thoughts": thoughts,
        "tool_calls": tool_calls_log,
        "rounds": rounds,
        "error": error_msg,
    }

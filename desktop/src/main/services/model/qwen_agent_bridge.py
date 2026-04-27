import json
import logging
import re
import sys
import traceback
import urllib.error
import urllib.request

DEFAULT_FINAL_CONTEXT_CHARS = 24000
DEFAULT_FINAL_CONTEXT_ITEM_CHARS = 6000


def emit(event, **payload):
    sys.stdout.write(json.dumps({"event": event, **payload}, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def read_request():
    raw = sys.stdin.read()
    if not raw.strip():
        raise ValueError("empty qwen-agent bridge request")
    return json.loads(raw)


def to_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def clip_text(value, max_chars):
    text = to_text(value)
    limit = max(1000, int(max_chars or 0))
    if len(text) <= limit:
        return text
    return f"{text[:limit - 15]}\n...[truncated]"


def ensure_model_server(value):
    base = to_text(value).rstrip("/")
    if not base:
        raise ValueError("llm model_server is required")
    return base if base.endswith("/v1") else f"{base}/v1"


def normalize_message(message):
    role = to_text(message.get("role")).lower()
    if role not in {"system", "user", "assistant"}:
        role = "user"
    return {
        "role": role,
        "content": to_text(message.get("content")),
    }


def message_content(message):
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(to_text(item.get("text") or item.get("content")))
            else:
                parts.append(to_text(item))
        return "\n".join(part for part in parts if part)
    return to_text(content)


def extract_final_answer(messages):
    for message in reversed(messages or []):
        if to_text(message.get("role")).lower() != "assistant":
            continue
        if message.get("function_call"):
            continue
        content = message_content(message).strip()
        if content:
            return content
    return ""


def looks_like_incomplete_plan(answer):
    text = to_text(answer).lower()
    if not text:
        return True
    markers = [
        "검색하겠습니다",
        "확인하겠습니다",
        "찾아보겠습니다",
        "읽어보겠습니다",
        "조사하겠습니다",
        "추가 검색이 필요",
        "추가 확인이 필요",
        "더 검색",
        "더 확인",
        "search하겠습니다",
        "i will search",
        "i'll search",
        "i will check",
        "i'll check",
        "let me search",
        "let me check",
        "need to search",
        "need to check",
        "additional search",
        "more search",
        "further search",
    ]
    return any(marker in text for marker in markers)


def strip_future_tool_plan(answer):
    text = to_text(answer)
    if not text:
        return ""
    sentence_patterns = [
        r"[^.!?\n。]*(?:추가\s*(?:검색|확인)|검색해야|확인해야|검색을\s*통해\s*확인|wiki_search를\s*통해|도구를\s*호출|tool\s+call|need\s+to\s+(?:search|check)|additional\s+(?:search|check)|further\s+(?:search|check))[^.!?\n。]*[.!?。]?",
        r"[^.!?\n。]*(?:추가로\s*알려주시면|더\s*알려주시면)[^.!?\n。]*[.!?。]?",
    ]
    cleaned = text
    import re
    for pattern in sentence_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    lines = []
    line_markers = [
        "추가 검색",
        "추가 확인",
        "검색해야",
        "확인해야",
        "검색을 통해 확인",
        "wiki_search를 통해",
        "need to search",
        "need to check",
        "additional search",
        "additional check",
        "further search",
        "further check",
    ]
    for line in cleaned.splitlines():
        lowered = line.lower()
        if any(marker in lowered for marker in line_markers):
            continue
        lines.append(line.rstrip())
    normalized = "\n".join(lines).strip()
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    return normalized or text


def sanitize_interop_syntax(answer):
    text = to_text(answer)
    if not text:
        return ""
    import re
    cleaned = text
    cleaned = re.sub(
        r"\[OutAttribute\]\s*([A-Za-z_][A-Za-z0-9_.:<>,]*)\s*\^\s*%\s*([A-Za-z_][A-Za-z0-9_]*)",
        r"out \1 \2",
        cleaned,
    )
    cleaned = re.sub(
        r"\bout\s+([A-Za-z_][A-Za-z0-9_.:<>,]*)\s*\^\s*([A-Za-z_][A-Za-z0-9_]*)",
        r"out \1 \2",
        cleaned,
    )
    cleaned = re.sub(
        r"([A-Za-z_][A-Za-z0-9_.:<>,]*)\s*\^\s*%\s*([A-Za-z_][A-Za-z0-9_]*)",
        r"ref \1 \2",
        cleaned,
    )
    cleaned = re.sub(
        r"([A-Za-z_][A-Za-z0-9_.:<>,]*)\s*\^\s*%",
        r"ref \1",
        cleaned,
    )
    cleaned = re.sub(
        r"([A-Za-z_][A-Za-z0-9_.:<>,]*)\s*\^\s*([A-Za-z_][A-Za-z0-9_]*)",
        r"\1 \2",
        cleaned,
    )
    cleaned = re.sub(
        r"([A-Za-z_][A-Za-z0-9_.:<>,]*)\s*\^",
        r"\1",
        cleaned,
    )
    cleaned = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)::", r"\1.", cleaned)
    cleaned = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)->([A-Za-z_][A-Za-z0-9_]*)", r"\1.\2", cleaned)
    cleaned = re.sub(r"\bgcnew\b", "new", cleaned)
    cleaned = cleaned.replace("C++/CLI", ".NET interop declaration")
    return cleaned.strip()


def strip_invalid_wiki_code_blocks(answer):
    text = to_text(answer)
    if not text:
        return ""
    block_pattern = re.compile(r"```[A-Za-z0-9_+-]*\n.*?```", re.DOTALL)

    def replace_block(match):
        block = match.group(0)
        lowered = block.lower()
        invalid_markers = (
            "예시 값",
            "thread.sleep",
            "system.threading",
        )
        if any(marker in lowered for marker in invalid_markers):
            return ""
        if "getpercent" in lowered and re.search(r"\bwhile\s*\(", lowered):
            return ""
        return block

    cleaned = block_pattern.sub(replace_block, text)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def sanitize_wiki_answer(answer):
    text = strip_invalid_wiki_code_blocks(answer)
    if not text:
        return ""
    forbidden_patterns = (
        r"\^%",
        r"\bcli\.array\b",
    )
    future_check_fragments = (
        "확인 필요",
        "문서 확인",
        "문서 참조",
        "소스 참조",
        "SDK 정의 참조",
        "SDK 문서",
        "추정",
        "확인하시기 바랍니다",
        "need to check",
        "need to search",
        "sdk의",
        "sdk 정의",
        "참조해야",
        "참조하여",
        "구체적인 설정 파라미터",
        "별도의 설정 api",
        "시스템 기본",
        "ui 스레드",
        "ui 업데이트",
        "ui thread",
        "백그라운드",
        "background",
        "응답성",
    )
    kept = []
    named_arg_pattern = re.compile(r"(^\s*|(?<=[(,])\s*)[A-Za-z_][A-Za-z0-9_]*\s*:\s*")
    placeholder_pattern = re.compile(r"(^|[=,(]\s*)\.\.\.(\s*[),;]|$)|…")
    in_code_block = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            kept.append(line)
            continue
        if in_code_block:
            line = named_arg_pattern.sub(lambda match: match.group(1), line)
        line = re.sub(r"비동기\s*처리\s*중", "진행 중", line)
        line = re.sub(r"Export2PBE가\s*비동기로\s*동작할\s*경우", "Export 진행 중", line)
        if any(re.search(pattern, line) for pattern in forbidden_patterns):
            continue
        if placeholder_pattern.search(line):
            continue
        lower = line.lower()
        if any(fragment.lower() in lower for fragment in future_check_fragments):
            continue
        kept.append(line)
    cleaned = "\n".join(kept).strip()
    vector_data_match = re.search(r"\bXvcBase\s+([A-Za-z_][A-Za-z0-9_]*)\s*=", cleaned)
    if "NXImageLayerVectorDisplay" in cleaned and ".SetDataSource(" not in cleaned and vector_data_match:
        vector_data = vector_data_match.group(1)
        cleaned = re.sub(
            r"(NXImageLayerVectorDisplay\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*new\s+NXImageLayerVectorDisplay\s*\(\s*\)\s*;\s*)",
            lambda match: f"{match.group(1)}\n{match.group(2)}.SetDataSource({vector_data});\n",
            cleaned,
            count=1,
        )
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def ended_with_tool_result(messages):
    for message in reversed(messages or []):
        role = to_text(message.get("role")).lower()
        if role:
            return role == "function"
    return False


def collect_tool_context(messages, max_chars=DEFAULT_FINAL_CONTEXT_CHARS, item_chars=DEFAULT_FINAL_CONTEXT_ITEM_CHARS):
    chunks = []
    remaining = max(1000, int(max_chars or DEFAULT_FINAL_CONTEXT_CHARS))
    per_item = max(1000, int(item_chars or DEFAULT_FINAL_CONTEXT_ITEM_CHARS))
    for message in messages or []:
        role = to_text(message.get("role")).lower()
        content_text = message_content(message)
        is_function_result = role == "function"
        is_preloaded_tool_response = "<tool_response" in content_text and "</tool_response>" in content_text
        if not is_function_result and not is_preloaded_tool_response:
            continue
        name = to_text(message.get("name")) or ("preloaded_tool_evidence" if is_preloaded_tool_response else "tool")
        content = clip_text(content_text, per_item)
        if not content:
            continue
        chunk = f"## {name}\n{content}"
        if len(chunk) > remaining:
            chunk = clip_text(chunk, remaining)
        chunks.append(chunk)
        remaining -= len(chunk)
        if remaining <= 0:
            break
    return "\n\n".join(chunks)


def make_knowledge_payload(context):
    text = to_text(context)
    if not text:
        return ""
    return [{"url": "qwen-agent-tool-results", "text": [text]}]


def run_final_answer_pass(Assistant, model_cfg, system, messages, tool_context):
    if not to_text(tool_context):
        return "", []
    final_system = "\n".join([
        to_text(system),
        "Function tools are disabled for this final answer pass.",
        "Use only the collected tool evidence in the Knowledge Base and the conversation.",
        "Do not say that you will search, check, inspect, or call tools later.",
        "Do not include executable sample code that depends on unconfirmed API names, constructors, or methods.",
        "Do not shorten overloads by dropping required parameters. If evidence says SetX(a, b), do not write SetX(a).",
        "If the user asks about a specific operation, the final code must call the verified method/property for that operation. Do not substitute setup-only or neighboring workflow code.",
        "If the user names a concrete API surface or class, answer with that family. Do not swap to a similar class just because it has richer method declarations.",
        "Use comments or a short 'unconfirmed gap' note for missing steps instead of inventing placeholder API calls.",
        "For C# examples, [OutAttribute] by-ref parameters must be written with out, not ref.",
        "Do not discuss C++/CLI or interop declaration syntax in the final answer unless the user asks; translate it directly to C# call syntax.",
        "For C# ref parameters, the variable passed by ref must be typed as the declared parameter type. If the object is a derived type, first assign or cast it to a local variable of the declared base type, then pass that local by ref.",
        "When a source snippet shows a concrete C# call shape, prefer that overload and literal shape over filling every available overload parameter.",
        "Treat curated workflow/howto signature bullets as routing and API-family evidence, but do not copy a generic workflow example unless it directly calls the operation requested by the user.",
        "When the evidence confirms only the method declaration and not the full object acquisition path, accept the receiver object as a parameter or say it must already be available.",
        "If the final answer would only show generic setup code and not the requested operation, omit the code block and give the exact confirmed call shape instead.",
        "Never invent convenience APIs, shorthand method names, inferred getters, inferred loaders, or inferred collection accessors unless they appear in collected evidence.",
        "A method/property name must appear exactly in collected evidence before you write it in code, comments, examples, or 'may be' notes.",
        "Do not derive names from patterns such as Get*At, Load*, Open*, Set*, or Get* just because similar APIs exist; require the exact declaration or source snippet.",
        "Do not invent enum members, enum examples, or named parameters; use evidence-backed literals or leave the value as a caller-provided variable without speculative examples.",
        "Do not use EnumType.None, default enum values, or 'example enum' comments as placeholders unless that exact enum member appears in tool evidence.",
        "Do not write EnumType.Member text even in comments unless that exact full literal appears in tool evidence.",
        "If an enum value is required but no literal is confirmed, make it a method parameter; do not put placeholder comments inside executable code.",
        "Use positional arguments in C# examples unless every named argument is directly confirmed and syntactically safe.",
        "For band/composite indices, use numeric indices when evidence only confirms 0/1/2 semantics; do not invent enum aliases or color meanings such as Red/Green/Blue.",
        "Do not invent sample coordinate, level, range, or threshold values. If those values are not confirmed literals, make them helper-method parameters or keep the caller-provided variables.",
        "Code examples must not assign arbitrary scalar SDK inputs such as maxLevel = 10, lllat = 37.0, or polling thresholds. Put those scalar inputs in the helper method signature instead.",
        "Do not add polling loops, sleeps, async/background/threading logic, or progress completion thresholds unless the source evidence explicitly provides that control flow. For progress APIs, show the confirmed single call shape only.",
        "A code block containing '...' or undeclared placeholder variables is invalid. If acquisition of an object is not verified, rewrite the sample so that object is an explicit helper-method parameter, or omit the code block and state the confirmed call shape.",
        "Do not add generic lifecycle, memory, threading, or performance cautions unless they are directly supported by tool evidence or the user asks.",
        "Do not add 'check the SDK/docs/source', 'range needs checking', or similar future-check notes; omit unsupported detail instead.",
        "If evidence does not verify how to obtain an intermediate object, accept that object as a function parameter or state it is already available; do not invent getter, factory, or collection-access methods.",
        "Do not write placeholder helper calls such as GetX(), CreateX(), LoadX(), or OpenX() unless that exact helper is in evidence. For missing input objects, write a helper method whose parameters receive those objects.",
        "Prefer a helper method signature over a top-level snippet when the sample needs objects that are not constructed by verified evidence.",
        "If evidence is incomplete, answer the confirmed parts and mark only the missing detail as unconfirmed.",
    ]).strip()
    final_messages = list(messages or []) + [{
        "role": "user",
        "content": (
            "Produce the final user-facing answer now from the Knowledge Base. "
            "Do not request more searches or tool calls."
        ),
    }]
    finalizer = Assistant(
        llm=model_cfg,
        system_message=final_system,
        function_list=[],
    )
    last_messages = finalizer.run_nonstream(
        messages=final_messages,
        knowledge=make_knowledge_payload(tool_context),
    ) or []
    return extract_final_answer(last_messages), last_messages


def post_json(url, payload, timeout=300):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            return json.loads(text) if text.strip() else {}
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(text or f"HTTP {exc.code}") from exc


def normalize_parameters(schema):
    source = schema if isinstance(schema, dict) else {}
    properties = source.get("properties") if isinstance(source.get("properties"), dict) else {}
    required = source.get("required") if isinstance(source.get("required"), list) else []
    normalized_required = [
        to_text(item)
        for item in required
        if to_text(item) and to_text(item) in properties
    ]
    return {
        "type": "object",
        "properties": properties,
        "required": normalized_required,
    }


def build_bridge_tool(spec, bridge_url):
    from qwen_agent.tools.base import BaseTool

    class BridgeTool(BaseTool):
        def __init__(self):
            self.name = to_text(spec.get("name"))
            self.description = to_text(spec.get("description")) or self.name
            self.parameters = normalize_parameters(spec.get("parameters"))
            super().__init__()

        def call(self, params, **kwargs):
            del kwargs
            arguments = params
            if isinstance(params, str):
                try:
                    arguments = json.loads(params) if params.strip() else {}
                except json.JSONDecodeError:
                    arguments = {"raw": params}
            if not isinstance(arguments, dict):
                arguments = {}
            response = post_json(
                f"{bridge_url.rstrip('/')}/tool-call",
                {
                    "name": self.name,
                    "arguments": arguments,
                    "raw_params": params if isinstance(params, str) else "",
                },
            )
            content = to_text(response.get("content"))
            if content:
                return content
            return json.dumps(response, ensure_ascii=False)

    return BridgeTool()


def compact_messages(messages):
    compacted = []
    for message in messages or []:
        compacted.append({
            "role": to_text(message.get("role")),
            "name": to_text(message.get("name")),
            "content_chars": len(message_content(message)),
            "has_function_call": bool(message.get("function_call")),
        })
    return compacted


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    try:
        request = read_request()
        try:
            from qwen_agent.agents import Assistant
            import qwen_agent.agents.fncall_agent as fncall_agent
        except Exception as exc:
            emit(
                "error",
                message=(
                    "qwen-agent sidecar dependency is missing or incomplete. "
                    "Install with: python -m pip install -r desktop/src/main/services/model/qwen_agent_requirements.txt"
                ),
                detail=str(exc),
            )
            return 2

        max_llm_calls = int(request.get("max_llm_calls") or 20)
        fncall_agent.MAX_LLM_CALL_PER_RUN = max(1, min(20, max_llm_calls))

        llm = request.get("llm") if isinstance(request.get("llm"), dict) else {}
        generate_cfg = {
            "temperature": float(llm.get("temperature", 0.2)),
            "max_tokens": int(llm.get("max_tokens", 4096)),
            "top_k": int(llm.get("top_k", 20)),
            "chat_template_kwargs": {
                "enable_thinking": bool(llm.get("enable_thinking", False)),
            },
        }
        model_cfg = {
            "model": to_text(llm.get("model")),
            "model_server": ensure_model_server(llm.get("model_server")),
            "api_key": to_text(llm.get("api_key")) or "EMPTY",
            "generate_cfg": generate_cfg,
        }

        bridge_url = to_text(request.get("tool_bridge_url"))
        tools = [
            build_bridge_tool(spec, bridge_url)
            for spec in request.get("tools", [])
            if isinstance(spec, dict) and to_text(spec.get("name"))
        ]
        messages = [
            normalize_message(message)
            for message in request.get("messages", [])
            if isinstance(message, dict) and to_text(message.get("content"))
        ]
        bot = Assistant(
            llm=model_cfg,
            system_message=to_text(request.get("system")),
            function_list=tools,
        )

        emit("start", tool_count=len(tools), thinking=bool(generate_cfg["chat_template_kwargs"]["enable_thinking"]))
        last_messages = []
        last_answer = ""
        for responses in bot.run(messages=messages):
            last_messages = responses or []
            answer = extract_final_answer(last_messages)
            if answer and answer != last_answer:
                emit("assistant", aggregate=answer, delta=answer[len(last_answer):] if answer.startswith(last_answer) else answer)
                last_answer = answer

        final_answer = extract_final_answer(last_messages)
        tool_context = collect_tool_context(
            last_messages,
            request.get("final_context_chars", DEFAULT_FINAL_CONTEXT_CHARS),
            request.get("final_context_item_chars", DEFAULT_FINAL_CONTEXT_ITEM_CHARS),
        )
        if not tool_context:
            tool_context = collect_tool_context(
                messages,
                request.get("final_context_chars", DEFAULT_FINAL_CONTEXT_CHARS),
                request.get("final_context_item_chars", DEFAULT_FINAL_CONTEXT_ITEM_CHARS),
            )
        needs_final_pass = (
            tool_context
            and request.get("finalize_after_tools", True)
            and (
                bool(request.get("always_finalize_after_tools", False))
                or
                not final_answer
                or looks_like_incomplete_plan(final_answer)
                or ended_with_tool_result(last_messages)
            )
        )
        if needs_final_pass:
            finalized_answer, finalized_messages = run_final_answer_pass(
                Assistant,
                model_cfg,
                to_text(request.get("system")),
                messages,
                tool_context,
            )
            if finalized_answer:
                emit(
                    "assistant",
                    aggregate=finalized_answer,
                    delta=finalized_answer,
                    phase="final_answer_pass",
                )
                final_answer = finalized_answer
                last_messages = finalized_messages or last_messages
        final_answer = sanitize_interop_syntax(strip_future_tool_plan(final_answer))
        if bool(request.get("wiki_mode", False)):
            final_answer = sanitize_wiki_answer(final_answer)
        emit(
            "done",
            answer=final_answer,
            messages=compact_messages(last_messages),
        )
        return 0
    except Exception as exc:
        emit("error", message=str(exc), traceback=traceback.format_exc())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

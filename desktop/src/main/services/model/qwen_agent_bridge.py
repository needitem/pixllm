import json
import logging
import sys
import traceback
import urllib.error
import urllib.request

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


def message_has_tool_request(message):
    return bool(message.get("function_call") or message.get("tool_calls"))


def is_tool_result_message(message):
    role = to_text(message.get("role")).lower()
    return role in {"function", "tool", "observation"}


def extract_final_answer(messages):
    saw_tool_result_after_candidate = False
    for message in reversed(messages or []):
        role = to_text(message.get("role")).lower()
        if is_tool_result_message(message):
            saw_tool_result_after_candidate = True
            continue
        if role != "assistant":
            continue
        if message_has_tool_request(message):
            saw_tool_result_after_candidate = True
            continue
        content = message_content(message).strip()
        if content:
            if saw_tool_result_after_candidate:
                return ""
            return content
    return ""


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
            "content_preview": message_content(message)[:160],
            "has_function_call": bool(message.get("function_call")),
            "has_tool_calls": bool(message.get("tool_calls")),
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
        if not last_messages:
            final_answer = last_answer
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

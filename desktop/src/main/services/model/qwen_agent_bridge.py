import json
import logging
import os
import re
import sys
import traceback
import urllib.error
import urllib.request

_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)


def strip_history_thinking():
    """이전 턴의 <think>...</think> 추론을 모델로 되돌려보내지 않는다.

    qwen_agent의 ReAct 루프는 한 질문 안에서 LLM을 여러 번 부르는데, 매 호출마다
    직전 assistant 응답(<think> 포함)을 그대로 이어붙여 다시 보낸다. 다음 호출에
    필요한 것은 "무슨 도구를 불렀고(<tool_call>) 결과가 뭐였나(<tool_response>)"
    뿐인데, 그 사이 사고과정까지 재투입되어 턴마다 토큰이 누적된다(3콜째 입력엔
    1·2콜 think 2개). Qwen 공식 권장사항도 멀티턴에서 이전 thinking을 넣지 말라는
    것이다.

    TextChatAtOAI.convert_messages_to_dicts가 요청 dict를 만들고, 그 안에서
    'LLM Input' 트레이스도 찍는다. 그래서 입력 Message의 <think>를 이 함수를
    부르기 '전에' 지워야, 실제 모델로 나가는 요청과 트레이스가 모두 stripped를
    반영한다. 입력 Message는 에이전트의 실제 히스토리이므로 직접 고치지 않고
    복사본을 만들어 넘긴다(원본·최종 답변 추출은 그대로).

    이 목록의 <think>는 모두 '이전 턴'의 것이다(현재 턴 응답은 아직 생성 전).
    마지막 항목은 continuation 모드 보호를 위해 건드리지 않고, 그 앞의 assistant
    메시지에서만 <think>...</think>를 제거한다.
    """
    try:
        from qwen_agent.llm import oai as _oai
    except Exception:
        return
    cls = getattr(_oai, "TextChatAtOAI", None)
    if cls is None or getattr(cls, "_pixllm_think_stripped", False):
        return
    original = cls.convert_messages_to_dicts

    def _strip_message(message):
        content = getattr(message, "content", None)
        if not isinstance(content, str) or "<think>" not in content:
            return message
        stripped = _THINK_RE.sub("", content)
        try:
            return message.model_copy(update={"content": stripped})
        except Exception:
            try:
                import copy as _copy
                clone = _copy.copy(message)
                clone.content = stripped
                return clone
            except Exception:
                return message

    def convert_messages_to_dicts(self, messages):
        prepared, n = [], len(messages)
        for i, message in enumerate(messages):
            if i < n - 1 and getattr(message, "role", None) == "assistant":
                message = _strip_message(message)
            prepared.append(message)
        return original(self, prepared)

    cls.convert_messages_to_dicts = convert_messages_to_dicts
    cls._pixllm_think_stripped = True

def setup_llm_trace():
    """PIXLLM_LLM_TRACE가 켜져 있으면 qwen_agent가 실제로 모델 서버에 보내는
    프롬프트/응답 원문(LLM Input / LLM Input generate_cfg / LLM Output)을
    파일에 그대로 남긴다.

    qwen_agent는 이 원문들을 자기 로거('qwen_agent_logger')의 DEBUG 레벨로만
    찍는다. 기본은 INFO라서 아무것도 안 남는다. 여기서 하는 일:
    - qwen_agent import 전에 QWEN_AGENT_DEBUG=1을 세팅한다
      (라이브러리가 import 시점에 이 값으로 로그 레벨을 정하기 때문).
    - 로거에 FileHandler를 달아 잘림 없이 파일로 떨군다.
    기본 동작(트레이스 끔)에는 아무 영향이 없다.
    """
    flag = os.environ.get("PIXLLM_LLM_TRACE", "").strip().lower()
    if flag not in ("1", "true", "yes", "on"):
        return ""
    # qwen_agent가 import 시점에 읽는다 — import보다 먼저 세팅해야 한다.
    os.environ["QWEN_AGENT_DEBUG"] = "1"
    trace_file = os.environ.get("PIXLLM_LLM_TRACE_FILE", "").strip()
    if not trace_file:
        home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        trace_dir = os.path.join(home, ".pixllm", "desktop")
        os.makedirs(trace_dir, exist_ok=True)
        trace_file = os.path.join(trace_dir, "llm-trace.log")
    handler = logging.FileHandler(trace_file, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    qa_logger = logging.getLogger("qwen_agent_logger")
    qa_logger.setLevel(logging.DEBUG)
    qa_logger.addHandler(handler)
    return trace_file


def emit(event, **payload):
    sys.stdout.write(json.dumps({"event": event, **payload}, ensure_ascii=False) + "\n")
    sys.stdout.flush()


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


def is_truthy(value):
    if isinstance(value, bool):
        return value
    return to_text(value).lower() in {"1", "true", "yes", "on"}


def apply_thinking_config(generate_cfg, llm):
    enable_thinking = is_truthy(llm.get("enable_thinking", False))
    extra_body = generate_cfg.get("extra_body")
    if not isinstance(extra_body, dict):
        extra_body = {}
    else:
        extra_body = dict(extra_body)
    chat_template_kwargs = extra_body.get("chat_template_kwargs")
    if not isinstance(chat_template_kwargs, dict):
        chat_template_kwargs = {}
    else:
        chat_template_kwargs = dict(chat_template_kwargs)
    chat_template_kwargs["enable_thinking"] = enable_thinking
    extra_body["chat_template_kwargs"] = chat_template_kwargs
    generate_cfg["extra_body"] = extra_body
    return generate_cfg


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


def handle_request(request, assistant_cls, fncall_agent):
    """요청 하나를 처리하고 start/assistant/done(또는 error) 이벤트를 내보낸다."""
    max_llm_calls = int(request.get("max_llm_calls") or 20)
    fncall_agent.MAX_LLM_CALL_PER_RUN = max(1, min(20, max_llm_calls))

    llm = request.get("llm") if isinstance(request.get("llm"), dict) else {}
    generate_cfg = {
        "temperature": float(llm.get("temperature", 0.2)),
        "max_tokens": int(llm.get("max_tokens", 4096)),
        "top_k": int(llm.get("top_k", 20)),
    }
    generate_cfg = apply_thinking_config(generate_cfg, llm)
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
    bot = assistant_cls(
        llm=model_cfg,
        system_message=to_text(request.get("system")),
        function_list=tools,
    )

    emit("start", tool_count=len(tools), thinking=bool(llm.get("enable_thinking", False)))
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


def main():
    """warm sidecar 요청 루프.

    프로세스를 질문마다 새로 띄우면 python 기동 + qwen_agent import(수 초)가
    매 질문의 첫 응답 지연에 그대로 얹힌다. 그래서 한 번 뜬 프로세스가
    stdin에서 한 줄에 하나씩 JSON 요청을 계속 받아 처리한다.
    - 기동 직후 (import 완료 후) "ready" 이벤트를 내보내 Node 쪽이 준비 시점을 알 수 있게 한다.
    - 요청 하나의 끝은 "done" 또는 "error" 이벤트다. 요청 처리 중 예외가 나도
      프로세스는 죽지 않고 다음 요청을 기다린다.
    - stdin이 닫히면(부모 종료) 루프를 빠져나가며 종료한다.
    """
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    trace_file = setup_llm_trace()
    try:
        from qwen_agent.agents import Assistant
        import qwen_agent.agents.fncall_agent as fncall_agent
        strip_history_thinking()
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

    emit("ready", llm_trace_file=trace_file)
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            emit("error", message=f"invalid request json: {exc}")
            continue
        try:
            handle_request(request, Assistant, fncall_agent)
        except Exception as exc:
            emit("error", message=str(exc), traceback=traceback.format_exc())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

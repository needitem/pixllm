import json
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from ... import config
from ...envelopes import ApiError
from . import service as source_service


MAX_OBSERVATIONS_FOR_MODEL = 8
MAX_TOOL_CALLS_PER_STEP = 4
MODEL_OBSERVATION_CHARS = 12000
MAX_API_SIGNATURES_FOR_MODEL = 64
MAX_TYPE_RELATIONS_FOR_MODEL = 32
MAX_READ_TARGETS_FOR_MODEL = 12
MAX_SOURCE_SPANS_FOR_MODEL = 12
SOURCE_SPAN_CONTENT_CHARS = 2200
REWRITE_TIMEOUT_SECONDS = 15
_SOURCE_IDENTIFIER_CACHE: Optional[set] = None


def _to_text(value: Any) -> str:
    return str(value or "").strip()


def _clip(value: Any, limit: int = 4000) -> str:
    text = str(value or "")
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


def _ensure_rewrite_server() -> str:
    base = _to_text(config.REWRITE_LLM_BASE_URL).rstrip("/")
    return base if base.endswith("/v1") else f"{base}/v1"


def _json_for_model(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _minimum_observation_for_model(item: Dict[str, Any]) -> Dict[str, Any]:
    observation = item.get("observation") if isinstance(item, dict) else None
    if not isinstance(observation, dict):
        return item

    reduced: Dict[str, Any] = {}
    for key in ("ok", "query", "path", "symbol", "kind", "schemas", "error"):
        if key in observation:
            reduced[key] = observation[key]
    for key, limit in (
        ("declarations", 2),
        ("types", 8),
        ("assignability", 16),
        ("operations", 32),
        ("paths", 1),
        ("results", 12),
        ("matches", 12),
        ("items", 12),
        ("candidates", 12),
        ("type_members", 16),
        ("files", 12),
        ("read_targets", 16),
        ("source_spans", 12),
        ("type_relations", 24),
        ("csharp_ref_constraints", 8),
    ):
        value = observation.get(key)
        if isinstance(value, list):
            reduced[key] = value[:limit]
    if "content" in observation:
        reduced["content"] = _clip(observation.get("content"), 6000)
    if "context" in observation:
        reduced["context"] = _clip(observation.get("context"), 2000)
    return {
        "tool": item.get("tool"),
        "input": item.get("input"),
        "observation": reduced,
    }


def _source_facts_for_model(observations: List[Dict[str, Any]], *, final: bool = False) -> Dict[str, Any]:
    api_signatures: List[Dict[str, Any]] = []
    source_spans: List[Dict[str, Any]] = []
    type_relations: List[Any] = []
    ref_constraints: List[Dict[str, Any]] = []
    read_targets: List[Dict[str, Any]] = []
    seen_api = set()
    seen_signature = set()
    seen_span = set()
    seen_target = set()

    def append_api(item: Dict[str, Any]) -> None:
        signature = _to_text(item.get("csharp_signature"))
        symbol = _to_text(item.get("symbol"))
        if not signature:
            return
        key = (symbol, signature)
        if key in seen_api:
            return
        seen_api.add(key)
        seen_signature.add(signature)
        if final:
            payload = {
                "symbol": symbol,
                "signature": signature,
                "enum_literals": item.get("enum_literals") or {},
            }
            if _to_text(item.get("reason")) == "exact_identifier":
                payload["summary"] = _to_text(item.get("summary"))
            api_signatures.append({key: value for key, value in payload.items() if value not in ("", [], {}, None)})
            return
        payload = {
            "symbol": symbol,
            "signature": signature,
            "return_type": item.get("return_type"),
            "parameter_types": item.get("parameter_types") or [],
            "ref_parameter_types": item.get("ref_parameter_types") or [],
            "out_parameter_types": item.get("out_parameter_types") or [],
            "enum_literals": item.get("enum_literals") or {},
            "summary": _to_text(item.get("summary")),
        }
        api_signatures.append({key: value for key, value in payload.items() if value not in ("", [], {}, None)})

    def append_span(item: Dict[str, Any]) -> None:
        path = _to_text(item.get("path"))
        line_range = _to_text(item.get("line_range"))
        content = _to_text(item.get("content"))
        signature = _to_text(item.get("csharp_signature"))
        if not path and not content:
            return
        key = (path, line_range, _to_text(item.get("symbol")))
        if key in seen_span:
            return
        seen_span.add(key)
        payload = {
            "symbol": _to_text(item.get("symbol")),
            "path": path,
            "line_range": line_range,
            "content": _clip(content, SOURCE_SPAN_CONTENT_CHARS),
        }
        if signature and signature not in seen_signature:
            payload["signature"] = signature
        source_spans.append(payload)

    def append_target(item: Dict[str, Any]) -> None:
        key = _json_for_model(item)
        if key in seen_target:
            return
        seen_target.add(key)
        read_targets.append(item)

    for item in observations:
        observation = item.get("observation") if isinstance(item, dict) else None
        if not isinstance(observation, dict):
            continue
        for candidate in observation.get("candidates") if isinstance(observation.get("candidates"), list) else []:
            if isinstance(candidate, dict):
                append_api(candidate)
        for candidate in observation.get("type_members") if isinstance(observation.get("type_members"), list) else []:
            if isinstance(candidate, dict):
                append_api(candidate)
        for span in observation.get("source_spans") if isinstance(observation.get("source_spans"), list) else []:
            if isinstance(span, dict):
                append_span(span)
        for target in observation.get("read_targets") if isinstance(observation.get("read_targets"), list) else []:
            if isinstance(target, dict):
                append_target(target)
        for relation in observation.get("type_relations") if isinstance(observation.get("type_relations"), list) else []:
            if relation not in type_relations:
                type_relations.append(relation)
        for constraint in observation.get("csharp_ref_constraints") if isinstance(observation.get("csharp_ref_constraints"), list) else []:
            if isinstance(constraint, dict) and constraint not in ref_constraints:
                ref_constraints.append(constraint)
        if observation.get("kind") == "source_file" or observation.get("content"):
            append_span(
                {
                    "symbol": observation.get("symbol"),
                    "csharp_signature": observation.get("csharp_signature"),
                    "path": observation.get("path"),
                    "line_range": observation.get("line_range"),
                    "content": observation.get("content"),
                }
            )

    facts: Dict[str, Any] = {}
    if api_signatures:
        facts["api_signatures"] = api_signatures[:MAX_API_SIGNATURES_FOR_MODEL]
    if ref_constraints:
        facts["csharp_ref_constraints"] = ref_constraints[:16]
    if type_relations:
        facts["type_relations"] = type_relations[:MAX_TYPE_RELATIONS_FOR_MODEL]
    if read_targets and not final:
        facts["read_targets"] = read_targets[:MAX_READ_TARGETS_FOR_MODEL]
    if source_spans:
        facts["source_spans"] = (
            source_spans[:2]
            if final and api_signatures
            else source_spans[:MAX_SOURCE_SPANS_FOR_MODEL]
        )
    return facts


def _identifier_key(value: Any) -> str:
    return "".join(ch.lower() for ch in _to_text(value) if ch.isalnum())


def _api_request_tokens(prompt: str) -> List[str]:
    tokens: List[str] = []
    for token in re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", prompt):
        if token not in tokens:
            tokens.append(token)
    for token in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+API(?=$|[^A-Za-z0-9_])", prompt, flags=re.IGNORECASE):
        if token not in tokens:
            tokens.append(token)
    return tokens


def _observed_identifier_keys(observations: List[Dict[str, Any]]) -> set:
    facts = _source_facts_for_model(observations, final=True)
    keys = set()
    for item in facts.get("api_signatures") if isinstance(facts.get("api_signatures"), list) else []:
        if not isinstance(item, dict):
            continue
        for part in _to_text(item.get("symbol")).split("."):
            key = _identifier_key(part)
            if key:
                keys.add(key)
        signature = _to_text(item.get("signature") or item.get("csharp_signature"))
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", signature)
        if match:
            keys.add(_identifier_key(match.group(1)))
    for item in facts.get("type_relations") if isinstance(facts.get("type_relations"), list) else []:
        values = item.values() if isinstance(item, dict) else item if isinstance(item, list) else []
        for value in values:
            key = _identifier_key(value)
            if key:
                keys.add(key)
    return keys


def _identifier_is_observed(token: str, observed_keys: set) -> bool:
    token_key = _identifier_key(token)
    if not token_key:
        return False
    return any(key == token_key or key.endswith(token_key) or token_key.endswith(key) for key in observed_keys)


def _not_observed_api_answer(prompt: str, observations: List[Dict[str, Any]]) -> str:
    tokens = _api_request_tokens(prompt)
    if not tokens:
        return ""
    observed_keys = _observed_identifier_keys(observations)
    if any(_identifier_is_observed(token, observed_keys) for token in tokens):
        return ""
    name = tokens[0]
    if re.search(r"[가-힣]", prompt):
        return (
            f"`{name}` API는 현재 소스에서 관측된 API 시그니처에 없습니다.\n\n"
            "따라서 실제 소스 기준 사용법이나 ref/out 변환 예제 코드는 제공할 수 없습니다."
        )
    return (
        f"`{name}` was not found in the observed source API signatures.\n\n"
        "I cannot provide source-grounded usage or ref/out conversion code for it."
    )


def _message_text(message: Dict[str, Any]) -> str:
    content = message.get("content") if isinstance(message, dict) else ""
    if isinstance(content, list):
        return "\n".join(_to_text(item.get("text") if isinstance(item, dict) else item) for item in content).strip()
    return _to_text(content)


def _strip_rewrite_text(value: Any) -> str:
    text = _to_text(value)
    if text.startswith("```"):
        text = re.sub(r"^```(?:json|text)?\s*", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"\s*```$", "", text).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            text = " ".join(_to_text(item) for item in parsed if _to_text(item))
        elif isinstance(parsed, dict):
            text = " ".join(_to_text(value) for value in parsed.values() if _to_text(value))
    except Exception:
        pass
    text = text.strip().strip("\"'`")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _preserved_source_tokens(value: Any) -> List[str]:
    tokens: List[str] = []
    for token in re.findall(r"[A-Za-z#_][A-Za-z0-9#_+.]*", _to_text(value)):
        if len(token) < 2:
            continue
        token_key = token.lower()
        is_identifier = (
            token.isupper()
            or any(ch.isupper() for ch in token[1:])
            or "#" in token
            or token.lower() in {"csharp", "cpp", "c++"}
        )
        if is_identifier and token_key not in {item.lower() for item in tokens}:
            tokens.append(token)
    return tokens


def _is_source_like_identifier(value: str) -> bool:
    token = _to_text(value)
    if len(token) < 2:
        return False
    return bool(
        token.isupper()
        or any(ch.isupper() for ch in token[1:])
        or "#" in token
        or "." in token
        or token.lower() in {"csharp", "cpp", "c++"}
    )


def _source_identifier_keys() -> set:
    global _SOURCE_IDENTIFIER_CACHE
    if _SOURCE_IDENTIFIER_CACHE is not None:
        return set(_SOURCE_IDENTIFIER_CACHE)
    keys = set()
    try:
        records = source_service.load_methods_index()
    except Exception:
        records = []
    for record in records:
        for field in ("member_name", "type_name", "qualified_symbol", "qualified_type", "declaration"):
            for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", _to_text(record.get(field))):
                keys.add(token.lower())
    _SOURCE_IDENTIFIER_CACHE = keys
    return set(keys)


def _rewrite_word_tokens(value: Any) -> List[str]:
    tokens: List[str] = []
    for token in re.findall(r"[\w#.+]{2,}", _to_text(value), flags=re.UNICODE):
        text = token.strip("_.+")
        if len(text) < 2 or not any(ch.isalnum() for ch in text):
            continue
        if text not in tokens:
            tokens.append(text)
    return tokens


def _merge_rewrite_query(original: str, rewritten: str) -> str:
    terms: List[str] = []
    seen = set()
    source_keys = _source_identifier_keys()
    language_keys = {"c#", "csharp", "cpp", "c++"}
    for token in [
        *_preserved_source_tokens(original),
        *_rewrite_word_tokens(rewritten),
        *_rewrite_word_tokens(original),
    ]:
        text = _to_text(token)
        if len(text) < 2:
            continue
        if _is_source_like_identifier(text) and text.lower() not in source_keys and text.lower() not in language_keys:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        terms.append(text)
    return _clip(" ".join(terms), 240).replace("\n...[truncated]", "").strip()


def _rewrite_source_query(query: str, trace: "_TraceRecorder") -> str:
    original = _to_text(query)
    if not original:
        return ""
    endpoint = f"{_ensure_rewrite_server()}/chat/completions"
    payload = {
        "model": config.REWRITE_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You rewrite developer questions for source-code search. "
                    "Output English operation words and exact identifiers only. "
                    "Do not answer the question."
                ),
            },
            {"role": "user", "content": original},
        ],
        "temperature": 0,
        "max_tokens": 96,
    }
    result: Dict[str, Any] = {
        "ok": False,
        "query": original,
        "rewritten_query": "",
        "merged_query": original,
        "model": config.REWRITE_MODEL,
        "model_server": _ensure_rewrite_server(),
    }
    try:
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": "Bearer EMPTY"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=REWRITE_TIMEOUT_SECONDS) as response:
            raw_response = json.loads(response.read().decode("utf-8"))
        rewritten = _strip_rewrite_text(_message_text(_choice_message(raw_response)))
        merged = _merge_rewrite_query(original, rewritten)
        result.update({"ok": True, "rewritten_query": rewritten, "merged_query": merged or original})
    except Exception as exc:
        result["error"] = repr(exc)
    trace.append("source_query_rewrite", {"query": original}, result, phase="rewrite")
    return _to_text(result.get("merged_query")) or original


def _build_system_prompt() -> str:
    return "\n".join(
        [
            "You are the PIXLLM backend source agent.",
            "Use source_search first, then source_read only when exact source spans matter.",
            "Treat source_facts.api_signatures as the observed API set.",
            "For named-API questions, answer from matching observed signatures only; if none match, say it was not observed and do not substitute unrelated APIs or code.",
            "For SDK/API calls in code, use observed Pixoneer/NXDL signatures; ordinary C# language/runtime syntax is allowed.",
            "For C# answers, emit C# syntax instead of source binding syntax.",
            "For ref/out parameters, declare and initialize local variables with the observed C# parameter type before the call.",
            "If a derived object is passed to a ref base-type parameter, first assign it to a variable of that base type.",
            "Answer naturally in the user's language.",
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


TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "source_overview",
            "description": "Return source root, file count, top-level modules, and index status.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_ls",
            "description": "List source directories/files under RAW_SOURCE_ROOT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Optional Source/... directory"},
                    "depth": {"type": "integer", "description": "Directory recursion depth"},
                    "limit": {"type": "integer", "description": "Maximum returned entries"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_glob",
            "description": "Find source files by glob pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern relative to Source/"},
                    "limit": {"type": "integer", "description": "Maximum returned files"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_search",
            "description": "Find candidate source files, symbols, and read targets for a natural-language or API query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural-language/API search query"},
                    "limit": {"type": "integer", "description": "Maximum returned items"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_read",
            "description": "Read a source file span or indexed symbol target returned by a source tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Source/... path or .runtime/methods_index.json#Symbol"},
                    "start_line": {"type": "integer", "description": "Optional start line"},
                    "end_line": {"type": "integer", "description": "Optional end line"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_type_graph",
            "description": "Build a type/member graph from declarations, referenced types, inheritance, and C# signatures.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Workflow, API, or type terms"},
                    "limit": {"type": "integer", "description": "Maximum returned types"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "source_usages",
            "description": "Find real non-comment source usages for a type, method, or call pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Type, method, or call pattern"},
                    "limit": {"type": "integer", "description": "Maximum returned usages"},
                },
                "required": ["query"],
            },
        },
    },
]

PRIMARY_TOOL_NAMES = ("source_search", "source_read", "source_type_graph", "source_usages")
BROAD_TOOL_NAMES = ("source_overview", "source_ls", "source_glob")
BROAD_SOURCE_PROMPT_RE = re.compile(
    r"(overview|module|directory|folder|glob|list|ls|tree|파일|목록|폴더|디렉|구조|모듈|전체|경로)",
    re.IGNORECASE,
)
COMPACT_TOOL_DESCRIPTIONS = {
    "source_overview": "Source root, counts, modules, index status.",
    "source_ls": "List Source/ paths.",
    "source_glob": "Find Source/ files by glob.",
    "source_search": "Find candidate symbols, files, and read targets.",
    "source_read": "Read a Source/ span or indexed symbol target.",
    "source_type_graph": "Return compact type/member graph and signatures.",
    "source_usages": "Find real source usages.",
}
TOOL_DEFINITIONS_BY_NAME = {
    _to_text(item.get("function", {}).get("name")): item
    for item in TOOL_DEFINITIONS
    if isinstance(item.get("function"), dict) and _to_text(item.get("function", {}).get("name"))
}


def _compact_parameters(schema: Any) -> Dict[str, Any]:
    if not isinstance(schema, dict):
        return {"type": "object", "properties": {}, "required": []}
    properties: Dict[str, Any] = {}
    raw_properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    for name, definition in raw_properties.items():
        if not isinstance(definition, dict):
            continue
        compact: Dict[str, Any] = {}
        for key in ("type", "enum", "items"):
            if key in definition:
                compact[key] = definition[key]
        properties[_to_text(name)] = compact or {"type": "string"}
    required = [
        _to_text(item)
        for item in (schema.get("required") if isinstance(schema.get("required"), list) else [])
        if _to_text(item) in properties
    ]
    return {"type": "object", "properties": properties, "required": required}


def _compact_tool_definition(definition: Dict[str, Any]) -> Dict[str, Any]:
    function = definition.get("function") if isinstance(definition, dict) else {}
    function = function if isinstance(function, dict) else {}
    name = _to_text(function.get("name"))
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": COMPACT_TOOL_DESCRIPTIONS.get(name, _to_text(function.get("description"))),
            "parameters": _compact_parameters(function.get("parameters")),
        },
    }


COMPACT_TOOL_DEFINITIONS_BY_NAME = {
    name: _compact_tool_definition(definition)
    for name, definition in TOOL_DEFINITIONS_BY_NAME.items()
}


def _prompt_needs_broad_source_tools(prompt: str) -> bool:
    return bool(BROAD_SOURCE_PROMPT_RE.search(_to_text(prompt)))


def _needs_broad_tool_fallback(observations: List[Dict[str, Any]]) -> bool:
    for item in observations[-2:]:
        if _to_text(item.get("tool")) != "source_search":
            continue
        observation = item.get("observation") if isinstance(item, dict) else {}
        observation = observation if isinstance(observation, dict) else {}
        if observation.get("ok") is False:
            return True
        has_candidates = bool(observation.get("candidates") or observation.get("source_spans") or observation.get("read_targets"))
        if not has_candidates:
            return True
    return False


def _tool_definitions_for_step(prompt: str, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    names = list(PRIMARY_TOOL_NAMES)
    if not observations or _prompt_needs_broad_source_tools(prompt) or _needs_broad_tool_fallback(observations):
        names = [*BROAD_TOOL_NAMES, *PRIMARY_TOOL_NAMES]
    return [
        COMPACT_TOOL_DEFINITIONS_BY_NAME[name]
        for name in names
        if name in COMPACT_TOOL_DEFINITIONS_BY_NAME
    ]


def _search_query_with_prompt(raw_query: str, prompt: str) -> str:
    query = _to_text(raw_query)
    prompt_text = _to_text(prompt)
    if prompt_text and prompt_text not in query:
        query = f"{query}\n{prompt_text}".strip()
    return query


def _execute_tool(name: str, arguments: Dict[str, Any], trace: _TraceRecorder, *, prompt: str = "") -> Dict[str, Any]:
    if name == "source_overview":
        result = source_service.get_context()
    elif name == "source_ls":
        result = source_service.list_source(
            _to_text(arguments.get("path") or arguments.get("pattern")),
            depth=_safe_int(arguments.get("depth"), 1, 0, 8),
            limit=_safe_int(arguments.get("limit"), 80, 1, 300),
        )
    elif name == "source_glob":
        result = source_service.glob_source(
            _to_text(arguments.get("pattern")) or "**/*",
            limit=_safe_int(arguments.get("limit"), 80, 1, 300),
        )
    elif name == "source_grep":
        result = source_service.grep_source(
            _to_text(arguments.get("pattern")),
            path_glob=_to_text(arguments.get("path_glob")),
            regex=bool(arguments.get("regex")),
            case_sensitive=bool(arguments.get("case_sensitive")),
            limit=_safe_int(arguments.get("limit"), 20, 1, 20),
            context=_safe_int(arguments.get("context"), 1, 0, 4),
        )
    elif name == "source_search":
        raw_query = _to_text(arguments.get("query") or arguments.get("pattern"))
        rewritten_query = _rewrite_source_query(_search_query_with_prompt(raw_query, prompt), trace)
        arguments["query"] = rewritten_query
        if rewritten_query != raw_query:
            arguments["original_query"] = raw_query
        result = source_service.find_source(
            rewritten_query,
            limit=max(12, _safe_int(arguments.get("limit"), 12, 1, 40)),
        )
    elif name == "source_read":
        result = source_service.read_source(
            _to_text(arguments.get("path") or arguments.get("pattern")),
            start_line=arguments.get("start_line"),
            end_line=arguments.get("end_line"),
        )
        if not result:
            result = {"ok": False, "error": "source_path_not_found", "path": _to_text(arguments.get("path"))}
    elif name == "source_type_graph":
        raw_query = _to_text(arguments.get("query") or arguments.get("pattern"))
        rewritten_query = _rewrite_source_query(_search_query_with_prompt(raw_query, prompt), trace)
        arguments["query"] = rewritten_query
        if rewritten_query != raw_query:
            arguments["original_query"] = raw_query
        result = source_service.type_graph(
            rewritten_query,
            limit=max(12, _safe_int(arguments.get("limit"), 12, 1, 20)),
        )
    elif name == "source_usages":
        raw_query = _to_text(arguments.get("query") or arguments.get("pattern"))
        rewritten_query = _rewrite_source_query(_search_query_with_prompt(raw_query, prompt), trace)
        arguments["query"] = rewritten_query
        if rewritten_query != raw_query:
            arguments["original_query"] = raw_query
        result = source_service.source_usages(
            rewritten_query,
            limit=_safe_int(arguments.get("limit"), 12, 1, 50),
        )
    else:
        result = {"ok": False, "error": "unknown_tool", "tool": name}

    trace.append(name, arguments, result)
    return result


def _observations_for_model(observations: List[Dict[str, Any]], *, final: bool = False) -> str:
    selected = observations[-MAX_OBSERVATIONS_FOR_MODEL:]
    if not selected:
        return "[]"

    source_facts = _source_facts_for_model(selected, final=final)
    if source_facts:
        payload = {"source_facts": source_facts}
        text = _json_for_model(payload)
        if len(text) <= MODEL_OBSERVATION_CHARS:
            return text
        for key in ("source_spans", "read_targets", "type_relations", "api_signatures"):
            value = source_facts.get(key)
            if isinstance(value, list):
                source_facts[key] = value[: max(4, len(value) // 2)]
            text = _json_for_model(payload)
            if len(text) <= MODEL_OBSERVATION_CHARS:
                return text

    text = _json_for_model(selected)
    if len(text) <= MODEL_OBSERVATION_CHARS:
        return text

    reduced = [_minimum_observation_for_model(item) for item in selected]
    text = _json_for_model(reduced)
    if len(text) <= MODEL_OBSERVATION_CHARS:
        return text

    for item in reduced:
        observation = item.get("observation") if isinstance(item, dict) else None
        if not isinstance(observation, dict):
            continue
        for key in ("operations", "results", "matches", "items", "types", "assignability", "declarations", "paths"):
            value = observation.get(key)
            if isinstance(value, list):
                observation[key] = value[:4]
        observation.pop("schemas", None)

    text = _json_for_model(reduced)
    while len(text) > MODEL_OBSERVATION_CHARS and len(reduced) > 1:
        reduced = reduced[1:]
        text = _json_for_model(reduced)
    return text


def _build_messages(prompt: str, observations: List[Dict[str, Any]], *, final: bool = False) -> List[Dict[str, str]]:
    messages = [
        {"role": "system", "content": _build_system_prompt()},
        {"role": "user", "content": prompt},
    ]
    if observations:
        task = (
            "Answer the user now from these source facts. Ground SDK/API calls in source_facts.api_signatures "
            "and follow source_facts.csharp_ref_constraints."
            if final
            else "Use more tools if needed; otherwise answer the user from source_facts only."
        )
        messages.append(
            {
                "role": "user",
                "content": f"Source observations so far:\n{_observations_for_model(observations, final=final)}\n\n{task}",
            }
        )
    return messages


def _chat_completion_response(
    *,
    model_cfg: Dict[str, Any],
    messages: List[Dict[str, Any]],
    max_tokens: int,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    endpoint = f"{_to_text(model_cfg.get('model_server')).rstrip('/')}/chat/completions"
    payload: Dict[str, Any] = {
        "model": model_cfg["model"],
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "top_k": 20,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer EMPTY"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ApiError("LLM_HTTP_ERROR", detail or repr(exc), status_code=502) from exc


def _response_usage(response: Dict[str, Any]) -> Dict[str, int]:
    usage = response.get("usage") if isinstance(response, dict) else {}
    usage = usage if isinstance(usage, dict) else {}
    return {
        "prompt_tokens": int(usage.get("prompt_tokens") or 0),
        "completion_tokens": int(usage.get("completion_tokens") or 0),
        "total_tokens": int(usage.get("total_tokens") or 0),
    }


def _add_response_usage(total: Dict[str, int], response: Dict[str, Any]) -> None:
    usage = _response_usage(response)
    for key, value in usage.items():
        total[key] = int(total.get(key) or 0) + value


def _choice_message(response: Dict[str, Any]) -> Dict[str, Any]:
    choices = response.get("choices") if isinstance(response, dict) else []
    if not choices or not isinstance(choices[0], dict):
        return {}
    message = choices[0].get("message")
    return message if isinstance(message, dict) else {}


def _extract_tool_calls(message: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    calls: List[Tuple[str, Dict[str, Any]]] = []
    tool_calls = message.get("tool_calls") if isinstance(message, dict) else None
    if isinstance(tool_calls, list):
        for call in tool_calls[:MAX_TOOL_CALLS_PER_STEP]:
            function = call.get("function") if isinstance(call, dict) else None
            if not isinstance(function, dict):
                continue
            name = _to_text(function.get("name"))
            arguments = _normalize_tool_args(function.get("arguments"))
            if name:
                calls.append((name, arguments))
    function_call = message.get("function_call") if isinstance(message, dict) else None
    if isinstance(function_call, dict):
        name = _to_text(function_call.get("name"))
        arguments = _normalize_tool_args(function_call.get("arguments"))
        if name:
            calls.append((name, arguments))
    return calls


def _message_answer(message: Dict[str, Any]) -> str:
    content = message.get("content") if isinstance(message, dict) else ""
    if isinstance(content, list):
        return "\n".join(_to_text(item.get("text") if isinstance(item, dict) else item) for item in content).strip()
    return _to_text(content)


def _final_answer(
    *,
    prompt: str,
    observations: List[Dict[str, Any]],
    model_cfg: Dict[str, Any],
    max_tokens: int,
) -> Tuple[str, Dict[str, int]]:
    response = _chat_completion_response(
        model_cfg=model_cfg,
        messages=_build_messages(prompt, observations, final=True),
        max_tokens=max_tokens,
        tools=None,
    )
    return _message_answer(_choice_message(response)), _response_usage(response)


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
    del enable_thinking
    normalized_prompt = _to_text(prompt)
    if not normalized_prompt:
        raise ApiError("EMPTY_PROMPT", "prompt is required")

    trace = _TraceRecorder()
    completion_token_budget = _safe_int(max_tokens, 4096, 256, 16384)
    model_cfg = {
        "model": _to_text(model) or config.DEFAULT_MODEL,
        "model_server": _ensure_model_server(llm_base_url or ""),
    }

    observations: List[Dict[str, Any]] = []
    completion_calls = 0
    final_answer = ""
    max_steps = _safe_int(max_llm_calls, 12, 1, 40)
    usage_totals = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    for _ in range(max_steps):
        response = _chat_completion_response(
            model_cfg=model_cfg,
            messages=_build_messages(normalized_prompt, observations, final=bool(observations)),
            max_tokens=completion_token_budget,
            tools=_tool_definitions_for_step(normalized_prompt, observations),
        )
        _add_response_usage(usage_totals, response)
        completion_calls += 1
        message = _choice_message(response)
        tool_calls = _extract_tool_calls(message)
        if not tool_calls:
            final_answer = _not_observed_api_answer(normalized_prompt, observations) or _message_answer(message)
            break
        for tool_name, arguments in tool_calls:
            observation = _execute_tool(tool_name, arguments, trace, prompt=normalized_prompt)
            observations.append({"tool": tool_name, "input": arguments, "observation": observation})
        final_answer = _not_observed_api_answer(normalized_prompt, observations)
        if final_answer:
            break

    if not final_answer:
        final_answer = _not_observed_api_answer(normalized_prompt, observations)
        if not final_answer:
            final_answer, final_usage = _final_answer(
                prompt=normalized_prompt,
                observations=observations,
                model_cfg=model_cfg,
                max_tokens=completion_token_budget,
            )
            for key, value in final_usage.items():
                usage_totals[key] = int(usage_totals.get(key) or 0) + value
            completion_calls += 1
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
            "completion_calls": completion_calls,
            "prompt_tokens": usage_totals["prompt_tokens"],
            "completion_tokens": usage_totals["completion_tokens"],
            "total_tokens": usage_totals["total_tokens"],
        },
    }

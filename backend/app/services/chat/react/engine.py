import asyncio
import json
import re
import time
from inspect import isawaitable
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .... import config, rag_config
from ..answer_quality import build_provenance_report, detect_unsupported_claims
from ..evidence import build_evidence_gate
from ..grounding import enforce_source_whitelist
from ..layered_merge import build_local_overlay_evidence, extract_local_workspace_overlay
from ..text import sanitize_user_message
from ..retrieval.routing import build_sources, tool_evidence_to_results
from .phase_log import PhaseLogger
from ..runtime_profile import resolve_runtime_routing_profile
from ..workspace_graph import (
    build_workspace_grounding_report,
    collect_grounded_overlay_paths,
    collect_grounded_overlay_windows,
    extract_workspace_graph,
    render_workspace_graph_answer,
    workspace_graph_has_content,
    workspace_graph_is_ready_for_answer,
)
from .usage_guide import (
    _generate_usage_guide_answer_from_bundle,
    _postprocess_usage_guide_answer,
    _repair_usage_guide_answer_from_results,
    _usage_bundle_has_tutorial_signal,
)
from .code_explain_overlay import run_local_overlay_code_explain
from ....core.llm_utils import (
    build_chat_template_extra_body,
    safe_chat_completion_create,
    extract_completion_finish_reason,
    stream_chat_completion_text,
    stream_chat_completion_text_with_meta,
)
from .loop import build_system_prompt, run_react_loop
from ...tools.runtime import (
    find_symbol,
    list_repo_files,
    open_doc_chunks,
    read_code_lines,
    search_code,
    search_docs,
)
from ...tools.code_runtime import relativize_code_path
from ...tools.query_strategy import prioritize_usage_matches
from ...tools.usage_bundle import collect_usage_guide_bundle, extract_symbol_candidates
from ...tools.access import resolve_tool_user_context
from ...tools.registry import ToolParam, ToolRegistry


ProgressCallback = Optional[Callable[[Dict[str, Any]], Awaitable[None] | None]]
TokenCallback = Optional[Callable[[str], Awaitable[None] | None]]
SourcesCallback = Optional[Callable[[List[Dict[str, Any]]], Awaitable[None] | None]]
ToolCallback = Optional[Callable[[str, Dict[str, Any], str], Awaitable[None] | None]]


class StageTimeoutError(RuntimeError):
    def __init__(self, stage: str, timeout_sec: float):
        self.stage = str(stage or "unknown")
        self.timeout_sec = float(timeout_sec)
        super().__init__(f"{self.stage} stage timed out after {self.timeout_sec:.0f}s")


async def _maybe_await_callback(callback, *args, **kwargs) -> None:
    if callback is None:
        return
    result = callback(*args, **kwargs)
    if isawaitable(result):
        await result


def _timeout_value(value: int) -> Optional[float]:
    timeout = int(value or 0)
    return float(timeout) if timeout > 0 else None


async def _run_with_stage_timeout(awaitable, *, stage: str, timeout_sec: Optional[float]):
    if not timeout_sec:
        return await awaitable
    try:
        return await asyncio.wait_for(awaitable, timeout=timeout_sec)
    except asyncio.TimeoutError as exc:
        raise StageTimeoutError(stage=stage, timeout_sec=timeout_sec) from exc


async def _emit_progress(
    callback: ProgressCallback,
    *,
    phase: str,
    message: str,
    **extra: Any,
) -> None:
    payload = {"phase": phase, "message": message}
    payload.update(extra)
    await _maybe_await_callback(callback, payload)


def _tool_progress_message(tool_name: str, tool_input: Dict[str, Any]) -> str:
    query = str(tool_input.get("query") or tool_input.get("pattern") or tool_input.get("symbol") or "").strip()
    if tool_name == "usage_bundle":
        return "코드 사용 흐름을 구조화하는 중..."
    if tool_name == "find_symbol":
        return f"'{query}' 정의 위치를 찾는 중..." if query else "심볼 정의를 찾는 중..."
    if tool_name in {"grep", "doc_search"}:
        return f"'{query}' 근거를 찾는 중..." if query else "관련 근거를 찾는 중..."
    if tool_name in {"read", "doc_read"}:
        return "찾은 근거를 자세히 읽는 중..."
    return f"{tool_name} 도구를 실행하는 중..."


def _merge_unique(rows: List[Dict[str, Any]], added: List[Dict[str, Any]], key_fields: List[str]) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for row in rows + added:
        key = tuple(str(row.get(k) or "") for k in key_fields)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _load_react_prompt_template(max_rounds: int) -> str:
    profile_root = Path(__file__).resolve().parents[3] / ".profiles"
    template_path = profile_root / "rules" / "react_tools.md"
    unlimited_rounds = int(max_rounds or 0) <= 0
    round_hint = "unbounded" if unlimited_rounds else str(int(max_rounds))
    if not template_path.exists():
        return (
            "Respond with exactly one JSON object per turn.\n"
            "Tool call format: {\"thought\":\"...\",\"action\":\"tool_name\",\"input\":{...}}\n"
            "Final answer format: {\"thought\":\"...\",\"answer\":\"...\"}\n"
            "Use only tool observations. If evidence is insufficient, state that clearly.\n"
            + ("Keep retrieving until evidence is sufficient or the available probes are exhausted.\n" if unlimited_rounds else "")
            + (f"Maximum {round_hint} rounds." if not unlimited_rounds else "No fixed round budget.")
        )
    raw = template_path.read_text(encoding="utf-8").strip()
    if raw.startswith("---"):
        parts = raw.split("\n---", 1)
        if len(parts) == 2:
            raw = parts[1].strip()
    raw = raw.replace("{max_rounds}", round_hint)
    if unlimited_rounds:
        raw += "\n- Keep retrieving until evidence is sufficient or the available probes are exhausted."
    return raw


def _build_tool_mode_hint(
    profile: Dict[str, Any],
    *,
    response_type: str = "",
    workspace_overlay_present: bool = False,
) -> str:
    preferred_mode = str(profile.get("preferred_tool_mode") or "code")
    tool_priority = ", ".join(str(x) for x in (profile.get("tool_priority") or []))
    lane = str(profile.get("agent_lane") or "general_assistant_lane")
    strategy = str(profile.get("tool_strategy") or "")
    answer_style = str(profile.get("answer_style") or "default")
    response_kind = str(response_type or "").strip().lower()
    answer_style_hint = ""
    if answer_style == "tutorial":
        answer_style_hint = (
            "Write the final answer as a grounded usage explanation with a short overview, the strongest confirmed code path, "
            "a minimal grounded example when available, and caveats. "
            "Do not default to property or method tables unless the user explicitly asks for API reference.\n"
        )
    elif answer_style == "reference":
        answer_style_hint = "Write the final answer as a concise reference summary grounded in the retrieved evidence.\n"
    elif answer_style == "troubleshooting":
        answer_style_hint = "Write the final answer as a troubleshooting guide with symptoms, likely causes, checks, and fixes.\n"
    if preferred_mode == "docs":
        return (
            f"Runtime routing profile: lane={lane}, strategy={strategy}.\n"
            "For this question type, prioritize document evidence first.\n"
            f"Use tools in this order when possible: {tool_priority}.\n"
            f"{answer_style_hint}"
            "Use code tools only when document evidence is insufficient."
        )
    if workspace_overlay_present:
        overlay_exhaustive_hint = (
            "For local code explanation requests, keep retrieving until the current frontier is grounded or the available probes are exhausted. "
            "Do not stop because of a fixed round budget. If exhaustive retrieval still cannot confirm a relation, state explicitly that the supporting code was not found.\n"
            if response_kind == "code_explain"
            else ""
        )
        return (
            f"Runtime routing profile: lane={lane}, strategy={strategy}.\n"
            "The local workspace overlay is the primary code graph for this request.\n"
            f"Use tools in this order when possible: {tool_priority}.\n"
            "Prefer local workspace evidence first.\n"
            "Use server code tools to confirm engine/framework baselines or when the local evidence is incomplete.\n"
            f"{overlay_exhaustive_hint}"
            "Treat server search hits as supporting evidence until you confirm them with grounded reads.\n"
            "Treat search-only candidates and frontier_files as leads, not confirmed evidence.\n"
            "Only grounded read spans and grounded graph nodes may appear as confirmed files or code references in the final answer.\n"
            "Default to prose. Only include a code block when it comes directly from a grounded read span.\n"
            f"{answer_style_hint}"
            "Write the answer from local workspace evidence first, and use engine references only as supporting context."
        )

    repo_hint = "Start with find_symbol or grep on the most distinctive symbol/API name and then read the most relevant files."
    usage_guide_hint = (
            "For usage_guide questions, call usage_bundle first when the question is about a concrete symbol or file-backed feature. "
            "If usage_bundle is unavailable or weak, call find_symbol before grep to anchor the exact definition file. "
            "Use usage_bundle.sections and usage_bundle.recommended_sequence only as grounded hints, not as a fixed template. "
            "Prefer one cohesive anchor file before using secondary files. "
            "Do not invent missing stages, flows, or example files just to fill structure. "
            "Avoid plain method/event tables unless the user explicitly asked for API reference.\n"
        if response_kind == "usage_guide"
        else ""
    )
    mode_hint = (
        "For this question type, balance code and document evidence together.\n"
        if preferred_mode == "hybrid"
        else "For this question type, prioritize code evidence first.\n"
    )
    return (
        f"Runtime routing profile: lane={lane}, strategy={strategy}.\n"
        f"{mode_hint}"
        f"Use tools in this order when possible: {tool_priority}.\n"
        f"{repo_hint}\n"
        + (
            "Treat the attached local workspace overlay as the primary source of truth. Answer from the local workspace evidence first. Use server code tools only to resolve engine or framework symbols that are explicitly referenced by the local workspace evidence. Do not run broad baseline searches for generic keywords.\n"
            if workspace_overlay_present
            else ""
        )
        +
        "Prefer find_symbol before broad grep when the question mentions a concrete class, control, method, or API name.\n"
        "For usage or tutorial questions, prefer reading the matched code blocks before writing the answer.\n"
        "Default to prose. Only include a code block when it comes directly from a grounded read span.\n"
        f"{answer_style_hint}"
        f"{usage_guide_hint}"
        "Use document tools when code evidence is insufficient."
    )


def _build_history_messages(
    history_messages: List[Dict[str, Any]],
    clean_message: str,
    *,
    local_overlay_context: str = "",
) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []
    for item in history_messages[-4:]:
        role = str(item.get("role") or "").strip().lower()
        if role not in {"user", "assistant"}:
            continue
        content = str(item.get("content") or "").strip()
        if not content:
            continue
        if role == "user":
            content = sanitize_user_message(content) or content
            content = content[:800]
        else:
            content = content[:1000]
        messages.append({"role": role, "content": content})
    if local_overlay_context:
        messages.append({"role": "user", "content": local_overlay_context})
    messages.append({"role": "user", "content": clean_message})
    return messages


def _build_local_overlay_context(
    local_overlay_items: List[Dict[str, Any]],
    *,
    grounding_report: Dict[str, Any] | None = None,
) -> str:
    if not local_overlay_items:
        return ""
    parts = ["[Local Workspace Evidence]"]
    for item in local_overlay_items[:4]:
        kind = str(item.get("kind") or "evidence")
        if kind in {"workspace_status", "workspace_diff"}:
            continue
        path = str(item.get("path") or "workspace")
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        normalized_text = " ".join(text.split())
        parts.append(f"- kind={kind} path={path}\n{normalized_text[:420]}")
    report = dict(grounding_report or {})
    confirmed_paths = [str(item).strip() for item in list(report.get("direct_paths") or []) if str(item).strip()]
    if confirmed_paths:
        parts.append("[Directly Inspected Files]")
        parts.extend(f"- {path}" for path in confirmed_paths[:4])
    graph_only_paths = [str(item).strip() for item in list(report.get("graph_only_paths") or []) if str(item).strip()]
    if report:
        parts.append(
            "[Grounding Report]\n"
            f"- focus_grounded={bool(report.get('focus_grounded'))}\n"
            f"- direct_path_count={int(report.get('direct_path_count') or 0)}\n"
            f"- graph_path_count={int(report.get('graph_path_count') or 0)}\n"
            f"- grounded_graph_path_count={int(report.get('grounded_graph_path_count') or 0)}"
        )
    if graph_only_paths:
        parts.append("[Graph-Only Files]")
        parts.extend(f"- {path}" for path in graph_only_paths[:3])
        parts.append(
            "[Graph Guidance]\n"
            "Treat graph-only files as hints about possible flow. Do not present them as directly confirmed unless the answer clearly marks them as inference."
        )
    if report.get("focus_path") and not bool(report.get("focus_grounded")):
        parts.append(
            "[Coverage Warning]\n"
            f"The workspace graph focus file `{report.get('focus_path')}` is not directly inspected by `selected_file` or `read_file` evidence. "
            "Do not claim method-level flow for that file unless you clearly mark it as unverified."
        )
    return "\n\n".join(parts).strip()


def _compact_preview_text(text: str, max_chars: int = 180) -> str:
    normalized = " ".join(str(text or "").split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max(40, max_chars - 24)] + "...[truncated]"


def _summarize_code_match_for_prompt(row: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(row or {})
    return {
        "path": str(payload.get("path") or payload.get("file_path") or "").strip(),
        "line_range": str(payload.get("line_range") or "").strip(),
        "symbol": str(payload.get("symbol") or payload.get("name") or "").strip(),
        "preview": _compact_preview_text(
            str(payload.get("preview") or payload.get("line_text") or payload.get("text") or ""),
            max_chars=180,
        ),
    }


def _summarize_glob_file_for_prompt(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        return {
            "path": str(item.get("path") or "").strip(),
            "type": str(item.get("type") or "").strip(),
        }
    return {"path": str(item or "").strip()}


def _normalize_engine_read_path(code_tools, path_value: str) -> str:
    return str(relativize_code_path(code_tools, str(path_value or "").strip()) or "").strip().replace("\\", "/")


def _extract_code_like_mentions(text: str) -> List[str]:
    matches = re.findall(
        r"\b(?:[A-Z][A-Za-z0-9_]*_[A-Za-z0-9_]+|[A-Z][A-Za-z0-9_]*[a-z][A-Z][A-Za-z0-9_]*)\b",
        str(text or ""),
    )
    seen = set()
    ordered: List[str] = []
    for token in matches:
        normalized = str(token or "").strip()
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        ordered.append(normalized)
    return ordered


class _EvidenceAccumulator:
    def __init__(self):
        self.doc_search_rows: List[Dict[str, Any]] = []
        self.doc_chunks: List[Dict[str, Any]] = []
        self.code_matches: List[Dict[str, Any]] = []
        self.code_windows: List[Dict[str, Any]] = []

    def add_doc_search_rows(self, rows: List[Dict[str, Any]]) -> None:
        self.doc_search_rows = _merge_unique(self.doc_search_rows, rows, ["chunk_id"])

    def add_doc_chunks(self, rows: List[Dict[str, Any]]) -> None:
        self.doc_chunks = _merge_unique(self.doc_chunks, rows, ["chunk_id"])

    def add_code_matches(self, rows: List[Dict[str, Any]]) -> None:
        self.code_matches = _merge_unique(self.code_matches, rows, ["path", "line_range"])

    def add_code_window(self, row: Dict[str, Any]) -> None:
        self.code_windows = _merge_unique(self.code_windows, [row], ["path", "line_range"])

    def to_results(self) -> List[Dict[str, Any]]:
        evidence = {
            "docs": {
                "search": {"results": self.doc_search_rows},
                "chunks": self.doc_chunks,
            },
            "code": {
                "search": {"matches": self.code_matches},
                "windows": self.code_windows,
            },
        }
        return tool_evidence_to_results(evidence)


async def run_react_chat_generation(
    *,
    chat_deps,
    req,
    clean_message: str,
    response_type: str,
    intent_source: str = "",
    intent_confidence: float = 0.0,
    retrieval_bias: str = "",
    answer_style: str = "",
    history_messages: List[Dict[str, Any]],
    model_name: str,
    max_tokens: int,
    temperature: float,
    system_prompt_seed: str,
    session_id: str,
    progress_callback: ProgressCallback = None,
    token_callback: TokenCallback = None,
    sources_callback: SourcesCallback = None,
    tool_callback: ToolCallback = None,
) -> Dict[str, Any]:
    started = time.perf_counter()
    phase_log = PhaseLogger(session_id=session_id, response_type=response_type)
    accumulator = _EvidenceAccumulator()
    local_overlay = extract_local_workspace_overlay(req)
    local_overlay_items = build_local_overlay_evidence(local_overlay)
    workspace_overlay_authoritative = bool(local_overlay.get("present"))
    workspace_graph = extract_workspace_graph(local_overlay)
    grounded_overlay_paths = collect_grounded_overlay_paths(local_overlay)
    grounded_overlay_windows = collect_grounded_overlay_windows(local_overlay)
    workspace_grounding_report = build_workspace_grounding_report(
        workspace_graph,
        grounded_overlay_paths,
    )
    local_overlay_context = _build_local_overlay_context(
        local_overlay_items,
        grounding_report=workspace_grounding_report,
    )
    active_collection = getattr(req, "collection", None) or config.RAG_DEFAULT_COLLECTION
    max_chars = min(int(config.CHAT_TOOL_MAX_CHARS), 12000)
    max_line_span = min(int(config.CHAT_TOOL_MAX_LINE_SPAN), 500)
    retrieve_timeout_sec = _timeout_value(rag_config.react_retrieve_timeout_sec())
    answer_timeout_sec = _timeout_value(rag_config.react_answer_timeout_sec())

    # Redis client from app state
    redis = getattr(chat_deps, "redis", None)
    if redis is not None:
        await resolve_tool_user_context(redis, session_id=session_id, user_id=None)

    for item in grounded_overlay_windows:
        accumulator.add_code_window(
            {
                "path": str(item.get("path") or "workspace"),
                "line_range": str(item.get("line_range") or "1-1"),
                "content": str(item.get("content") or ""),
            }
        )

    filters: Dict[str, Any] = {}
    if getattr(req, "language_filter", None):
        filters["language"] = getattr(req, "language_filter")
    if getattr(req, "module_filter", None):
        filters["module"] = getattr(req, "module_filter")
    registry = ToolRegistry()
    routing_profile = resolve_runtime_routing_profile(
        response_type=response_type,
        intent_source=intent_source,
        intent_confidence=intent_confidence,
        retrieval_bias=retrieval_bias,
        answer_style=answer_style,
        workspace_overlay_present=workspace_overlay_authoritative,
    )
    preferred_mode = str(routing_profile.get("preferred_tool_mode") or "code")
    docs_enabled = bool(routing_profile.get("docs_enabled"))
    phase_log.classify(intent=response_type, method="hybrid")
    await _emit_progress(
        progress_callback,
        phase="classify",
        message="질문 의도와 답변 유형을 분석하는 중...",
        response_type=response_type,
    )

    if str(response_type or "").strip().lower() == "usage_guide":
        usage_query = (extract_symbol_candidates(clean_message) or [clean_message])[0]
        await _emit_progress(
            progress_callback,
            phase="retrieve",
            message="코드 사용 흐름과 예제를 수집하는 중...",
            tool="usage_bundle",
            query=usage_query,
        )
        prefetched_bundle = await _run_with_stage_timeout(
            collect_usage_guide_bundle(
                redis=redis,
                code_tools=chat_deps.code_tools,
                session_id=session_id,
                query=usage_query,
                limit=12,
                max_chars=max_chars,
                max_line_span=max_line_span,
            ),
            stage="retrieve",
            timeout_sec=retrieve_timeout_sec,
        )
        bundle = dict(prefetched_bundle.get("bundle", {}) or {})
        bundle_matches = list(prefetched_bundle.get("matches", []) or [])[:12]
        bundle_windows = list(prefetched_bundle.get("windows", []) or [])[:8]
        accumulator.add_code_matches(bundle_matches)
        for window in bundle_windows:
            accumulator.add_code_window(
                {
                    "path": window.get("path"),
                    "line_range": window.get("line_range"),
                    "content": window.get("content", ""),
                }
            )

        prefetched_tool_calls: List[Dict[str, Any]] = []
        if bundle:
            await _maybe_await_callback(
                tool_callback,
                "usage_bundle",
                {
                    "query": str(bundle.get("symbol") or clean_message),
                    "limit": 12,
                },
                json.dumps(bundle, ensure_ascii=False)[:500],
            )
            prefetched_tool_calls.append(
                {
                    "round": 0,
                    "tool": "usage_bundle",
                    "input": {
                        "query": str(bundle.get("symbol") or clean_message),
                        "limit": 12,
                    },
                    "output_preview": json.dumps(bundle, ensure_ascii=False)[:500],
                }
            )
            phase_log.retrieve(tool="usage_bundle", round=0, result_count=max(1, len(bundle_windows)))
            await _emit_progress(
                progress_callback,
                phase="retrieve",
                message="코드 근거를 정리했습니다. 답변 작성을 준비하는 중...",
                tool="usage_bundle",
                match_count=len(bundle_matches),
                window_count=len(bundle_windows),
            )

        if _usage_bundle_has_tutorial_signal(bundle):
            results = accumulator.to_results()
            sources = build_sources(results)
            await _maybe_await_callback(sources_callback, sources)
            await _emit_progress(
                progress_callback,
                phase="answer",
                message="근거를 바탕으로 답변을 작성하는 중...",
                source_count=len(sources),
            )
            generation_result = await _run_with_stage_timeout(
                _generate_usage_guide_answer_from_bundle(
                    state=chat_deps, # _generate doesn't strictly need state if it uses vllm_client etc, but we'll adapt it later if needed or pass chat_deps
                    model_name=model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt_seed=system_prompt_seed,
                    clean_message=clean_message,
                    bundle=bundle,
                    token_callback=token_callback,
                ),
                stage="answer",
                timeout_sec=answer_timeout_sec,
            )
            answer = str(generation_result.get("text") or "").strip()
            answer_truncated = bool(generation_result.get("truncated"))
            if answer:
                phase_log.verify(policy="answer")
                await _emit_progress(progress_callback, phase="verify", message="근거와 답변을 정리하는 중...")
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                phase_log.finalize(answer_len=len(answer), total_ms=elapsed_ms)
                return {
                    "answer": answer,
                    "results": results,
                    "sources": sources,
                    "query_time_ms": elapsed_ms,
                    "react": {
                        "mode": "usage_bundle_synthesis",
                        "preferred_tool_mode": preferred_mode,
                        "profile": routing_profile,
                        "rounds": 1,
                        "tool_calls": prefetched_tool_calls,
                        "thoughts": [],
                    },
                    "routing_profile": routing_profile,
                    "session_id": session_id,
                    "answer_truncated": answer_truncated,
                }

    if workspace_overlay_authoritative and str(response_type or "").strip().lower() == "code_explain":
        graph_answer = render_workspace_graph_answer(
            clean_message,
            workspace_graph,
            grounded_paths=grounded_overlay_paths,
        )
        if (
            workspace_graph_has_content(workspace_graph)
            and workspace_graph_is_ready_for_answer(workspace_graph, grounded_overlay_paths).get("passed")
            and graph_answer
        ):
            results = accumulator.to_results()
            sources = build_sources(results)
            await _maybe_await_callback(sources_callback, sources)
            phase_log.verify(policy="workspace_graph")
            await _emit_progress(progress_callback, phase="verify", message="워크스페이스 그래프를 바탕으로 답변을 정리하는 중...")
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            phase_log.finalize(answer_len=len(graph_answer), total_ms=elapsed_ms)
            return {
                "answer": graph_answer,
                "results": results,
                "sources": sources,
                "query_time_ms": elapsed_ms,
                "react": {
                    "mode": "workspace_graph",
                    "preferred_tool_mode": preferred_mode,
                    "profile": routing_profile,
                    "rounds": 0,
                    "tool_calls": [],
                    "thoughts": [],
                },
                "routing_profile": routing_profile,
                "session_id": session_id,
                "answer_truncated": False,
            }

        overlay_code_explain = await _run_with_stage_timeout(
            run_local_overlay_code_explain(
                chat_deps=chat_deps,
                accumulator=accumulator,
                clean_message=clean_message,
                local_overlay=local_overlay,
                model_name=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system_prompt_seed=system_prompt_seed,
                session_id=session_id,
                routing_profile=routing_profile,
                max_chars=max_chars,
                max_line_span=max_line_span,
                progress_callback=progress_callback,
                token_callback=token_callback,
                tool_callback=tool_callback,
            ),
            stage="answer",
            timeout_sec=answer_timeout_sec,
        )
        if overlay_code_explain:
            results = list(overlay_code_explain.get("results") or [])
            sources = list(overlay_code_explain.get("sources") or [])
            await _maybe_await_callback(sources_callback, sources)
            phase_log.verify(policy="local_overlay_code_explain")
            await _emit_progress(progress_callback, phase="verify", message="로컬 근거를 기준으로 답변을 정리하는 중..")
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            phase_log.finalize(
                answer_len=len(str(overlay_code_explain.get("answer") or "")),
                total_ms=elapsed_ms,
            )
            return {
                "answer": str(overlay_code_explain.get("answer") or ""),
                "results": results,
                "sources": sources,
                "query_time_ms": elapsed_ms,
                "react": {
                    "mode": str(overlay_code_explain.get("mode") or "local_overlay_code_explain"),
                    "preferred_tool_mode": preferred_mode,
                    "profile": routing_profile,
                    "rounds": 0,
                    "tool_calls": list(overlay_code_explain.get("tool_calls") or []),
                    "thoughts": [],
                },
                "routing_profile": routing_profile,
                "session_id": session_id,
                "answer_truncated": bool(overlay_code_explain.get("answer_truncated")),
            }

    # ------------------------------------------------------------------
    # Tool implementations (closures with redis injected)
    # ------------------------------------------------------------------

    async def _tool_doc_search(query: str, top_k: int = 8, collection: str = "") -> Dict[str, Any]:
        await _emit_progress(
            progress_callback,
            phase="retrieve",
            message=_tool_progress_message("doc_search", {"query": query}),
            tool="doc_search",
        )
        res = await search_docs(
            redis,
            chat_deps.search_svc,
            chat_deps.embed_model,
            query=str(query or "").strip(),
            filters=filters,
            top_k=max(1, min(int(top_k or 8), 50)),
            collection=(collection or active_collection),
            session_id=session_id,
            use_reranker=getattr(req, "use_reranker", False),
        )
        accumulator.add_doc_search_rows(list(res.get("results", []) or []))
        return {
            "query": res.get("query", query),
            "top_k": res.get("top_k", top_k),
            "result_count": len(res.get("results", []) or []),
            "results": res.get("results", []),
            "reason": res.get("reason"),
        }

    async def _tool_doc_read(chunk_ids: List[str], max_chars: int = 6000, collection: str = "") -> Dict[str, Any]:
        ids = [str(x).strip() for x in (chunk_ids or []) if str(x).strip()]
        await _emit_progress(
            progress_callback,
            phase="retrieve",
            message=_tool_progress_message("doc_read", {}),
            tool="doc_read",
        )
        res = await open_doc_chunks(
            redis,
            chat_deps.search_svc,
            chunk_ids=ids,
            max_chars=max(200, min(int(max_chars or 6000), 12000)),
            collection=(collection or active_collection),
            session_id=session_id,
            explicit_reference=False,
        )
        chunks = list(res.get("chunks", []) or [])
        accumulator.add_doc_chunks(chunks)
        return {
            "chunk_count": len(chunks),
            "chunks": chunks,
            "missing_chunk_ids": res.get("missing_chunk_ids", []),
            "reason": res.get("reason"),
        }

    async def _tool_grep(
        pattern: str = "",
        query: str = "",
        path_filter: str = "",
        limit: int = 10,
    ) -> Dict[str, Any]:
        query_text = str(pattern or query or "").strip()
        await _emit_progress(progress_callback, phase="retrieve", message=_tool_progress_message("grep", {"query": query_text}), tool="grep")
        res = await search_code(
            redis,
            chat_deps.code_tools,
            query_or_regex=query_text,
            path_filter=(path_filter or None),
            limit=max(1, min(int(limit or 10), 100)),
            session_id=session_id,
        )
        matches = list(res.get("matches", []) or [])
        if str(response_type or "").strip().lower() in {"usage_guide", "api_lookup"}:
            symbol_candidates = extract_symbol_candidates(query_text)
            matches = prioritize_usage_matches(
                matches,
                query_text=query_text,
                preferred_symbol=(symbol_candidates[0] if symbol_candidates else ""),
            )
            res["matches"] = matches
        accumulator.add_code_matches(matches)
        summarized_matches = [_summarize_code_match_for_prompt(row) for row in matches[: min(len(matches), 8)]]
        unique_paths: List[str] = []
        seen_paths = set()
        for row in matches:
            path_value = str(dict(row or {}).get("path") or dict(row or {}).get("file_path") or "").strip()
            lowered = path_value.lower()
            if not path_value or lowered in seen_paths:
                continue
            seen_paths.add(lowered)
            unique_paths.append(path_value)
        return {
            "query": res.get("query", query_text),
            "match_count": len(matches),
            "matches": summarized_matches,
            "path_count": len(unique_paths),
            "top_paths": unique_paths[:6],
            "reason": res.get("reason"),
            "scope": res.get("scope", "all"),
        }

    async def _tool_find_symbol(
        symbol: str = "",
        path_filter: str = "",
        limit: int = 6,
    ) -> Dict[str, Any]:
        symbol_text = str(symbol or "").strip()
        if not symbol_text:
            candidates = extract_symbol_candidates(clean_message)
            symbol_text = candidates[0] if candidates else clean_message

        await _emit_progress(
            progress_callback,
            phase="retrieve",
            message=_tool_progress_message("find_symbol", {"symbol": symbol_text}),
            tool="find_symbol",
        )
        res = await find_symbol(
            redis,
            chat_deps.code_tools,
            symbol=symbol_text,
            limit=max(1, min(int(limit or 6), 50)),
            session_id=session_id,
            path_filter=(path_filter or None),
        )
        matches = list(res.get("matches", []) or [])
        accumulator.add_code_matches(matches)
        return {
            "symbol": symbol_text,
            "match_count": len(matches),
            "matches": matches,
            "reason": res.get("reason"),
        }

    async def _tool_read(
        path: str = "",
        start_line: int = 1,
        end_line: int = 200,
    ) -> Dict[str, Any]:
        await _emit_progress(progress_callback, phase="retrieve", message=_tool_progress_message("read", {}), tool="read")
        requested_path = str(path or "").strip()
        normalized_requested_path = _normalize_engine_read_path(chat_deps.code_tools, requested_path)
        res = read_code_lines(
            chat_deps.code_tools,
            path=normalized_requested_path or requested_path,
            start_line=max(1, int(start_line or 1)),
            end_line=max(1, int(end_line or start_line or 1)),
            max_line_span=max_line_span,
            max_chars=max_chars,
        )
        if bool(res.get("found")):
            accumulator.add_code_window(
                {
                    "path": res.get("path"),
                    "line_range": res.get("line_range"),
                    "content": res.get("content", ""),
                }
            )
        return res

    async def _tool_glob(pattern: str = "**/*", limit: int = 100) -> Dict[str, Any]:
        res = await list_repo_files(
            redis,
            chat_deps.code_tools,
            glob=str(pattern or "**/*"),
            limit=max(1, min(int(limit or 100), 200)),
            session_id=session_id,
        )
        files = list(res.get("files") or [])
        return {
            "pattern": str(pattern or "**/*"),
            "file_count": len(files),
            "files": [_summarize_glob_file_for_prompt(item) for item in files[:12]],
            "truncated": bool(res.get("truncated")),
            "reason": res.get("reason"),
        }

    async def _tool_usage_bundle(query: str = "", limit: int = 12) -> Dict[str, Any]:
        await _emit_progress(
            progress_callback,
            phase="retrieve",
            message=_tool_progress_message("usage_bundle", {"query": query}),
            tool="usage_bundle",
        )
        bundle_result = await _run_with_stage_timeout(
            collect_usage_guide_bundle(
                redis=redis,
                code_tools=chat_deps.code_tools,
                session_id=session_id,
                query=str(query or clean_message or "").strip(),
                limit=max(6, min(int(limit or 12), 24)),
                max_chars=max_chars,
                max_line_span=max_line_span,
            ),
            stage="retrieve",
            timeout_sec=retrieve_timeout_sec,
        )
        accumulator.add_code_matches(list(bundle_result.get("matches", []) or []))
        for window in list(bundle_result.get("windows", []) or []):
            accumulator.add_code_window(
                {
                    "path": window.get("path"),
                    "line_range": window.get("line_range"),
                    "content": window.get("content", ""),
                }
            )
        return dict(bundle_result.get("bundle", {}) or {})

    # ------------------------------------------------------------------
    # Tool registration with per-tool output caps
    # ------------------------------------------------------------------

    if preferred_mode == "docs":
        registry.register(
            name="doc_search",
            func=_tool_doc_search,
            description="Document retrieval over indexed docs/chunks.",
            parameters=[
                ToolParam("query", "string", "Search query", required=True),
                ToolParam("top_k", "integer", "Maximum doc hits", required=False, default=8),
                ToolParam("collection", "string", "Qdrant collection", required=False, default=active_collection),
            ],
            max_output_chars=5000,
        )
        registry.register(
            name="doc_read",
            func=_tool_doc_read,
            description="Open full document chunks by chunk IDs.",
            parameters=[
                ToolParam("chunk_ids", "array", "Document chunk ids", required=True),
                ToolParam("max_chars", "integer", "Character cap for chunk text", required=False, default=6000),
                ToolParam("collection", "string", "Qdrant collection", required=False, default=active_collection),
            ],
            max_output_chars=8000,
        )
    else:
        if docs_enabled:
            registry.register(
                name="doc_search",
                func=_tool_doc_search,
                description="Document retrieval over indexed docs/chunks.",
                parameters=[
                    ToolParam("query", "string", "Search query", required=True),
                    ToolParam("top_k", "integer", "Maximum doc hits", required=False, default=8),
                    ToolParam("collection", "string", "Qdrant collection", required=False, default=active_collection),
                ],
                max_output_chars=5000,
            )
            registry.register(
                name="doc_read",
                func=_tool_doc_read,
                description="Open full document chunks by chunk IDs.",
                parameters=[
                    ToolParam("chunk_ids", "array", "Document chunk ids", required=True),
                    ToolParam("max_chars", "integer", "Character cap for chunk text", required=False, default=6000),
                    ToolParam("collection", "string", "Qdrant collection", required=False, default=active_collection),
                ],
                max_output_chars=8000,
            )

    if str(response_type or "").strip().lower() == "usage_guide":
        registry.register(
            name="usage_bundle",
            func=_tool_usage_bundle,
            description="Build a structured usage-guide evidence bundle for a concrete symbol, centered on grounded definition, usage, calls, updates, and supporting files. Use this first for how-to questions.",
            parameters=[
                ToolParam("query", "string", "Concrete symbol or usage question", required=False, default=clean_message),
                ToolParam("limit", "integer", "Maximum internal matches to inspect", required=False, default=12),
            ],
            max_output_chars=12000,
        )
    registry.register(
        name="find_symbol",
        func=_tool_find_symbol,
        description="Locate likely definition files and line ranges for a concrete class, control, method, or API symbol before broader code search.",
        parameters=[
            ToolParam("symbol", "string", "Concrete symbol name to resolve", required=False, default=""),
            ToolParam("path_filter", "string", "Optional path substring filter", required=False, default=""),
            ToolParam("limit", "integer", "Maximum matches", required=False, default=6),
        ],
        max_output_chars=5000,
    )
    registry.register(
        name="grep",
        func=_tool_grep,
        description="Search code paths and lines by text/regex across the available code roots.",
        parameters=[
            ToolParam("pattern", "string", "Regex/text pattern", required=False, default=""),
            ToolParam("query", "string", "Alternative query field", required=False, default=""),
            ToolParam("path_filter", "string", "Optional path substring filter", required=False, default=""),
            ToolParam("limit", "integer", "Maximum matches", required=False, default=10),
        ],
        max_output_chars=6000,
    )
    registry.register(
        name="read",
        func=_tool_read,
        description="Read code window for a file path and line range. Use paths returned by grep/find_symbol.",
        parameters=[
            ToolParam("path", "string", "File path from earlier search results", required=True),
            ToolParam("start_line", "integer", "Start line number", required=False, default=1),
            ToolParam("end_line", "integer", "End line number", required=False, default=200),
        ],
        max_output_chars=8000,
    )
    registry.register(
        name="glob",
        func=_tool_glob,
        description="List files across the available code roots by glob.",
        parameters=[
            ToolParam("pattern", "string", "Glob pattern", required=False, default="**/*"),
            ToolParam("limit", "integer", "Maximum files", required=False, default=100),
        ],
        max_output_chars=3000,
    )

    phase_log.plan(tools_selected=registry.list_tools(), preferred_mode=preferred_mode)
    await _emit_progress(
        progress_callback,
        phase="plan",
        message="검색 계획을 세우고 사용할 도구를 고르는 중...",
        tools=registry.list_tools(),
        preferred_mode=preferred_mode,
    )

    # ------------------------------------------------------------------
    # System prompt & LLM call setup
    # ------------------------------------------------------------------

    react_max_rounds = rag_config.react_max_rounds()
    exhaustive_local_code_explain = (
        workspace_overlay_authoritative
        and str(response_type or "").strip().lower() == "code_explain"
    )
    react_loop_max_rounds = 0 if exhaustive_local_code_explain else react_max_rounds
    react_loop_max_tool_calls = 0 if exhaustive_local_code_explain else rag_config.react_max_tool_calls()
    react_loop_timeout_sec = 0 if exhaustive_local_code_explain else rag_config.react_timeout_sec()
    use_native = (
        chat_deps.vllm_client is not None
        and rag_config.react_native_tool_calling()
        and not rag_config.react_model_prefers_text_tool_mode(model_name)
    )

    extra_instructions = (
        _build_tool_mode_hint(
            routing_profile,
            response_type=response_type,
            workspace_overlay_present=bool(routing_profile.get("workspace_overlay_present")),
        )
        + "\n\n"
        + _load_react_prompt_template(react_loop_max_rounds)
    )
    system_prompt = build_system_prompt(
        registry=registry,
        orchestration_prompt=(system_prompt_seed or ""),
        extra_instructions=extra_instructions,
        native_tool_calling=use_native,
    )

    # Fallback llm_call (used only when native tool calling is disabled)
    async def _llm_call(messages: List[Dict[str, str]], full_system_prompt: str) -> str:
        full_messages = [{"role": "system", "content": full_system_prompt}]
        full_messages.extend(messages)
        completion = await asyncio.to_thread(
            safe_chat_completion_create,
            model=model_name,
            messages=full_messages,
            max_tokens=max(256, int(max_tokens or 1400)),
            temperature=max(0.0, min(float(temperature), 0.4)),
            client=chat_deps.vllm_client,
            extra_body=build_chat_template_extra_body(rag_config.model_structured_generation_enable_thinking()),
        )
        if not completion.choices:
            return ""
        return str(completion.choices[0].message.content or "")

    def _current_grounded_paths() -> List[str]:
        paths: List[str] = list(grounded_overlay_paths or [])
        for row in list(accumulator.code_windows or []):
            path_value = str(dict(row or {}).get("path") or "").strip()
            if path_value:
                paths.append(path_value)
        seen = set()
        ordered: List[str] = []
        for item in paths:
            key = str(item or "").strip().replace("\\", "/").lower()
            if not key or key in seen:
                continue
            seen.add(key)
            ordered.append(str(item))
        return ordered

    retrieval_tracker: Dict[str, Any] = {
        "enabled": exhaustive_local_code_explain,
        "last_signature": (
            len(list(accumulator.doc_search_rows or [])),
            len(list(accumulator.doc_chunks or [])),
            len(list(accumulator.code_matches or [])),
            len(list(accumulator.code_windows or [])),
        ),
        "last_direct_read_count": len(list(accumulator.doc_chunks or [])) + len(list(accumulator.code_windows or [])),
        "tool_calls": 0,
        "stalled_tool_calls": 0,
        "empty_tool_calls": 0,
        "repeat_probe_calls": 0,
        "same_frontier_stall_calls": 0,
        "search_without_read_calls": 0,
        "low_signal_search_calls": 0,
        "last_frontier_signature": "",
        "probe_counts": {},
        "exhausted": False,
        "reason": "",
    }

    def _parse_tool_observation(observation: str) -> Dict[str, Any]:
        raw = str(observation or "").strip()
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
        except Exception:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _observation_has_signal(tool_name: str, observation: str) -> bool:
        payload = _parse_tool_observation(observation)
        if not payload:
            return False
        if bool(payload.get("found")) and str(payload.get("content") or "").strip():
            return True
        for key in ("matches", "results", "chunks", "files"):
            value = payload.get(key)
            if isinstance(value, list) and len(value) > 0:
                return True
        for key in ("match_count", "result_count", "chunk_count"):
            if int(payload.get(key) or 0) > 0:
                return True
        if tool_name == "read" and bool(payload.get("found")):
            return True
        return any(
            key not in {"reason", "scope", "query", "symbol", "path", "start_line", "end_line", "line_range", "top_k"}
            and bool(value)
            for key, value in payload.items()
        )

    def _frontier_signature(frontier: Dict[str, Any] | None) -> str:
        node = dict(frontier or {})
        path_value = str(node.get("path") or "").strip().replace("\\", "/").lower()
        symbol_value = str(node.get("symbol") or node.get("base_symbol") or "").strip().lower()
        return f"{path_value}::{symbol_value}"

    def _note_tool_outcome(tool_name: str, tool_input: Dict[str, Any], observation: str) -> None:
        if not bool(retrieval_tracker.get("enabled")):
            return
        direct_read_count = len(list(accumulator.doc_chunks or [])) + len(list(accumulator.code_windows or []))
        direct_read_progress = direct_read_count != int(retrieval_tracker.get("last_direct_read_count") or 0)
        retrieval_tracker["last_direct_read_count"] = direct_read_count
        current_signature = (
            len(list(accumulator.doc_search_rows or [])),
            len(list(accumulator.doc_chunks or [])),
            len(list(accumulator.code_matches or [])),
            len(list(accumulator.code_windows or [])),
        )
        progress = current_signature != tuple(retrieval_tracker.get("last_signature") or ())
        retrieval_tracker["last_signature"] = current_signature
        retrieval_tracker["tool_calls"] = int(retrieval_tracker.get("tool_calls") or 0) + 1

        probe_signature = json.dumps(
            {"tool": str(tool_name or ""), "input": dict(tool_input or {})},
            ensure_ascii=False,
            sort_keys=True,
        )
        probe_counts = dict(retrieval_tracker.get("probe_counts") or {})
        probe_counts[probe_signature] = int(probe_counts.get(probe_signature) or 0) + 1
        retrieval_tracker["probe_counts"] = probe_counts

        if progress:
            retrieval_tracker["stalled_tool_calls"] = 0
            retrieval_tracker["empty_tool_calls"] = 0
            retrieval_tracker["repeat_probe_calls"] = 0
            retrieval_tracker["same_frontier_stall_calls"] = 0
            if direct_read_progress:
                retrieval_tracker["search_without_read_calls"] = 0
                retrieval_tracker["low_signal_search_calls"] = 0
            return

        retrieval_tracker["stalled_tool_calls"] = int(retrieval_tracker.get("stalled_tool_calls") or 0) + 1
        has_signal = _observation_has_signal(tool_name, observation)
        if not has_signal:
            retrieval_tracker["empty_tool_calls"] = int(retrieval_tracker.get("empty_tool_calls") or 0) + 1
        if int(probe_counts.get(probe_signature) or 0) > 1:
            retrieval_tracker["repeat_probe_calls"] = int(retrieval_tracker.get("repeat_probe_calls") or 0) + 1
        if tool_name in {"grep", "glob", "find_symbol"} and not direct_read_progress:
            retrieval_tracker["search_without_read_calls"] = int(retrieval_tracker.get("search_without_read_calls") or 0) + 1
            if not has_signal or tool_name == "glob":
                retrieval_tracker["low_signal_search_calls"] = int(retrieval_tracker.get("low_signal_search_calls") or 0) + 1
        elif direct_read_progress:
            retrieval_tracker["search_without_read_calls"] = 0
            retrieval_tracker["low_signal_search_calls"] = 0

        frontier_signature = _frontier_signature(_evaluate_retrieval_state().get("frontier"))
        if frontier_signature and frontier_signature == str(retrieval_tracker.get("last_frontier_signature") or ""):
            retrieval_tracker["same_frontier_stall_calls"] = int(retrieval_tracker.get("same_frontier_stall_calls") or 0) + 1
        else:
            retrieval_tracker["same_frontier_stall_calls"] = 0
        retrieval_tracker["last_frontier_signature"] = frontier_signature

    def _maybe_mark_retrieval_exhausted(state: Dict[str, Any]) -> bool:
        if not bool(retrieval_tracker.get("enabled")):
            return False
        if bool(state.get("ok")):
            return False
        if bool(retrieval_tracker.get("exhausted")):
            return True
        if int(retrieval_tracker.get("tool_calls") or 0) < 6:
            return False

        frontier_signature = _frontier_signature(state.get("frontier"))
        exhausted = False
        reason = ""
        if (
            int(retrieval_tracker.get("stalled_tool_calls") or 0) >= 4
            and int(retrieval_tracker.get("empty_tool_calls") or 0) >= 2
        ):
            exhausted = True
            reason = "no_new_evidence"
        elif (
            frontier_signature
            and int(retrieval_tracker.get("same_frontier_stall_calls") or 0) >= 3
            and int(retrieval_tracker.get("repeat_probe_calls") or 0) >= 2
        ):
            exhausted = True
            reason = "frontier_exhausted"
        elif (
            int(state.get("direct_read_count") or 0) == 0
            and int(retrieval_tracker.get("search_without_read_calls") or 0) >= 6
            and int(retrieval_tracker.get("low_signal_search_calls") or 0) >= 3
        ):
            exhausted = True
            reason = "search_without_read_exhausted"
        elif (
            int(retrieval_tracker.get("tool_calls") or 0) >= 18
            and int(state.get("direct_read_count") or 0) <= 1
            and int(retrieval_tracker.get("search_without_read_calls") or 0) >= 8
        ):
            exhausted = True
            reason = "search_loop_exhausted"

        if exhausted:
            retrieval_tracker["exhausted"] = True
            retrieval_tracker["reason"] = reason
            retrieval_tracker["last_frontier_signature"] = frontier_signature
        return exhausted

    def _render_exhaustion_feedback(frontier: Dict[str, Any] | None = None) -> str:
        node = dict(frontier or {})
        target_bits = [
            str(node.get("path") or "").strip(),
            str(node.get("symbol") or node.get("base_symbol") or "").strip(),
        ]
        target_bits = [item for item in target_bits if item]
        prefix = "The current retrieval frontier appears exhausted after repeated probes."
        if target_bits:
            prefix = (
                "The current retrieval frontier appears exhausted around "
                + " / ".join(target_bits[:2])
                + "."
            )
        return (
            prefix
            + "\nStop calling tools and write the final answer from the grounded evidence already gathered."
            + "\nIf a relation, caller chain, or flow could not be confirmed, state explicitly that the supporting code was not found after exhaustive retrieval."
        )

    async def _on_tool_call(tool_name: str, tool_input: Dict[str, Any], observation: str) -> None:
        await _maybe_await_callback(tool_callback, tool_name, tool_input, observation)
        await _emit_progress(
            progress_callback,
            phase="retrieve",
            message=_tool_progress_message(tool_name, tool_input),
            tool=tool_name,
            output_preview=str(observation or "")[:180],
        )
        _note_tool_outcome(tool_name, tool_input, observation)

    def _evaluate_retrieval_state() -> Dict[str, Any]:
        current_results = accumulator.to_results()
        current_sources = build_sources(current_results)
        evidence_gate = build_evidence_gate(current_results, current_sources)
        current_grounded_paths = _current_grounded_paths()
        graph_gate = workspace_graph_is_ready_for_answer(workspace_graph, current_grounded_paths)
        code_window_count = len(list(accumulator.code_windows or []))
        doc_chunk_count = len(list(accumulator.doc_chunks or []))
        direct_read_count = code_window_count + doc_chunk_count
        search_only_count = len(list(accumulator.code_matches or [])) + len(list(accumulator.doc_search_rows or []))
        response_kind = str(response_type or "").strip().lower()

        issues: List[str] = []
        if direct_read_count == 0 and response_kind in {"code_explain", "usage_guide", "troubleshooting"}:
            issues.append("missing_direct_reads")
        if search_only_count > 0 and direct_read_count == 0:
            issues.append("search_without_read")
        if workspace_overlay_authoritative and response_kind == "code_explain":
            issues.extend(list(graph_gate.get("issues") or []))
        elif not bool(evidence_gate.get("passed")) and search_only_count > 0:
            issues.append("thin_evidence")

        frontier = None
        frontiers = list(graph_gate.get("frontiers") or [])
        if frontiers:
            frontier = dict(frontiers[0] or {})
        elif isinstance(dict(workspace_graph.get("graph_state") or {}).get("frontier"), dict):
            frontier = dict(dict(workspace_graph.get("graph_state") or {}).get("frontier") or {})

        return {
            "ok": len(issues) == 0,
            "issues": issues,
            "frontier": frontier or {},
            "graph_gate": graph_gate,
            "evidence_gate": evidence_gate,
            "direct_read_count": direct_read_count,
            "search_only_count": search_only_count,
            "results": current_results,
            "sources": current_sources,
            "grounded_paths": current_grounded_paths,
        }

    def _render_retrieval_feedback(issues: List[str], frontier: Dict[str, Any] | None = None) -> str:
        frontier = dict(frontier or {})
        feedback_lines = [
            "More evidence is still needed before answering.",
        ]
        if "missing_direct_reads" in issues:
            feedback_lines.append("Read at least one grounded code or document span before finalizing.")
        if "search_without_read" in issues:
            feedback_lines.append("You already have search hits. Read the strongest matching span instead of answering from search output alone.")
        if "no_grounded_graph_paths" in issues:
            feedback_lines.append("The local workspace graph is still ungrounded. Read the strongest file or symbol span from the graph focus.")
        if "focus_not_grounded" in issues:
            feedback_lines.append("The current graph focus is not grounded yet. Read the focused symbol or file span before answering.")
        if "open_frontier" in issues:
            target_bits = [
                str(frontier.get("path") or "").strip(),
                str(frontier.get("symbol") or frontier.get("base_symbol") or "").strip(),
            ]
            target_bits = [item for item in target_bits if item]
            if target_bits:
                feedback_lines.append(
                    "The workspace graph still has an open frontier around "
                    + " / ".join(target_bits[:2])
                    + ". Continue probing that frontier before answering."
                )
            else:
                feedback_lines.append("The workspace graph still has an open frontier. Continue probing it before answering.")
        if "uncovered_graph_nodes" in issues:
            feedback_lines.append("You have discovered additional graph nodes but have not read all of their grounded spans yet.")
        if "thin_graph_coverage" in issues:
            feedback_lines.append("The workspace graph coverage is still thin. Read another grounded span from the current chain before answering.")
        if "planner_missing_dimensions" in issues:
            feedback_lines.append("The planner still marks some evidence dimensions as missing. Continue retrieval until those missing dimensions are covered or exhausted.")
        if "thin_evidence" in issues:
            feedback_lines.append("The overall evidence set is still thin. Read the strongest matched span before answering.")
        return "\n".join(feedback_lines)

    async def _build_round_instruction(round_idx: int) -> Dict[str, Any]:
        state = _evaluate_retrieval_state()
        if bool(state.get("ok")):
            return {}
        if _maybe_mark_retrieval_exhausted(state):
            return {
                "message": _render_exhaustion_feedback(dict(state.get("frontier") or {})),
                "force_answer": True,
                "stop": True,
            }

        frontier = dict(state.get("frontier") or {})
        guidance: List[str] = [
            "Retrieval is still in progress. Do not answer yet.",
        ]
        if frontier:
            frontier_path = str(frontier.get("path") or "").strip()
            frontier_symbol = str(frontier.get("symbol") or frontier.get("base_symbol") or "").strip()
            if frontier_path or frontier_symbol:
                guidance.append(
                    "Prioritize the current frontier: "
                    + " / ".join([item for item in [frontier_path, frontier_symbol] if item][:2])
                    + "."
                )
        guidance.append(_render_retrieval_feedback(list(state.get("issues") or []), frontier))
        guidance.append("Use tools to close the remaining evidence gaps before drafting the final answer.")
        return {"message": "\n".join(guidance)}

    async def _check_retrieval_ready(answer_text: str, round_idx: int) -> Dict[str, Any]:
        state = _evaluate_retrieval_state()

        if bool(state.get("ok")) or _maybe_mark_retrieval_exhausted(state):
            return {"ok": True, "answer": answer_text}
        return {
            "ok": False,
            "feedback": _render_retrieval_feedback(
                list(state.get("issues") or []),
                dict(state.get("frontier") or {}),
            ),
            "answer": answer_text,
        }

    async def _validate_candidate_answer(answer_text: str, round_idx: int) -> Dict[str, Any]:
        draft = str(answer_text or "").strip()
        if not draft:
            return {
                "ok": False,
                "feedback": "The draft answer is empty. Read the most relevant grounded code span before answering.",
                "answer": "",
            }

        state = _evaluate_retrieval_state()
        current_results = accumulator.to_results()
        current_sources = build_sources(current_results)
        guarded_answer, guard_meta = enforce_source_whitelist(
            draft,
            current_sources,
            current_results,
            session_id,
            extra_allowed_paths=list(state.get("grounded_paths") or _current_grounded_paths()),
        )
        provenance = build_provenance_report(guarded_answer, current_results, current_sources)
        unsupported_claims = detect_unsupported_claims(guarded_answer, current_results)
        evidence_fragments: List[str] = []
        for item in current_results:
            payload = dict(item.get("payload", {}) or {})
            evidence_fragments.append(str(payload.get("text") or ""))
            evidence_fragments.append(str(payload.get("file_path") or ""))
            evidence_fragments.append(str(payload.get("source_file") or ""))
        for src in current_sources:
            evidence_fragments.append(str(dict(src or {}).get("file_path") or ""))
        for node in list(dict(workspace_graph or {}).get("nodes") or []):
            if not isinstance(node, dict):
                continue
            evidence_fragments.append(str(node.get("path") or ""))
        for node in list(dict(dict(workspace_graph or {}).get("graph_state") or {}).get("chain") or []):
            if not isinstance(node, dict):
                continue
            evidence_fragments.append(str(node.get("path") or ""))
            evidence_fragments.append(str(node.get("symbol") or ""))
            evidence_fragments.append(str(node.get("base_symbol") or ""))
        evidence_fragments.extend(list(state.get("grounded_paths") or _current_grounded_paths()))
        grounded_tokens = {
            token.lower()
            for token in _extract_code_like_mentions(" ".join(evidence_fragments))
        }
        unresolved_symbols = [
            token
            for token in _extract_code_like_mentions(guarded_answer)
            if token.lower() not in grounded_tokens
        ]

        issues: List[str] = []
        if not bool(guard_meta.get("passed", True)):
            issues.append("ungrounded_paths")
        if not bool(provenance.get("all_code_blocks_grounded", True)):
            issues.append("ungrounded_code_blocks")
        if unresolved_symbols:
            issues.append("ungrounded_symbols")
        unsupported_count = int(unsupported_claims.get("unsupported_count") or 0)
        other_issue_count = len(issues)
        if unsupported_count > 0 and (
            int(state.get("direct_read_count") or 0) == 0
            or other_issue_count > 0
            or unsupported_count >= 3
        ):
            issues.append("unsupported_claims")

        if not issues:
            return {"ok": True, "answer": guarded_answer}

        feedback_lines = [
            "The drafted answer still contains claims that are not grounded in retrieved evidence.",
        ]
        if "ungrounded_paths" in issues:
            examples = list(guard_meta.get("ungrounded_examples") or [])
            suffix = f" Examples: {', '.join(examples[:3])}." if examples else ""
            feedback_lines.append(
                "You mentioned file paths that were not confirmed by tool results. Use another search or read step before naming those files."
                + suffix
            )
        if "ungrounded_code_blocks" in issues:
            feedback_lines.append("Any code block in the answer must come from a grounded read result.")
        if unresolved_symbols:
            feedback_lines.append(
                "You mentioned unresolved code symbols such as "
                + ", ".join(unresolved_symbols[:4])
                + ". Ground them with tool evidence or remove those claims."
            )
        if "unsupported_claims" in issues:
            feedback_lines.append("Some answer sentences do not overlap with the retrieved evidence. Verify those claims with more tool calls before answering.")
        return {
            "ok": False,
            "feedback": "\n".join(feedback_lines),
            "answer": guarded_answer,
        }

    await _emit_progress(progress_callback, phase="retrieve", message="근거 수집을 시작합니다...")

    react_result = await run_react_loop(
        llm_call=_llm_call,
        registry=registry,
        messages=_build_history_messages(
            history_messages,
            clean_message,
            local_overlay_context=local_overlay_context,
        ),
        system_prompt=system_prompt,
        max_rounds=react_loop_max_rounds,
        max_tool_calls=react_loop_max_tool_calls,
        on_tool_call=_on_tool_call,
        round_controller=_build_round_instruction,
        answer_readiness_checker=_check_retrieval_ready,
        answer_validator=_validate_candidate_answer,
        phase_log=phase_log,
        # native function calling
        openai_client=chat_deps.vllm_client if use_native else None,
        model_name=model_name if use_native else None,
        max_tokens=max(256, int(max_tokens or 1400)),
        temperature=max(0.0, min(float(temperature), 0.4)),
        completion_extra_body=build_chat_template_extra_body(
            rag_config.model_native_generation_enable_thinking()
        ),
        timeout_sec=react_loop_timeout_sec,
    )

    answer = str(react_result.get("answer") or "").strip()
    react_error = str(react_result.get("error") or "").strip()

    # Phase log: verify & finalize
    has_error = bool(react_error)
    evidence_policy = "error" if has_error else ("answer" if answer else "insufficient")
    phase_log.verify(policy=evidence_policy)
    await _emit_progress(progress_callback, phase="verify", message="근거와 답변을 정리하는 중...")

    results = accumulator.to_results()
    sources = build_sources(results)
    await _maybe_await_callback(sources_callback, sources)
    answer_truncated = False
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    phase_log.finalize(answer_len=len(answer), total_ms=elapsed_ms)

    return {
        "answer": answer,
        "results": results,
        "sources": sources,
        "query_time_ms": elapsed_ms,
        "reasoning": {
            "summary": phase_log.summary(),
            "trace": phase_log.trace(),
            "narrative": phase_log.narrative(),
        },
        "react": {
            "mode": "native_tool_calls" if use_native else "text_json",
            "preferred_tool_mode": preferred_mode,
            "profile": routing_profile,
            "rounds": int(react_result.get("rounds") or 0),
            "tool_calls": react_result.get("tool_calls", []),
            "thoughts": react_result.get("thoughts", []),
        },
        "routing_profile": routing_profile,
        "session_id": session_id,
        "answer_truncated": answer_truncated,
        "error": react_error,
    }




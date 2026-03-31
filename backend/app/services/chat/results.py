import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastapi import HTTPException

from .answer_quality import build_context_pack, build_provenance_report, detect_unsupported_claims
from .cancellation import ensure_run_not_cancelled
from .evidence import apply_evidence_policy, build_evidence_gate
from .grounding import enforce_source_whitelist
from .http import raise_http_error
from .layered_merge import build_layer_manifest, build_local_overlay_evidence, extract_local_workspace_overlay
from .preparation import PreparedChatExecution, record_prepared_error
from .question_contract import normalize_question_contract
from .react.engine import StageTimeoutError
from .runtime_profile import build_react_routing_payload
from .workspace_graph import (
    build_workspace_grounding_report,
    collect_grounded_overlay_paths,
    extract_workspace_graph,
    render_workspace_graph_answer,
    workspace_graph_has_content,
    workspace_graph_has_grounded_focus,
    workspace_graph_is_ready_for_answer,
)
from ..tools.access import resolve_tool_user_context


logger = logging.getLogger(__name__)

StatusCallback = Optional[Callable[[Dict[str, Any]], Awaitable[None] | None]]
TokenCallback = Optional[Callable[[str], Awaitable[None] | None]]
SourcesCallback = Optional[Callable[[List[Dict[str, Any]]], Awaitable[None] | None]]


def _uses_korean(text: str) -> bool:
    return any("\uac00" <= char <= "\ud7a3" for char in str(text or ""))


def _overlay_changed_paths(local_overlay: Dict[str, Any] | None) -> List[str]:
    overlay = dict(local_overlay or {})
    paths = [str(item).strip() for item in list(overlay.get("workspace_change_paths") or []) if str(item).strip()]
    selected = str(overlay.get("selected_file_path") or "").strip()
    if selected and selected not in paths:
        paths.insert(0, selected)
    seen = set()
    ordered: List[str] = []
    for item in paths:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        ordered.append(item)
    return ordered


def _render_overlay_review_answer(question: str, local_overlay: Dict[str, Any] | None) -> str:
    overlay = dict(local_overlay or {})
    changed_paths = _overlay_changed_paths(overlay)
    diff_text = str(overlay.get("workspace_diff") or "").strip()
    selected_path = str(overlay.get("selected_file_path") or "").strip()
    uses_korean = _uses_korean(question)

    if uses_korean:
        lines = ["## 코드 리뷰", "", "현재 제공된 오버레이 증거만으로는 확정 가능한 결함을 확인하지 못했습니다.", ""]
        if changed_paths:
            lines.append("### 확인된 변경 파일")
            lines.extend(f"- `{path}`" for path in changed_paths[:5])
            lines.append("")
        lines.append("### 근거")
        if selected_path:
            lines.append(f"- 선택 파일: `{selected_path}`")
        if diff_text:
            snippet = " ".join(diff_text.split())[:320]
            lines.append(f"- 워크스페이스 diff 오버레이: `{snippet}`")
        lines.append("")
        lines.append("### 한계")
        lines.append("- 이번 응답은 클라이언트가 첨부한 로컬 오버레이와 diff만 근거로 삼았습니다.")
        lines.append("- 이 실행에서는 추가 서버 읽기나 테스트 결과가 그라운딩되지 않아 구체 결함을 확정하지는 않았습니다.")
        return "\n".join(lines).strip()

    lines = ["## Code Review", "", "No confirmed defect findings were identified from the grounded overlay evidence alone.", ""]
    if changed_paths:
        lines.append("### Changed Files")
        lines.extend(f"- `{path}`" for path in changed_paths[:5])
        lines.append("")
    lines.append("### Grounded Evidence")
    if selected_path:
        lines.append(f"- Selected file: `{selected_path}`")
    if diff_text:
        snippet = " ".join(diff_text.split())[:320]
        lines.append(f"- Workspace diff overlay: `{snippet}`")
    lines.append("")
    lines.append("### Limits")
    lines.append("- This answer relied on the client-provided local overlay and diff evidence.")
    lines.append("- No additional grounded server reads or test results were available in this run to confirm a concrete defect.")
    return "\n".join(lines).strip()


def _source_paths(sources: List[Dict[str, Any]] | None) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in list(sources or []):
        if not isinstance(item, dict):
            continue
        path = str(
            item.get("file_path")
            or item.get("path")
            or item.get("source_path")
            or item.get("source")
            or ""
        ).strip()
        if not path:
            continue
        normalized = path.replace("\\", "/")
        lowered = normalized.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        ordered.append(normalized)
    return ordered


def _overlay_review_evidence_present(local_overlay: Dict[str, Any] | None) -> bool:
    overlay = dict(local_overlay or {})
    return bool(
        _overlay_changed_paths(overlay)
        or str(overlay.get("workspace_diff") or "").strip()
        or str(overlay.get("selected_file_path") or "").strip()
    )


def _result_source_kind_counts(results: List[Dict[str, Any]] | None) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in list(results or []):
        if not isinstance(item, dict):
            continue
        payload = dict(item.get("payload") or {}) if isinstance(item.get("payload"), dict) else {}
        kind = str(payload.get("source_kind") or "").strip().lower()
        if not kind:
            continue
        counts[kind] = counts.get(kind, 0) + 1
    return counts


def _overlay_review_has_server_direct_reads(results: List[Dict[str, Any]] | None) -> bool:
    counts = _result_source_kind_counts(results)
    return any(
        int(counts.get(kind) or 0) > 0
        for kind in ("code_tool", "documents")
    )


def _answer_matches_review_contract(answer: str) -> bool:
    text = str(answer or "").strip().lower()
    if not text:
        return False
    markers = (
        "## code review",
        "### changed files",
        "### grounded evidence",
        "no confirmed defect findings",
        "confirmed findings",
        "### findings",
        "### limits",
    )
    return any(marker in text for marker in markers)


def _sources_align_with_overlay(local_overlay: Dict[str, Any] | None, sources: List[Dict[str, Any]] | None) -> bool:
    overlay = dict(local_overlay or {})
    allowed = {
        path.replace("\\", "/").lower()
        for path in [
            *(_overlay_changed_paths(overlay) or []),
            str(overlay.get("selected_file_path") or "").strip(),
        ]
        if str(path).strip()
    }
    source_paths = _source_paths(sources)
    if not source_paths:
        return True
    if not allowed:
        return False
    return all(path.lower() in allowed for path in source_paths)


def _results_align_with_overlay(local_overlay: Dict[str, Any] | None, results: List[Dict[str, Any]] | None) -> bool:
    overlay = dict(local_overlay or {})
    allowed = {
        path.replace("\\", "/").lower()
        for path in [
            *(_overlay_changed_paths(overlay) or []),
            str(overlay.get("selected_file_path") or "").strip(),
        ]
        if str(path).strip()
    }
    if not allowed:
        return False
    result_paths: List[str] = []
    for item in list(results or []):
        if not isinstance(item, dict):
            continue
        payload = dict(item.get("payload") or {}) if isinstance(item.get("payload"), dict) else {}
        path = str(payload.get("file_path") or payload.get("source_file") or "").strip()
        if not path:
            continue
        result_paths.append(path.replace("\\", "/"))
    if not result_paths:
        return True
    return all(path.lower() in allowed for path in result_paths)


def _should_render_overlay_review_fallback(
    *,
    question_contract: Dict[str, Any] | None,
    local_overlay: Dict[str, Any] | None,
    results: List[Dict[str, Any]] | None,
    sources: List[Dict[str, Any]] | None,
) -> bool:
    normalized_contract = normalize_question_contract(question_contract)
    if str(normalized_contract.get("kind") or "").strip().lower() != "code_review":
        return False
    overlay = dict(local_overlay or {})
    if not bool(overlay.get("present")):
        return False
    if not _overlay_review_evidence_present(overlay):
        return False
    if not _sources_align_with_overlay(overlay, sources):
        return False
    return _results_align_with_overlay(overlay, results)


def _should_force_overlay_review_answer(
    *,
    question_contract: Dict[str, Any] | None,
    local_overlay: Dict[str, Any] | None,
    results: List[Dict[str, Any]] | None,
    sources: List[Dict[str, Any]] | None,
    answer: str = "",
) -> bool:
    if not _should_render_overlay_review_fallback(
        question_contract=question_contract,
        local_overlay=local_overlay,
        results=results,
        sources=sources,
    ):
        return False
    if not _overlay_review_has_server_direct_reads(results):
        return True
    return not _answer_matches_review_contract(answer)


def _should_render_workspace_graph_answer(
    *,
    question_contract: Dict[str, Any] | None,
    workspace_graph: Dict[str, Any],
    grounded_overlay_paths: List[str],
) -> bool:
    normalized_contract = normalize_question_contract(question_contract)
    contract_kind = str(normalized_contract.get("kind") or "").strip().lower()
    if contract_kind != "code_flow_explanation":
        return False
    if not workspace_graph_has_content(workspace_graph):
        return False
    gate = workspace_graph_is_ready_for_answer(workspace_graph, grounded_overlay_paths)
    if bool(gate.get("passed")):
        return True
    return bool(workspace_graph_has_grounded_focus(workspace_graph, grounded_overlay_paths))


async def maybe_await_callback(callback, *args, **kwargs) -> None:
    if callback is None:
        return
    result = callback(*args, **kwargs)
    if asyncio.iscoroutine(result):
        await result


async def _raise_if_cancel_requested(prepared: PreparedChatExecution, *, stage: str) -> None:
    await ensure_run_not_cancelled(prepared, stage=stage)


def _retry_policy(prepared: PreparedChatExecution) -> Dict[str, Any]:
    raw = getattr(prepared.req, "retry_policy", None)
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump()
    raw = dict(raw or {})
    return {
        "max_attempts": max(1, int(raw.get("max_attempts", 1) or 1)),
        "retry_backoff_ms": max(0, int(raw.get("retry_backoff_ms", 0) or 0)),
        "retry_on_timeout": bool(raw.get("retry_on_timeout", True)),
        "retry_on_runtime_error": bool(raw.get("retry_on_runtime_error", True)),
    }


def _is_retryable_exception(exc: Exception, retry_policy: Dict[str, Any]) -> bool:
    if isinstance(exc, HTTPException):
        return False
    if isinstance(exc, StageTimeoutError):
        return bool(retry_policy.get("retry_on_timeout"))
    return bool(retry_policy.get("retry_on_runtime_error"))


async def _sleep_backoff(retry_policy: Dict[str, Any], attempt: int) -> None:
    backoff_ms = int(retry_policy.get("retry_backoff_ms", 0) or 0)
    if backoff_ms <= 0:
        return
    await asyncio.sleep((backoff_ms * max(1, attempt)) / 1000.0)


async def _record_task_step(
    prepared: PreparedChatExecution,
    *,
    task_key: str,
    title: str,
    owner_agent: str,
    kind: str,
    status: str,
    input_data: Any = None,
    output_preview: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    await prepared.run_svc.upsert_task(
        prepared.run_id,
        task_key,
        title=title,
        status=status,
        owner_agent=owner_agent,
        metadata=metadata,
    )
    await prepared.run_svc.append_step(
        prepared.run_id,
        task_key,
        title=title,
        kind=kind,
        status=status,
        owner_agent=owner_agent,
        input_data=input_data,
        output_preview=output_preview,
        metadata=metadata,
    )


async def _execute_with_retries(
    prepared: PreparedChatExecution,
    *,
    task_key: str,
    title: str,
    owner_agent: str,
    factory: Callable[[], Awaitable[Any]],
) -> Any:
    retry_policy = _retry_policy(prepared)
    max_attempts = int(retry_policy["max_attempts"])
    last_exc: Optional[Exception] = None

    for attempt in range(1, max_attempts + 1):
        await _raise_if_cancel_requested(prepared, stage=task_key)
        await _record_task_step(
            prepared,
            task_key=task_key,
            title=title,
            owner_agent=owner_agent,
            kind="attempt",
            status="running",
            metadata={"attempt": attempt, "max_attempts": max_attempts},
        )
        try:
            result = await factory()
            await _record_task_step(
                prepared,
                task_key=task_key,
                title=title,
                owner_agent=owner_agent,
                kind="attempt",
                status="completed",
                metadata={"attempt": attempt, "max_attempts": max_attempts},
            )
            if attempt > 1:
                await prepared.run_svc.add_artifact(
                    prepared.run_id,
                    artifact_type="retry_trace",
                    title=f"{task_key} recovered on retry",
                    content={"task_key": task_key, "attempt": attempt, "max_attempts": max_attempts},
                    owner_agent=owner_agent,
                    task_key=task_key,
                    metadata={"attempt": attempt},
                )
            return result
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            retryable = _is_retryable_exception(exc, retry_policy)
            await _record_task_step(
                prepared,
                task_key=task_key,
                title=title,
                owner_agent=owner_agent,
                kind="attempt",
                status="failed",
                output_preview=str(exc)[:300],
                metadata={
                    "attempt": attempt,
                    "max_attempts": max_attempts,
                    "retryable": retryable,
                    "error_type": type(exc).__name__,
                },
            )
            await prepared.run_svc.add_artifact(
                prepared.run_id,
                artifact_type="retry_attempt",
                title=f"{task_key} attempt failed",
                content={"task_key": task_key, "attempt": attempt, "error": str(exc)},
                owner_agent=owner_agent,
                task_key=task_key,
                metadata={"retryable": retryable, "error_type": type(exc).__name__},
            )
            if attempt >= max_attempts or not retryable:
                raise
            await _sleep_backoff(retry_policy, attempt)

    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"{task_key} execution failed without an exception")


async def _load_resume_artifacts(prepared: PreparedChatExecution) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    react_artifact = await prepared.run_svc.get_latest_artifact(prepared.run_id, "react_payload_snapshot")
    workspace_artifact = await prepared.run_svc.get_latest_artifact(prepared.run_id, "workspace_snapshot")
    react_payload = dict(react_artifact.get("content") or {}) if react_artifact and isinstance(react_artifact.get("content"), dict) else None
    workspace_snapshot = dict(workspace_artifact.get("content") or {}) if workspace_artifact and isinstance(workspace_artifact.get("content"), dict) else None
    return react_payload, workspace_snapshot


def _should_reuse_resume_payload(prepared: PreparedChatExecution, task_key: str) -> bool:
    resume_task = str(prepared.resume_from_task_key or "").strip().lower()
    if not resume_task:
        return False
    if task_key == "retrieve":
        return resume_task in {"answer", "verify", "workspace_analysis"}
    if task_key == "workspace_analysis":
        return resume_task in {"retrieve", "answer", "verify"}
    return False


def _build_react_call(
    prepared: PreparedChatExecution,
    *,
    status_callback: StatusCallback,
    token_callback: TokenCallback,
    sources_callback: SourcesCallback,
    sources_recorded_ref: Dict[str, bool],
):
    async def _progress(payload: Dict[str, Any]) -> None:
        phase = str(payload.get("phase") or "").strip().lower()
        mapped_phase = "plan" if phase == "classify" else (phase or "plan")
        extra = {k: v for k, v in payload.items() if k not in {"phase", "message"}}
        await prepared.run_tracker.record_phase(mapped_phase, str(payload.get("message") or ""), **extra)
        await maybe_await_callback(status_callback, payload)

    async def _tool_call(tool_name: str, tool_input: Dict[str, Any], observation: str) -> None:
        await prepared.run_tracker.record_tool_call(tool_name, tool_input, observation)

    async def _token(token: str) -> None:
        await maybe_await_callback(token_callback, token)

    async def _sources(rows: List[Dict[str, Any]]) -> None:
        if not rows:
            return
        sources_recorded_ref["value"] = True
        await prepared.run_tracker.record_sources(rows)
        await maybe_await_callback(sources_callback, rows)

    return prepared.backends.reasoning.run_react_generation(
        prepared,
        status_callback=_progress,
        token_callback=_token,
        sources_callback=_sources,
        tool_callback=_tool_call,
    )


async def run_react_payload(
    prepared: PreparedChatExecution,
    *,
    status_callback: StatusCallback = None,
    token_callback: TokenCallback = None,
    sources_callback: SourcesCallback = None,
) -> tuple[Dict[str, Any], bool, Optional[Dict[str, Any]]]:
    sources_recorded_ref: Dict[str, bool] = {"value": False}
    workspace_snapshot: Optional[Dict[str, Any]] = None
    react_payload: Optional[Dict[str, Any]] = None

    await _raise_if_cancel_requested(prepared, stage="plan")

    workspace_backend = getattr(prepared.backends, "workspace", None)
    workspace_redis = getattr(workspace_backend, "redis", None)
    if workspace_redis is not None:
        await resolve_tool_user_context(workspace_redis, session_id=prepared.session_id, user_id=None)

    await prepared.run_tracker.record_handoff(
        from_agent="planner",
        to_agent="retriever",
        reason="plan_ready",
        payload={"task_key": "retrieve"},
        task_key="plan",
    )

    local_overlay = extract_local_workspace_overlay(prepared.req)
    workspace_path = str(local_overlay.get("workspace_path") or getattr(prepared.req, "workspace_id", "") or "").strip()
    has_workspace_analyst = "workspace_analyst" in list(prepared.execution_plan.get("required_agents") or []) and bool(workspace_path)

    resume_react_payload, resume_workspace_snapshot = await _load_resume_artifacts(prepared)
    reuse_retrieve = _should_reuse_resume_payload(prepared, "retrieve") and isinstance(resume_react_payload, dict)
    reuse_workspace = has_workspace_analyst and _should_reuse_resume_payload(prepared, "workspace_analysis") and isinstance(resume_workspace_snapshot, dict)

    if has_workspace_analyst:
        await prepared.run_tracker.record_handoff(
            from_agent="planner",
            to_agent="workspace_analyst",
            reason="workspace_context_requested",
            payload={"task_key": "workspace_analysis"},
            task_key="plan",
        )

    retrieve_call = None
    workspace_call = None

    if reuse_retrieve:
        react_payload = dict(resume_react_payload or {})
        await prepared.run_svc.add_artifact(
            prepared.run_id,
            artifact_type="resume_reuse",
            title="Reused React Payload",
            content={"task_key": "retrieve", "resume_from": prepared.resume_from_task_key},
            owner_agent="retriever",
            task_key="retrieve",
        )
        await prepared.run_svc.upsert_task(
            prepared.run_id,
            "retrieve",
            title="Retrieve Evidence",
            status="completed",
            owner_agent="retriever",
            metadata={"resumed": True},
        )
    else:
        async def _run_retrieve() -> Dict[str, Any]:
            call = _build_react_call(
                prepared,
                status_callback=status_callback,
                token_callback=token_callback,
                sources_callback=sources_callback,
                sources_recorded_ref=sources_recorded_ref,
            )
            payload = await call
            await prepared.run_svc.add_artifact(
                prepared.run_id,
                artifact_type="react_payload_snapshot",
                title="React Payload Snapshot",
                content=payload,
                owner_agent="retriever",
                task_key="retrieve",
            )
            return payload

        retrieve_call = _execute_with_retries(
            prepared,
            task_key="retrieve",
            title="Retrieve Evidence",
            owner_agent="retriever",
            factory=_run_retrieve,
        )

    if has_workspace_analyst:
        if reuse_workspace:
            workspace_snapshot = dict(resume_workspace_snapshot or {})
            await prepared.run_svc.add_artifact(
                prepared.run_id,
                artifact_type="resume_reuse",
                title="Reused Workspace Snapshot",
                content={"task_key": "workspace_analysis", "resume_from": prepared.resume_from_task_key},
                owner_agent="workspace_analyst",
                task_key="workspace_analysis",
            )
            await prepared.run_svc.upsert_task(
                prepared.run_id,
                "workspace_analysis",
                title="Analyze Workspace",
                status="completed",
                owner_agent="workspace_analyst",
                metadata={"resumed": True},
            )
        else:
            async def _run_workspace() -> Dict[str, Any]:
                snapshot = await prepared.backends.workspace.collect_snapshot(
                    prepared,
                    workspace_path=workspace_path,
                    path_filter=None,
                )
                await prepared.run_svc.add_artifact(
                    prepared.run_id,
                    artifact_type="workspace_snapshot",
                    title="Workspace Snapshot",
                    content=snapshot,
                    owner_agent="workspace_analyst",
                    task_key="workspace_analysis",
                    metadata={"changed_file_count": snapshot.get("changed_file_count")},
                )
                return snapshot

            workspace_call = _execute_with_retries(
                prepared,
                task_key="workspace_analysis",
                title="Analyze Workspace",
                owner_agent="workspace_analyst",
                factory=_run_workspace,
            )

    if retrieve_call is not None or workspace_call is not None:
        await _record_task_step(
            prepared,
            task_key="answer",
            title="Barrier Wait",
            owner_agent="presenter",
            kind="barrier",
            status="running",
            metadata={"parallel_group": ["retrieve", "workspace_analysis"] if has_workspace_analyst else ["retrieve"]},
        )
        if retrieve_call is not None and workspace_call is not None:
            react_payload, workspace_snapshot = await asyncio.gather(retrieve_call, workspace_call)
        elif retrieve_call is not None:
            react_payload = await retrieve_call
        elif workspace_call is not None:
            workspace_snapshot = await workspace_call
        await _record_task_step(
            prepared,
            task_key="answer",
            title="Barrier Wait",
            owner_agent="presenter",
            kind="barrier",
            status="completed",
            metadata={"parallel_group": ["retrieve", "workspace_analysis"] if has_workspace_analyst else ["retrieve"]},
        )

    await _raise_if_cancel_requested(prepared, stage="retrieve")

    if workspace_snapshot:
        await prepared.run_tracker.record_handoff(
            from_agent="workspace_analyst",
            to_agent="presenter",
            reason="workspace_snapshot_ready",
            payload={"changed_file_count": workspace_snapshot.get("changed_file_count")},
            task_key="workspace_analysis",
        )

    if react_payload is None:
        raise_http_error(500, "MISSING_REACT_PAYLOAD", "React payload was not produced by orchestration.", run_id=prepared.run_id)

    return react_payload, bool(sources_recorded_ref["value"]), workspace_snapshot


async def finalize_react_payload(
    prepared: PreparedChatExecution,
    react_payload: Dict[str, Any],
    *,
    sources_recorded: bool,
    workspace_snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    await _raise_if_cancel_requested(prepared, stage="answer")
    answer = str(react_payload.get("answer") or "").strip()
    results = list(react_payload.get("results", []) or [])
    sources = list(react_payload.get("sources", []) or [])
    query_ms = float(react_payload.get("query_time_ms", 0.0) or 0.0)
    react_meta = dict(react_payload.get("react", {}) or {})
    routing_profile = dict(react_payload.get("routing_profile", {}) or react_meta.get("profile", {}) or {})
    reasoning_payload = dict(react_payload.get("reasoning", {}) or {})
    reasoning_summary = dict(reasoning_payload.get("summary", {}) or {})
    reasoning_trace = list(reasoning_payload.get("trace", []) or [])
    reasoning_narrative = list(reasoning_payload.get("narrative", []) or [])
    local_overlay = extract_local_workspace_overlay(prepared.req)
    local_overlay_evidence = build_local_overlay_evidence(local_overlay)
    workspace_graph = extract_workspace_graph(local_overlay)
    grounded_overlay_paths = collect_grounded_overlay_paths(local_overlay)
    normalized_question_contract = normalize_question_contract(
        dict(prepared.intent_resolution.get("question_contract") or {}),
        response_type=prepared.resolved.response_type,
        message=prepared.clean_message,
        task_type=getattr(prepared.req, "task_type", ""),
        tool_scope=list(getattr(prepared.req, "tool_scope", []) or []),
        workspace_overlay_present=bool(local_overlay.get("present")),
    )
    workspace_grounding_report = build_workspace_grounding_report(
        workspace_graph,
        grounded_overlay_paths,
    )
    layer_manifest = build_layer_manifest(
        response_type=prepared.resolved.response_type,
        routing_profile=routing_profile,
        results=results,
        sources=sources,
        local_overlay=local_overlay,
    )

    if _should_render_workspace_graph_answer(
        question_contract=normalized_question_contract,
        workspace_graph=workspace_graph,
        grounded_overlay_paths=grounded_overlay_paths,
    ):
        rendered_answer = render_workspace_graph_answer(
            prepared.clean_message,
            workspace_graph,
            grounded_paths=grounded_overlay_paths,
            local_overlay=local_overlay,
        )
        if rendered_answer:
            answer = rendered_answer
    elif _should_force_overlay_review_answer(
        question_contract=normalized_question_contract,
        local_overlay=local_overlay,
        results=results,
        sources=sources,
        answer=answer,
    ):
        rendered_answer = _render_overlay_review_answer(prepared.clean_message, local_overlay)
        if rendered_answer:
            answer = rendered_answer

    evidence_gate = build_evidence_gate(results, sources)
    if not bool(evidence_gate.get("passed")):
        answer, rejection = apply_evidence_policy(answer, evidence_gate)
        if rejection:
            await record_prepared_error(
                prepared,
                status_code=int(rejection["status_code"]),
                code=rejection["code"],
                message=rejection["message"],
                stage="verify",
                evidence_gate=evidence_gate,
            )

    if not answer:
        await record_prepared_error(
            prepared,
            status_code=422,
            code="INSUFFICIENT_ANSWER_QUALITY",
            message=str(react_payload.get("error") or "Failed to generate an evidence-grounded answer. Narrow the question and try again."),
            stage="answer",
        )

    answer, guard_meta = enforce_source_whitelist(
        answer,
        sources,
        results,
        prepared.trace_id,
        extra_allowed_paths=grounded_overlay_paths,
    )
    if not bool(guard_meta.get("passed", True)):
        await record_prepared_error(
            prepared,
            status_code=422,
            code="UNGROUNDED_SOURCE_MENTIONS",
            message=(
                "The final answer referenced source paths that were not grounded in retrieved evidence: "
                + ", ".join(str(item) for item in list(guard_meta.get("ungrounded_examples") or [])[:5])
            ).strip(),
            stage="answer",
            source_guard=guard_meta,
        )
    if not answer:
        await record_prepared_error(
            prepared,
            status_code=422,
            code="INSUFFICIENT_GROUNDED_ANSWER",
            message=str(react_payload.get("error") or "The answer is empty after validation. Narrow the question and try again."),
            stage="answer",
        )
    truncated = bool(react_payload.get("answer_truncated"))

    conv_id = await prepared.conv_svc.append_message(prepared.req.conversation_id, prepared.req.model, "user", prepared.clean_message)
    await prepared.conv_svc.append_message(conv_id, prepared.req.model, "assistant", answer, sources=sources)

    if sources and not sources_recorded:
        await prepared.run_tracker.record_sources(sources)

    await prepared.run_tracker.record_handoff(
        from_agent="retriever",
        to_agent="presenter",
        reason="evidence_ready",
        payload={"source_count": len(sources)},
        task_key="retrieve",
    )

    routing_artifact = await prepared.run_svc.add_artifact(
        prepared.run_id,
        artifact_type="routing",
        title="Routing Metadata",
        content=build_react_routing_payload(react_meta, routing_profile),
        owner_agent=prepared.resolved.agent_id,
        metadata={"trace_id": prepared.trace_id},
    )
    reasoning_artifact = await prepared.run_svc.add_artifact(
        prepared.run_id,
        artifact_type="reasoning_summary",
        title="Reasoning Summary",
        content={
            "summary": reasoning_summary,
            "trace": reasoning_trace,
            "narrative": reasoning_narrative,
        },
        owner_agent=prepared.resolved.agent_id,
        task_key="answer",
        metadata={"trace_id": prepared.trace_id},
    )
    sources_artifact = await prepared.run_svc.get_latest_artifact(prepared.run_id, "sources")
    workspace_artifact = await prepared.run_svc.get_latest_artifact(prepared.run_id, "workspace_snapshot")

    evidence_artifact = await prepared.run_svc.add_artifact(
        prepared.run_id,
        artifact_type="evidence_gate",
        title="Evidence Gate",
        content=evidence_gate,
        owner_agent="reviewer",
        task_key="verify",
        metadata={"trace_id": prepared.trace_id},
    )
    context_pack = build_context_pack(
        results=results,
        sources=sources,
        response_type=prepared.resolved.response_type,
        execution_plan=prepared.execution_plan,
        workspace_snapshot=workspace_snapshot,
        local_overlay={
            "present": local_overlay.get("present"),
            "workspace_path": local_overlay.get("workspace_path"),
            "selected_file_path": local_overlay.get("selected_file_path"),
            "summary": local_overlay.get("local_summary"),
            "error": local_overlay.get("local_error"),
            "workspace_graph": workspace_graph,
            "grounding_report": workspace_grounding_report,
            "evidence": local_overlay_evidence,
        },
        layer_manifest=layer_manifest,
    )
    context_pack_artifact = await prepared.run_svc.add_artifact(
        prepared.run_id,
        artifact_type="context_pack",
        title="Context Pack",
        content=context_pack,
        owner_agent="retriever",
        task_key="retrieve",
        metadata={
            "lineage": {
                "routing_artifact_id": (routing_artifact or {}).get("artifact_id"),
                "sources_artifact_id": (sources_artifact or {}).get("artifact_id"),
                "workspace_artifact_id": (workspace_artifact or {}).get("artifact_id"),
            }
        },
    )
    provenance_report = build_provenance_report(answer, results, sources)
    provenance_artifact = await prepared.run_svc.add_artifact(
        prepared.run_id,
        artifact_type="provenance_report",
        title="Provenance Report",
        content=provenance_report,
        owner_agent="reviewer",
        task_key="verify",
        metadata={"context_pack_artifact_id": (context_pack_artifact or {}).get("artifact_id")},
    )
    unsupported_claims = detect_unsupported_claims(answer, results)
    unsupported_artifact = await prepared.run_svc.add_artifact(
        prepared.run_id,
        artifact_type="unsupported_claims",
        title="Unsupported Claims Report",
        content=unsupported_claims,
        owner_agent="reviewer",
        task_key="verify",
        metadata={
            "evidence_gate_artifact_id": (evidence_artifact or {}).get("artifact_id"),
            "provenance_artifact_id": (provenance_artifact or {}).get("artifact_id"),
        },
    )
    await prepared.run_tracker.record_answer(
        answer,
        source_count=len(sources),
        answer_truncated=truncated,
        trace_id=prepared.trace_id,
        unsupported_count=unsupported_claims.get("unsupported_count"),
    )
    await prepared.run_tracker.record_handoff(
        from_agent="presenter",
        to_agent="reviewer",
        reason="answer_ready",
        payload={"artifact_type": "answer", "unsupported_claims_artifact_id": (unsupported_artifact or {}).get("artifact_id")},
        task_key="answer",
    )
    await prepared.run_tracker.complete(conversation_id=conv_id)

    payload = {
        "answer": answer,
        "sources": sources,
        "response_type": prepared.resolved.response_type,
        "classified_intent": "react",
        "intent_source": prepared.intent_resolution.get("source"),
        "intent_id": prepared.intent_resolution.get("intent"),
        "intent_confidence": prepared.intent_resolution.get("confidence"),
        "conversation_id": conv_id,
        "query_time_ms": query_ms,
        "trace_id": prepared.trace_id,
        "run_id": prepared.run_id,
        "answer_truncated": truncated,
        "planned_response_type": prepared.intent_resolution.get("response_type"),
        "retrieval_bias": prepared.intent_resolution.get("retrieval_bias"),
        "answer_style": prepared.intent_resolution.get("answer_style"),
        "planning": prepared.execution_plan,
        "routing": build_react_routing_payload(react_meta, routing_profile),
        "layer_manifest": layer_manifest,
        "local_overlay": {
            "present": local_overlay.get("present"),
            "workspace_path": local_overlay.get("workspace_path"),
            "selected_file_path": local_overlay.get("selected_file_path"),
            "summary": local_overlay.get("local_summary"),
            "error": local_overlay.get("local_error"),
            "workspace_graph": workspace_graph,
            "grounding_report": workspace_grounding_report,
            "evidence": local_overlay_evidence,
        },
        "reasoning_summary": reasoning_summary,
        "reasoning_trace": reasoning_trace,
        "reasoning_narrative": reasoning_narrative,
        "source_guard": guard_meta,
        "evidence_gate": evidence_gate,
        "context_pack": context_pack,
        "provenance": provenance_report,
        "unsupported_claims": unsupported_claims,
        "workspace_snapshot": workspace_snapshot or {},
        "reasoning_artifact_id": (reasoning_artifact or {}).get("artifact_id"),
    }

    logger.info(
        "Chat execution completed",
        extra={
            "trace_id": prepared.trace_id,
            "conversation_id": conv_id,
            "classified_intent": "react",
            "intent_source": prepared.intent_resolution.get("source"),
            "intent_id": prepared.intent_resolution.get("intent"),
            "intent_confidence": prepared.intent_resolution.get("confidence"),
            "planned_response_type": prepared.intent_resolution.get("response_type"),
            "retrieval_bias": prepared.intent_resolution.get("retrieval_bias"),
            "answer_style": prepared.intent_resolution.get("answer_style"),
            "response_type": prepared.resolved.response_type,
            "answer_truncated": truncated,
            "source_count": len(sources),
            "source_guard": guard_meta,
            "evidence_gate": evidence_gate,
            "react_rounds": react_meta.get("rounds"),
            "reasoning_summary": reasoning_summary,
        },
    )
    return payload

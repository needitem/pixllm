import asyncio
import logging
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, List
from uuid import uuid4

from fastapi import HTTPException

from ... import config
from ...schemas.chat import ChatRequest, IntentVerifyRequest
from ...services.conversations.service import ConversationsService
from ...services.execution.runs import ExecutionRunTracker, ExecutionRunsService
from .backends import build_default_chat_backends
from .http import intent_failure_to_api_error, raise_http_error
from .intent import classify_intent_hybrid
from .planning import build_execution_plan
from .runtime_profile import resolve_runtime_routing_profile
from .text import sanitize_user_message


logger = logging.getLogger(__name__)


def _attachment_field(item: Any, key: str) -> Any:
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def _has_local_workspace_overlay(request: Any) -> bool:
    attachments = list(getattr(request, "attachments", []) or [])
    for item in attachments:
        kind = str(_attachment_field(item, "kind") or "").strip().lower()
        if kind == "local_workspace_overlay":
            return True
    return False


def _extract_overlay_user_question(request: Any) -> str:
    attachments = list(getattr(request, "attachments", []) or [])
    for item in attachments:
        kind = str(_attachment_field(item, "kind") or "").strip().lower()
        if kind != "local_workspace_overlay":
            continue
        metadata = _attachment_field(item, "metadata") or {}
        if isinstance(metadata, dict):
            question = str(metadata.get("question") or "").strip()
            if question:
                return question
    return ""


@dataclass
class PreparedChatExecution:
    trace_id: str
    req: ChatRequest
    clean_message: str
    resolved: Any
    session_id: str
    conv_svc: ConversationsService
    history_messages: List[Dict[str, Any]]
    max_tokens: int
    temperature: float
    intent_resolution: Dict[str, Any]
    execution_plan: Dict[str, Any]
    run_id: str
    run_tracker: ExecutionRunTracker
    run_svc: ExecutionRunsService
    backends: Any = None
    resume_run_id: str = ""
    resume_from_task_key: str = ""
    resume_from_step_key: str = ""


def apply_runtime_overrides(req: ChatRequest, resolved_intent) -> None:
    overrides = resolved_intent.runtime_overrides or {}
    for key in ("top_k", "use_reranker", "evidence_mode"):
        if key in overrides and hasattr(req, key):
            setattr(req, key, overrides[key])
    if "primary_collection" in overrides and overrides["primary_collection"]:
        req.collection = overrides["primary_collection"]


async def record_prepared_error(
    prepared: PreparedChatExecution,
    *,
    status_code: int,
    code: str,
    message: str,
    stage: str,
    **extra: Any,
) -> None:
    await prepared.run_tracker.record_error(code, message, stage=stage)
    raise_http_error(status_code, code, message, run_id=prepared.run_id, **extra)


async def verify_chat_intent_request(payload: IntentVerifyRequest, chat_deps: Any) -> Dict[str, Any]:
    raw_message = _extract_overlay_user_question(payload) or payload.message
    clean_message = sanitize_user_message(raw_message)
    if not clean_message:
        raise_http_error(400, "BAD_REQUEST", "message is required")

    orchestration_policy = chat_deps.orchestrator
    if orchestration_policy is None:
        raise_http_error(503, "SERVICE_UNAVAILABLE", "orchestration policy unavailable")

    model_name = str(payload.model or config.VLLM_MODEL).strip() or config.VLLM_MODEL
    try:
        loop = asyncio.get_running_loop()
        intent_resolution = await loop.run_in_executor(
            None,
            lambda: classify_intent_hybrid(
                policy=orchestration_policy,
                message=clean_message,
                model_name=model_name,
                llm_client=chat_deps.vllm_client,
                task_type=getattr(payload, "task_type", ""),
                tool_scope=list(getattr(payload, "tool_scope", []) or []),
                approval_mode=getattr(payload, "approval_mode", ""),
                workspace_overlay_present=_has_local_workspace_overlay(payload),
            ),
        )
        intent_error = intent_failure_to_api_error(intent_resolution)
        if intent_error:
            raise_http_error(
                int(intent_error["status_code"]),
                intent_error["code"],
                intent_error["message"],
                failure_reason=intent_error["failure_reason"],
            )

        resolved = orchestration_policy.resolve_intent_by_id(intent_resolution.get("intent", "general"))
        planned_response_type = str(intent_resolution.get("response_type") or "").strip()
        if planned_response_type and planned_response_type != str(resolved.response_type or "").strip():
            resolved = orchestration_policy.resolve_intent_by_response_type(planned_response_type)
        routing_profile = resolve_runtime_routing_profile(
            response_type=resolved.response_type,
            intent_source=intent_resolution.get("source", ""),
            intent_confidence=float(intent_resolution.get("confidence", 0.0) or 0.0),
            retrieval_bias=str(intent_resolution.get("retrieval_bias") or ""),
            answer_style=str(intent_resolution.get("answer_style") or ""),
            workspace_overlay_present=_has_local_workspace_overlay(payload),
        )
        execution_plan = build_execution_plan(
            payload,
            response_type=resolved.response_type,
            intent_resolution=intent_resolution,
            resolved=resolved,
        )

        return {
            "message": clean_message,
            "intent_id": intent_resolution.get("intent"),
            "intent_source": intent_resolution.get("source"),
            "intent_confidence": intent_resolution.get("confidence"),
            "planned_response_type": intent_resolution.get("response_type"),
            "retrieval_bias": intent_resolution.get("retrieval_bias"),
            "answer_style": intent_resolution.get("answer_style"),
            "response_type": resolved.response_type,
            "resolved_intent_id": resolved.intent_id,
            "agent_id": resolved.agent_id,
            "skill_ids": resolved.skill_ids,
            "runtime_overrides": resolved.runtime_overrides or {},
            "planning": execution_plan,
            "routing": {"profile": routing_profile},
            "debug": {
                "used_llm": intent_resolution.get("used_llm"),
                "llm_error": intent_resolution.get("llm_error"),
                "llm_raw": intent_resolution.get("llm_raw"),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Chat intent verification failed")
        raise_http_error(503, "INTENT_CLASSIFIER_UNAVAILABLE", str(exc))


async def prepare_chat_execution(request: ChatRequest, chat_deps: Any) -> PreparedChatExecution:
    trace_id = f"chat-{uuid4().hex[:12]}"
    raw_message = _extract_overlay_user_question(request) or request.message
    clean_message = sanitize_user_message(raw_message)
    if not clean_message:
        raise_http_error(400, "BAD_REQUEST", "message is required")

    req = request
    req.message = clean_message
    session_id = str(getattr(req, "conversation_id", "") or "").strip() or f"chat-{uuid4().hex[:10]}"

    run_svc = ExecutionRunsService(chat_deps.redis)
    resume_run_id = str(getattr(req, "resume_run_id", "") or "").strip()
    resume_from_task_key = str(getattr(req, "resume_from_task_key", "") or "").strip()
    resume_from_step_key = str(getattr(req, "resume_from_step_key", "") or "").strip()
    if resume_run_id:
        existing_run = await run_svc.get(resume_run_id)
        if not existing_run:
            raise_http_error(404, "RUN_NOT_FOUND", "resume_run_id does not match an existing run")
        await run_svc.resume_run(
            resume_run_id,
            from_task_key=resume_from_task_key,
            from_step_key=resume_from_step_key,
        )
        run = await run_svc.get(resume_run_id)
        session_id = str((run or {}).get("session_id") or session_id)
    else:
        run = await run_svc.create_run(
            session_id=session_id,
            conversation_id=request.conversation_id,
            model=req.model or config.VLLM_MODEL,
            user_message=clean_message,
            owner_agent="planner",
            metadata={
                "trace_id": trace_id,
                "top_k": getattr(req, "top_k", None),
                "request_snapshot": request.model_dump(),
            },
        )
    tracker = ExecutionRunTracker(run_svc, run["run_id"], primary_agent="planner")
    await tracker.record_phase("accepted", "Request accepted")
    await tracker.record_phase("prepare", "Preparing request")

    logger.info(
        "Chat execution started",
        extra={
            "trace_id": trace_id,
            "conversation_id": request.conversation_id,
            "top_k": getattr(req, "top_k", None),
        },
    )

    conv_svc = ConversationsService(chat_deps.redis)
    history_messages: List[Dict[str, Any]] = []
    if request.conversation_id:
        existing = await conv_svc.get(request.conversation_id)
        if existing:
            history_messages = existing.get("messages", [])

    try:
        orchestration_policy = chat_deps.orchestrator
        if orchestration_policy is None:
            await tracker.record_error("SERVICE_UNAVAILABLE", "orchestration policy unavailable", stage="prepare")
            raise_http_error(503, "SERVICE_UNAVAILABLE", "orchestration policy unavailable", run_id=run["run_id"])

        loop = asyncio.get_running_loop()
        intent_resolution = await loop.run_in_executor(
            None,
            lambda: classify_intent_hybrid(
                policy=orchestration_policy,
                message=clean_message,
                model_name=req.model or config.VLLM_MODEL,
                llm_client=chat_deps.vllm_client,
                task_type=getattr(req, "task_type", ""),
                tool_scope=list(getattr(req, "tool_scope", []) or []),
                approval_mode=getattr(req, "approval_mode", ""),
                workspace_overlay_present=_has_local_workspace_overlay(req),
            ),
        )
        intent_error = intent_failure_to_api_error(intent_resolution)
        if intent_error:
            await tracker.record_error(intent_error["code"], intent_error["message"], stage="prepare")
            raise_http_error(
                int(intent_error["status_code"]),
                intent_error["code"],
                intent_error["message"],
                failure_reason=intent_error["failure_reason"],
                run_id=run["run_id"],
            )

        resolved = orchestration_policy.resolve_intent_by_id(intent_resolution.get("intent", "general"))
        planned_response_type = str(intent_resolution.get("response_type") or "").strip()
        if planned_response_type and planned_response_type != str(resolved.response_type or "").strip():
            resolved = orchestration_policy.resolve_intent_by_response_type(planned_response_type)
        apply_runtime_overrides(req, resolved)
        execution_plan = build_execution_plan(req, response_type=resolved.response_type, intent_resolution=intent_resolution, resolved=resolved)
        workspace_overlay_present = _has_local_workspace_overlay(req)

        max_tokens = int(resolved.runtime_overrides.get("max_tokens", 1800))
        temperature = float(resolved.runtime_overrides.get("temperature", 0.2))
        tracker.set_primary_agent(resolved.agent_id or "build")
        await run_svc.update_run(
            run["run_id"],
            response_type=resolved.response_type,
            owner_agent=resolved.agent_id,
            workspace_id=getattr(req, "workspace_id", None),
            task_type=getattr(req, "task_type", None),
            goal=getattr(req, "goal", None),
            approval_mode=getattr(req, "approval_mode", None),
            tool_scope=list(getattr(req, "tool_scope", []) or []),
            budget=(req.budget.model_dump() if getattr(req, "budget", None) is not None else None),
            task_family=execution_plan.get("task_family"),
            risk_class=execution_plan.get("risk_class"),
            needs_approval=execution_plan.get("needs_approval"),
            required_agents=execution_plan.get("required_agents"),
            expected_artifacts=execution_plan.get("expected_artifacts"),
            corpus_profile=execution_plan.get("corpus_profile"),
            metadata={
                "trace_id": trace_id,
                "intent_id": intent_resolution.get("intent"),
                "intent_source": intent_resolution.get("source"),
                "intent_confidence": intent_resolution.get("confidence"),
                "retrieval_bias": intent_resolution.get("retrieval_bias"),
                "answer_style": intent_resolution.get("answer_style"),
                "planned_response_type": intent_resolution.get("response_type"),
                "workspace_binding": execution_plan.get("workspace_binding"),
                "requested": execution_plan.get("requested"),
                "client_metadata": dict(getattr(req, "client_metadata", {}) or {}),
                "request_snapshot": request.model_dump(),
                "resume_from_task_key": resume_from_task_key or None,
                "resume_from_step_key": resume_from_step_key or None,
                "workspace_overlay_present": workspace_overlay_present,
            },
        )
        await tracker.record_execution_plan(execution_plan)
        await tracker.record_phase(
            "plan",
            "Execution plan prepared",
            response_type=resolved.response_type,
            planned_response_type=intent_resolution.get("response_type"),
            retrieval_bias=intent_resolution.get("retrieval_bias"),
            answer_style=intent_resolution.get("answer_style"),
            task_family=execution_plan.get("task_family"),
            risk_class=execution_plan.get("risk_class"),
            needs_approval=execution_plan.get("needs_approval"),
            corpus_profile=execution_plan.get("corpus_profile"),
            workspace_overlay_present=workspace_overlay_present,
        )

        return PreparedChatExecution(
            trace_id=trace_id,
            req=req,
            clean_message=clean_message,
            resolved=resolved,
            session_id=session_id,
            conv_svc=conv_svc,
            history_messages=history_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            intent_resolution=intent_resolution,
            execution_plan=execution_plan,
            run_id=run["run_id"],
            run_tracker=tracker,
            run_svc=run_svc,
            backends=build_default_chat_backends(chat_deps),
            resume_run_id=resume_run_id,
            resume_from_task_key=resume_from_task_key,
            resume_from_step_key=resume_from_step_key,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Chat preparation failed", extra={"trace_id": trace_id})
        await tracker.record_error("LLM_UNAVAILABLE", str(exc), stage="prepare")
        raise_http_error(503, "LLM_UNAVAILABLE", str(exc), run_id=run["run_id"])

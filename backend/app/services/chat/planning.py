from typing import Any, Dict, List

from .agents import build_handoff_plan, resolve_agent_specs


_LOW_RISK_RESPONSE_TYPES = {
    "general",
    "doc_lookup",
    "api_lookup",
    "code_explain",
}
_MEDIUM_RISK_RESPONSE_TYPES = {
    "troubleshooting",
    "code_review",
    "compare",
    "design_review",
}
_HIGH_RISK_RESPONSE_TYPES = {
    "code_generate",
    "bug_fix",
    "refactor",
    "migration",
}


def _normalize_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _normalize_str(value: Any) -> str:
    return str(value or "").strip()


def _has_local_workspace_overlay_attachment(request: Any) -> bool:
    attachments = list(getattr(request, "attachments", []) or [])
    for item in attachments:
        if isinstance(item, dict):
            kind = _normalize_str(item.get("kind", "")).lower()
        else:
            kind = _normalize_str(getattr(item, "kind", "")).lower()
        if kind == "local_workspace_overlay":
            return True
    return False


def infer_task_family(*, response_type: str, task_type: str = "") -> str:
    explicit = _normalize_str(task_type).lower()
    if explicit:
        return explicit

    rt = _normalize_str(response_type).lower()
    if rt in {"doc_lookup", "api_lookup"}:
        return "knowledge"
    if rt in {"code_explain", "compare", "design_review"}:
        return "analysis"
    if rt in {"code_review"}:
        return "review"
    if rt in {"bug_fix", "troubleshooting"}:
        return "repair"
    if rt in {"code_generate", "refactor", "migration"}:
        return "change"
    return "general"


def infer_risk_class(
    *,
    response_type: str,
    approval_mode: str = "",
    tool_scope: List[str] | None = None,
) -> str:
    approval = _normalize_str(approval_mode).lower()
    scope = {item.lower() for item in _normalize_list(tool_scope)}
    rt = _normalize_str(response_type).lower()

    if approval == "always":
        return "high"
    if {"write", "execute", "build", "svn"} & scope:
        return "high" if rt in _HIGH_RISK_RESPONSE_TYPES else "medium"
    if rt in _HIGH_RISK_RESPONSE_TYPES:
        return "high"
    if rt in _MEDIUM_RISK_RESPONSE_TYPES:
        return "medium"
    return "low"


def infer_needs_approval(*, approval_mode: str = "", risk_class: str = "") -> bool:
    approval = _normalize_str(approval_mode).lower()
    if approval in {"always", "required"}:
        return True
    if approval in {"never", "disabled"}:
        return False
    return _normalize_str(risk_class).lower() == "high"


def infer_required_agents(*, response_type: str, risk_class: str) -> List[str]:
    rt = _normalize_str(response_type).lower()
    agents = ["planner", "retriever", "presenter"]

    if rt in {"code_generate", "bug_fix", "refactor", "migration"}:
        agents.append("executor")
    if rt in {"bug_fix", "troubleshooting", "code_generate", "refactor", "migration", "code_review", "design_review"}:
        agents.append("reviewer")
    if rt in {"bug_fix", "code_generate", "refactor", "migration"}:
        agents.append("tester")
    if _normalize_str(risk_class).lower() == "high" and "reviewer" not in agents:
        agents.append("reviewer")

    seen = set()
    ordered: List[str] = []
    for agent in agents:
        if agent in seen:
            continue
        seen.add(agent)
        ordered.append(agent)
    return ordered


def infer_workspace_agent_needed(request: Any, *, response_type: str) -> bool:
    rt = _normalize_str(response_type).lower()
    workspace_id = _normalize_str(getattr(request, "workspace_id", ""))
    module_filter = _normalize_str(getattr(request, "module_filter", ""))
    attachments = list(getattr(request, "attachments", []) or [])
    if rt not in {"code_explain", "code_review", "bug_fix", "troubleshooting", "code_generate", "refactor", "migration"}:
        return False
    if _has_local_workspace_overlay_attachment(request):
        return False
    return bool(workspace_id or module_filter or attachments)


def infer_expected_artifacts(*, response_type: str, needs_approval: bool) -> List[str]:
    rt = _normalize_str(response_type).lower()
    artifacts = ["execution_plan", "routing_metadata", "source_bundle", "final_answer"]

    if rt == "code_review":
        artifacts.append("findings_report")
    if rt in {"bug_fix", "troubleshooting"}:
        artifacts.extend(["failure_analysis", "verification_plan"])
    if rt in {"code_generate", "refactor", "migration"}:
        artifacts.extend(["change_plan", "draft_patch"])
    if needs_approval:
        artifacts.append("approval_request")

    seen = set()
    ordered: List[str] = []
    for artifact in artifacts:
        if artifact in seen:
            continue
        seen.add(artifact)
        ordered.append(artifact)
    return ordered


def infer_corpus_profile(request: Any, *, response_type: str) -> str:
    workspace_id = _normalize_str(getattr(request, "workspace_id", ""))
    attachments = list(getattr(request, "attachments", []) or [])
    rt = _normalize_str(response_type).lower()

    if rt == "doc_lookup":
        return "docs_with_server_code_reference"
    if workspace_id or attachments:
        return "local_workspace_primary_with_engine_reference"
    return "server_code_first"


def build_planned_tasks(*, required_agents: List[str]) -> List[Dict[str, Any]]:
    default_owner = required_agents[0] if required_agents else "planner"
    tasks = [
        {"task_key": "accepted", "title": "Accepted", "owner_agent": "system", "depends_on": [], "status": "pending", "execution_mode": "sequential"},
        {"task_key": "prepare", "title": "Prepare Request", "owner_agent": "planner", "depends_on": ["accepted"], "status": "pending", "execution_mode": "sequential"},
        {"task_key": "plan", "title": "Plan Execution", "owner_agent": default_owner, "depends_on": ["prepare"], "status": "pending", "execution_mode": "sequential"},
        {"task_key": "retrieve", "title": "Retrieve Evidence", "owner_agent": "retriever", "depends_on": ["plan"], "status": "pending", "execution_mode": "parallel"},
    ]
    if "workspace_analyst" in required_agents:
        tasks.append(
            {
                "task_key": "workspace_analysis",
                "title": "Analyze Workspace",
                "owner_agent": "workspace_analyst",
                "depends_on": ["plan"],
                "status": "pending",
                "execution_mode": "parallel",
            }
        )
        answer_deps = ["retrieve", "workspace_analysis"]
    else:
        answer_deps = ["retrieve"]
    tasks.extend([
        {"task_key": "answer", "title": "Generate Answer", "owner_agent": "presenter", "depends_on": answer_deps, "status": "pending", "execution_mode": "barrier"},
        {"task_key": "verify", "title": "Verify Result", "owner_agent": "reviewer" if "reviewer" in required_agents else "presenter", "depends_on": ["answer"], "status": "pending", "execution_mode": "barrier"},
    ])
    return tasks


def build_execution_plan(request: Any, *, response_type: str, intent_resolution: Dict[str, Any], resolved: Any) -> Dict[str, Any]:
    task_family = infer_task_family(
        response_type=response_type,
        task_type=getattr(request, "task_type", ""),
    )
    risk_class = infer_risk_class(
        response_type=response_type,
        approval_mode=getattr(request, "approval_mode", ""),
        tool_scope=list(getattr(request, "tool_scope", []) or []),
    )
    needs_approval = infer_needs_approval(
        approval_mode=getattr(request, "approval_mode", ""),
        risk_class=risk_class,
    )
    required_agents = infer_required_agents(response_type=response_type, risk_class=risk_class)
    if infer_workspace_agent_needed(request, response_type=response_type) and "workspace_analyst" not in required_agents:
        required_agents.insert(2, "workspace_analyst")
    expected_artifacts = infer_expected_artifacts(
        response_type=response_type,
        needs_approval=needs_approval,
    )
    corpus_profile = infer_corpus_profile(request, response_type=response_type)
    agent_specs = resolve_agent_specs(required_agents)
    handoff_plan = build_handoff_plan(required_agents)
    planned_tasks = build_planned_tasks(required_agents=required_agents)

    return {
        "task_family": task_family,
        "risk_class": risk_class,
        "needs_approval": needs_approval,
        "required_agents": required_agents,
        "agent_specs": agent_specs,
        "handoff_plan": handoff_plan,
        "expected_artifacts": expected_artifacts,
        "corpus_profile": corpus_profile,
        "workspace_binding": {
            "workspace_id": _normalize_str(getattr(request, "workspace_id", "")) or None,
            "module_filter": _normalize_str(getattr(request, "module_filter", "")) or None,
        },
        "merge_policy": {
            "authoritative_layer": "local_workspace_overlay" if infer_workspace_agent_needed(request, response_type=response_type) else "server_code_baseline",
            "supplemental_layers": [
                "server_code_baseline",
                "server_docs",
            ],
            "conflict_resolution": (
                "prefer_local_workspace_then_server_engine_then_docs"
                if infer_workspace_agent_needed(request, response_type=response_type)
                else "prefer_server_code_then_local_overlay_then_docs"
            ),
        },
        "requested": {
            "task_type": _normalize_str(getattr(request, "task_type", "")) or None,
            "goal": _normalize_str(getattr(request, "goal", "")) or None,
            "approval_mode": _normalize_str(getattr(request, "approval_mode", "")) or "manual",
            "tool_scope": _normalize_list(getattr(request, "tool_scope", [])),
            "attachments_count": len(list(getattr(request, "attachments", []) or [])),
            "budget": getattr(getattr(request, "budget", None), "model_dump", lambda **_: getattr(request, "budget", None))() if getattr(request, "budget", None) is not None else None,
        },
        "resolved": {
            "intent_id": getattr(resolved, "intent_id", "") or intent_resolution.get("intent"),
            "response_type": response_type,
            "agent_id": getattr(resolved, "agent_id", ""),
            "skill_ids": list(getattr(resolved, "skill_ids", []) or []),
            "intent_source": intent_resolution.get("source"),
            "intent_confidence": intent_resolution.get("confidence"),
            "retrieval_bias": intent_resolution.get("retrieval_bias"),
            "answer_style": intent_resolution.get("answer_style"),
        },
        "planned_tasks": planned_tasks,
        "task_graph": {
            "tasks": [task.get("task_key") for task in planned_tasks],
            "edges": [
                {"from": dep, "to": task.get("task_key"), "mode": task.get("execution_mode", "sequential")}
                for task in planned_tasks
                for dep in list(task.get("depends_on") or [])
            ],
                "parallel_groups": [
                    ["retrieve", "workspace_analysis"]
                    if any(task.get("task_key") == "workspace_analysis" for task in planned_tasks)
                    else ["retrieve"]
                ],
                "barriers": [
                    {
                        "task_key": "answer",
                        "depends_on": list(
                            next(
                                (task.get("depends_on") or [])
                                for task in planned_tasks
                                if task.get("task_key") == "answer"
                            )
                        ),
                    }
                ],
            },
        }

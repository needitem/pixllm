from typing import Any, Dict, List


_AGENT_SPECS: Dict[str, Dict[str, Any]] = {
    "planner": {
        "agent_id": "planner",
        "role": "planning",
        "input_contract": ["user_request", "workspace_binding", "risk_class", "tool_scope"],
        "output_contract": ["execution_plan", "required_agents", "expected_artifacts", "handoff_plan"],
        "failure_contract": ["intent_unavailable", "planning_failed"],
        "default_tools": [],
    },
    "retriever": {
        "agent_id": "retriever",
        "role": "evidence_collection",
        "input_contract": ["query", "corpus_profile", "workspace_binding"],
        "output_contract": ["source_bundle", "retrieval_trace", "citations"],
        "failure_contract": ["no_evidence", "retrieval_timeout"],
        "default_tools": ["find_symbol", "grep", "doc_search", "read", "doc_read", "glob"],
    },
    "workspace_analyst": {
        "agent_id": "workspace_analyst",
        "role": "workspace_analysis",
        "input_contract": ["workspace_state", "recent_changes", "symbol_candidates"],
        "output_contract": ["workspace_summary", "changed_files", "diff_summary"],
        "failure_contract": ["workspace_unavailable"],
        "default_tools": ["svn_status", "svn_diff", "find_symbol", "grep"],
    },
    "executor": {
        "agent_id": "executor",
        "role": "change_execution",
        "input_contract": ["execution_plan", "source_bundle", "workspace_state"],
        "output_contract": ["draft_patch", "change_plan", "execution_log"],
        "failure_contract": ["execution_failed", "tool_denied"],
        "default_tools": ["read", "grep", "glob"],
    },
    "reviewer": {
        "agent_id": "reviewer",
        "role": "quality_review",
        "input_contract": ["draft_output", "source_bundle", "execution_trace"],
        "output_contract": ["review_findings", "quality_verdict"],
        "failure_contract": ["review_failed"],
        "default_tools": [],
    },
    "security": {
        "agent_id": "security",
        "role": "security_review",
        "input_contract": ["draft_output", "workspace_state", "tool_scope"],
        "output_contract": ["security_findings", "policy_flags"],
        "failure_contract": ["security_review_failed"],
        "default_tools": [],
    },
    "tester": {
        "agent_id": "tester",
        "role": "verification",
        "input_contract": ["change_plan", "workspace_state", "build_targets"],
        "output_contract": ["verification_plan", "test_results"],
        "failure_contract": ["verification_failed", "build_unavailable"],
        "default_tools": ["pytest", "npm_test", "build"],
    },
    "migration": {
        "agent_id": "migration",
        "role": "migration_planning",
        "input_contract": ["source_version", "target_version", "constraints"],
        "output_contract": ["migration_plan", "compatibility_notes"],
        "failure_contract": ["migration_analysis_failed"],
        "default_tools": [],
    },
    "presenter": {
        "agent_id": "presenter",
        "role": "response_synthesis",
        "input_contract": ["source_bundle", "review_findings", "execution_artifacts"],
        "output_contract": ["final_answer", "report"],
        "failure_contract": ["presentation_failed"],
        "default_tools": [],
    },
    "ops_monitoring": {
        "agent_id": "ops_monitoring",
        "role": "operations_monitoring",
        "input_contract": ["run_state", "system_metrics"],
        "output_contract": ["ops_summary", "alerts"],
        "failure_contract": ["ops_analysis_failed"],
        "default_tools": [],
    },
}


def get_agent_spec(agent_id: str) -> Dict[str, Any]:
    normalized = str(agent_id or "").strip().lower()
    spec = _AGENT_SPECS.get(normalized)
    if spec is None:
        return {
            "agent_id": normalized or "unknown",
            "role": "generic",
            "input_contract": [],
            "output_contract": [],
            "failure_contract": [],
            "default_tools": [],
        }
    return dict(spec)


def resolve_agent_specs(agent_ids: List[str]) -> List[Dict[str, Any]]:
    seen = set()
    specs: List[Dict[str, Any]] = []
    for agent_id in agent_ids or []:
        normalized = str(agent_id or "").strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        specs.append(get_agent_spec(normalized))
    return specs


def build_handoff_plan(agent_ids: List[str]) -> List[Dict[str, Any]]:
    ordered = [spec["agent_id"] for spec in resolve_agent_specs(agent_ids)]
    handoffs: List[Dict[str, Any]] = []
    for current, nxt in zip(ordered, ordered[1:]):
        handoffs.append(
            {
                "from_agent": current,
                "to_agent": nxt,
                "reason": f"{current}_completed",
                "payload_contract": {
                    "from_output": get_agent_spec(current).get("output_contract", []),
                    "to_input": get_agent_spec(nxt).get("input_contract", []),
                },
            }
        )
    return handoffs

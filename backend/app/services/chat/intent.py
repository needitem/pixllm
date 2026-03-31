"""
Minimal routing for chat requests.

This module intentionally avoids a heavyweight intent classifier.
Instead, it resolves:

- a coarse routing bucket
- a response-style hint
- a structured question contract for retrieval coverage

The goal is fail-open, evidence-first behavior.
"""

import logging
import re
from typing import Any, Dict, Iterable, List

from .question_contract import build_overlay_structure_profile, build_question_contract

logger = logging.getLogger(__name__)

_SYMBOL_TOKEN_RE = re.compile(r"\b[A-Z][A-Za-z0-9_]{2,}\b")
_PATH_HINT_RE = re.compile(r"[/\\]|`[^`]+`|\.[A-Za-z0-9]{1,6}\b")
_CODE_FENCE_RE = re.compile(r"```|`[^`]+`")
_MEMBER_ACCESS_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\s*(?:\.|::|->)\s*[A-Za-z_][A-Za-z0-9_]*")
_CALL_LIKE_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\s*\(")

_WRITE_TOOL_SCOPE = {"write", "execute", "build", "svn"}
_DOC_TOOL_SCOPE = {"docs", "doc_search", "doc_read"}
_CHANGE_TASK_TYPES = {
    "change",
    "edit",
    "write",
    "code_generate",
    "bug_fix",
    "refactor",
    "migration",
    "fix",
}
_DOC_TASK_TYPES = {"docs", "doc", "doc_lookup", "document", "reference"}
_READ_TASK_TYPES = {"read", "analysis", "explain", "usage", "compare", "general"}
_REVIEW_TASK_TYPES = {"review", "code_review", "design_review"}
_TROUBLESHOOT_TASK_TYPES = {"bug_fix", "fix", "repair", "troubleshooting", "debug"}
_SPECIALIZED_TASK_RESPONSE_TYPES = {
    "api_lookup": "api_lookup",
    "code_explain": "code_explain",
    "code_generate": "code_generate",
    "code_review": "code_review",
    "compare": "compare",
    "design_review": "design_review",
    "doc_lookup": "doc_lookup",
    "migration": "migration",
    "refactor": "refactor",
    "troubleshooting": "troubleshooting",
}


def _normalize_str(value: Any) -> str:
    return str(value or "").strip()


def _normalize_tokens(values: Iterable[Any] | None) -> set[str]:
    if not values:
        return set()
    return {str(item or "").strip().lower() for item in values if str(item or "").strip()}


def _looks_like_symbol(text: str) -> bool:
    return bool(_SYMBOL_TOKEN_RE.search(text or ""))


def _looks_code_context(text: str) -> bool:
    normalized = str(text or "")
    return (
        _looks_like_symbol(normalized)
        or bool(_PATH_HINT_RE.search(normalized))
        or bool(_CODE_FENCE_RE.search(normalized))
        or bool(_MEMBER_ACCESS_RE.search(normalized))
        or bool(_CALL_LIKE_RE.search(normalized))
    )


def _default_answer_style_for_response_type(response_type: str) -> str:
    rt = _normalize_str(response_type).lower()
    if rt == "doc_lookup":
        return "reference"
    if rt == "compare":
        return "comparison"
    if rt in {"bug_fix", "troubleshooting"}:
        return "troubleshooting"
    return "explanation" if rt in {"code_explain", "code_generate", "refactor", "api_lookup"} else "default"


def _default_answer_style_for_contract(question_contract: Dict[str, Any], response_type: str) -> str:
    contract_hint = _normalize_str(dict(question_contract or {}).get("answer_style_hint")).lower()
    if contract_hint in {"tutorial", "reference", "explanation", "troubleshooting", "comparison"}:
        return contract_hint
    return _default_answer_style_for_response_type(response_type)


def _coarse_bucket_from_signals(
    *,
    task_type: str,
    tool_scope: List[str] | None,
    approval_mode: str,
    workspace_overlay_present: bool = False,
) -> str:
    explicit_task_type = _normalize_str(task_type).lower()
    normalized_scope = _normalize_tokens(tool_scope)
    approval = _normalize_str(approval_mode).lower()

    if explicit_task_type in _DOC_TASK_TYPES:
        return "doc_lookup"
    if explicit_task_type in _CHANGE_TASK_TYPES:
        return "change_code"
    if explicit_task_type in _READ_TASK_TYPES:
        return "read_code"

    if normalized_scope & _WRITE_TOOL_SCOPE:
        return "change_code"
    if normalized_scope & _DOC_TOOL_SCOPE and not (normalized_scope & _WRITE_TOOL_SCOPE):
        return "doc_lookup"
    if approval in {"always", "required"} and normalized_scope & _WRITE_TOOL_SCOPE:
        return "change_code"
    if workspace_overlay_present:
        return "read_code"
    return ""


def _coarse_bucket_from_message(message: str) -> str:
    if _looks_code_context(message):
        return "read_code"
    return "general"


def _explicit_response_type(
    *,
    task_type: str,
    tool_scope: List[str] | None,
    workspace_overlay_present: bool = False,
) -> str:
    explicit_task_type = _normalize_str(task_type).lower()
    normalized_scope = _normalize_tokens(tool_scope)

    if explicit_task_type in _SPECIALIZED_TASK_RESPONSE_TYPES:
        return _SPECIALIZED_TASK_RESPONSE_TYPES[explicit_task_type]
    if explicit_task_type in _REVIEW_TASK_TYPES:
        return "code_review"
    if explicit_task_type in _TROUBLESHOOT_TASK_TYPES:
        return "troubleshooting"
    if explicit_task_type in _DOC_TASK_TYPES:
        return "doc_lookup"
    if explicit_task_type in _CHANGE_TASK_TYPES:
        return "code_generate"
    if explicit_task_type in _READ_TASK_TYPES:
        return "general"

    if normalized_scope & _WRITE_TOOL_SCOPE:
        return "code_generate"
    if normalized_scope & _DOC_TOOL_SCOPE and not (normalized_scope & _WRITE_TOOL_SCOPE):
        return "doc_lookup"
    return ""


def _response_type_for_bucket(
    bucket: str,
    message: str,
    allowed_response_types: List[str],
    *,
    task_type: str = "",
    tool_scope: List[str] | None = None,
    workspace_overlay_present: bool = False,
) -> str:
    explicit = _explicit_response_type(
        task_type=task_type,
        tool_scope=tool_scope,
        workspace_overlay_present=workspace_overlay_present,
    )
    if explicit:
        return explicit if explicit in allowed_response_types else "general"

    if bucket == "doc_lookup":
        candidate = "doc_lookup"
    elif bucket == "change_code":
        candidate = "code_generate"
    else:
        candidate = "general"

    return candidate if candidate in allowed_response_types else "general"


def _response_type_for_contract(question_contract: Dict[str, Any], allowed_response_types: List[str]) -> str:
    contract_kind = _normalize_str(dict(question_contract or {}).get("kind")).lower()
    mapping = {
        "doc_reference": "doc_lookup",
        "code_change": "code_generate",
        "code_review": "code_review",
        "failure_analysis": "troubleshooting",
        "code_compare": "compare",
        "code_flow_explanation": "general",
        "code_read": "general",
        "general": "general",
    }
    candidate = mapping.get(contract_kind, "general")
    return candidate if candidate in allowed_response_types else "general"


def _resolve_intent_for_response_type(policy, response_type: str, allowed_intents: List[str]) -> str:
    resolved = _normalize_str(policy.intent_id_for_response_type(response_type))
    if resolved:
        return resolved
    return response_type if response_type in allowed_intents else "general"


def classify_intent_hybrid(
    *,
    policy,
    message: str,
    model_name: str,
    llm_client=None,
    task_type: str = "",
    tool_scope: List[str] | None = None,
    approval_mode: str = "",
    workspace_overlay_present: bool = False,
    local_workspace_overlay: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Resolve a minimal routing hint for downstream execution.

    `model_name` and `llm_client` remain in the signature for compatibility with
    current call sites, but front routing is deterministic by design.
    """

    _ = model_name
    _ = llm_client
    overlay_profile = build_overlay_structure_profile(local_workspace_overlay)

    allowed_intents = sorted(
        {
            _normalize_str(intent.get("id"))
            for intent in policy.intents
            if _normalize_str(intent.get("id"))
        }
    )
    if "general" not in allowed_intents:
        allowed_intents.append("general")

    allowed_response_types = sorted(
        {
            _normalize_str(intent.get("response_type"))
            for intent in policy.intents
            if _normalize_str(intent.get("response_type"))
        }
    )
    if "general" not in allowed_response_types:
        allowed_response_types.append("general")

    routing_bucket = _coarse_bucket_from_signals(
        task_type=task_type,
        tool_scope=tool_scope,
        approval_mode=approval_mode,
        workspace_overlay_present=workspace_overlay_present or bool(overlay_profile.get("present")),
    ) or _coarse_bucket_from_message(message)

    initial_response_type = _response_type_for_bucket(
        routing_bucket,
        message,
        allowed_response_types,
        task_type=task_type,
        tool_scope=tool_scope,
        workspace_overlay_present=workspace_overlay_present or bool(overlay_profile.get("present")),
    )
    question_contract = build_question_contract(
        message=message,
        task_type=task_type,
        tool_scope=tool_scope,
        workspace_overlay_present=workspace_overlay_present or bool(overlay_profile.get("present")),
        response_type=initial_response_type,
        local_workspace_overlay=local_workspace_overlay,
    )
    response_type = _response_type_for_contract(question_contract, allowed_response_types) or initial_response_type
    intent_id = _resolve_intent_for_response_type(policy, response_type, allowed_intents)
    retrieval_bias = _normalize_str(question_contract.get("retrieval_mode")).lower()
    if retrieval_bias not in {"code", "docs", "hybrid"}:
        retrieval_bias = "docs" if routing_bucket == "doc_lookup" else ("code" if routing_bucket in {"read_code", "change_code"} else "")
    answer_style = _default_answer_style_for_contract(question_contract, response_type)

    logger.debug(
        "Intent resolved by minimal router: bucket=%s response_type=%s intent=%s contract=%s",
        routing_bucket,
        response_type,
        intent_id,
        question_contract.get("kind"),
    )

    return {
        "intent": intent_id,
        "response_type": response_type,
        "retrieval_bias": retrieval_bias,
        "answer_style": answer_style,
        "question_contract": question_contract,
        "source": "heuristic",
        "confidence": 0.0,
        "used_llm": False,
        "llm_error": "",
        "llm_raw": "",
        "routing_bucket": routing_bucket,
    }

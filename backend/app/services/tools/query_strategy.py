import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ... import config
from ..retrieval.mode_policy import default_mode_for_response_type
from .query_terms import compact_token as _compact_text
from .query_terms import extract_query_compacts, extract_query_terms
from .query_terms import split_identifier_parts

_USAGE_MARKUP_BACKING_SUFFIXES: Tuple[str, ...] = ()
_USAGE_TEST_PATH_HINTS = ("/test/", "/tests/", "/spec/", "/specs/", "/__tests__/")
_USAGE_GENERATED_PATH_HINTS = ("/generated/", "/gen/", "/dist/", "/build/")
_CALL_LIKE_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\(")
_MEMBER_CALL_RE = re.compile(r"(?:\.|->)[A-Za-z_][A-Za-z0-9_]*\s*\(")
_MEMBER_ASSIGN_RE = re.compile(r"(?:\.|->)?[A-Za-z_][A-Za-z0-9_]*\s*=")
_DEFINITION_HINT_RE = re.compile(r"\b(?:class|struct|interface|enum|record|namespace|module|typedef|def|function)\b")
_USAGE_CODE_EXTENSIONS = (".cs", ".cpp", ".c", ".h", ".hpp", ".cc", ".hh", ".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".kt")


def clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


_USAGE_CODE_RESPONSE_TYPES = {"api_lookup"}


def route_collect_mode(response_type: str, mode: str) -> str:
    """Resolve the collect mode ('code', 'docs', or 'hybrid') for a given response_type.

    Priority:
    1. Explicit caller override ('docs', 'code', or 'hybrid' in `mode`) wins.
    2. Falls back to the canonical response_type → mode mapping from routing_arbitration.
    """
    requested = str(mode or "auto").strip().lower()
    if requested in {"docs", "code", "hybrid"}:
        return requested
    return default_mode_for_response_type(response_type)


def code_match_key(item: Dict[str, str]) -> str:
    return f"{str(item.get('path') or '').strip()}::{str(item.get('line_range') or '').strip()}"


def merge_code_matches(match_groups: Sequence[Sequence[Dict[str, str]]], max_items: int) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    seen = set()
    capped = clamp_int(max_items, 1, 200)
    for group in match_groups:
        for row in group or []:
            key = code_match_key(row)
            if key in {"::", ""} or key in seen:
                continue
            seen.add(key)
            out.append(row)
            if len(out) >= capped:
                return out
    return out


def _extract_query_terms(query_text: str, limit: int = 8) -> List[str]:
    return extract_query_terms(query_text, limit=limit)


def _query_compacts(query_text: str, limit: int = 12) -> List[str]:
    return extract_query_compacts(query_text, limit=limit)


def normalize_usage_path(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def strip_usage_companion_suffixes(stem: str) -> str:
    normalized = str(stem or "").strip()
    lowered = normalized.lower()
    for suffix in (".generated", ".gen", ".g.i", ".g"):
        if lowered.endswith(suffix):
            normalized = normalized[: -len(suffix)]
            lowered = normalized.lower()
    return normalized


def is_usage_example_path(path: str) -> bool:
    return False


def is_usage_markup_backing_path(path: str) -> bool:
    normalized = normalize_usage_path(path).lower()
    return any(normalized.endswith(suffix) for suffix in _USAGE_MARKUP_BACKING_SUFFIXES)


def is_usage_entrypoint_file(path: str) -> bool:
    return False


def usage_match_evidence(
    item: Dict[str, Any],
    *,
    query_text: str = "",
    preferred_symbol: str = "",
) -> Dict[str, float]:
    path = str(item.get("path") or "")
    match_text = str(item.get("match") or "")
    normalized_path = normalize_usage_path(path).lower()
    path_compact = _compact_text(normalize_usage_path(path))
    text_compact = _compact_text(match_text)
    file_name = Path(normalized_path).name
    query_compacts = _query_compacts(query_text)
    preferred_compacts = _query_compacts(preferred_symbol or "")
    preferred_terms = [term.lower() for term in _extract_query_terms(preferred_symbol or "", limit=4)]

    query_path_overlap = sum(1 for compact in query_compacts if compact in path_compact)
    query_text_overlap = sum(1 for compact in query_compacts if compact in text_compact)
    preferred_symbol_in_path = 1.0 if any(compact in path_compact for compact in preferred_compacts) else 0.0
    preferred_symbol_in_text = 1.0 if any(compact in text_compact for compact in preferred_compacts) else 0.0
    preferred_symbol_invocation = 0.0
    preferred_symbol_new_expression = 0.0
    lowered_text = match_text.lower()
    for term in preferred_terms:
        if f"{term}(" in lowered_text or f".{term}(" in lowered_text or f"->{term}(" in lowered_text:
            preferred_symbol_invocation = 1.0
        if f"new {term}" in lowered_text:
            preferred_symbol_new_expression = 1.0

    return {
        "is_markup_backing_path": 1.0 if is_usage_markup_backing_path(path) else 0.0,
        "is_source_extension": 1.0 if file_name.endswith(_USAGE_CODE_EXTENSIONS) else 0.0,
        "is_test_path": 1.0 if any(token in normalized_path for token in _USAGE_TEST_PATH_HINTS) else 0.0,
        "is_generated_path": 1.0 if any(token in normalized_path for token in _USAGE_GENERATED_PATH_HINTS) else 0.0,
        "query_path_overlap": float(query_path_overlap),
        "query_text_overlap": float(query_text_overlap),
        "preferred_symbol_in_path": preferred_symbol_in_path,
        "preferred_symbol_in_text": preferred_symbol_in_text,
        "preferred_symbol_invocation": preferred_symbol_invocation,
        "preferred_symbol_new_expression": preferred_symbol_new_expression,
        "call_count": float(len(_CALL_LIKE_RE.findall(match_text))),
        "member_call_count": float(len(_MEMBER_CALL_RE.findall(match_text))),
        "assignment_count": float(len(_MEMBER_ASSIGN_RE.findall(match_text))),
        "has_definition_hint": 1.0 if _DEFINITION_HINT_RE.search(lowered_text) else 0.0,
    }


def _usage_match_rank_key(
    item: Dict[str, Any],
    *,
    query_text: str = "",
    preferred_symbol: str = "",
) -> Tuple[int, int, int, int, int, int, int, int, int, int, int]:
    evidence = usage_match_evidence(item, query_text=query_text, preferred_symbol=preferred_symbol)
    path = normalize_usage_path(str(item.get("path") or ""))
    return (
        int(bool(evidence["preferred_symbol_invocation"])),
        int(bool(evidence["preferred_symbol_in_text"])),
        int(bool(evidence["preferred_symbol_in_path"])),
        int(min(evidence["query_text_overlap"], 5.0)),
        int(min(evidence["query_path_overlap"], 4.0)),
        int(bool(evidence["is_source_extension"])),
        -int(bool(evidence["has_definition_hint"])),
        -int(bool(evidence["is_test_path"])),
        -int(bool(evidence["is_generated_path"])),
        int(min(evidence["member_call_count"], 4.0) + min(evidence["call_count"], 4.0)),
        -len(path),
    )


def prioritize_usage_matches(
    matches: Sequence[Dict[str, str]],
    query_text: str = "",
    preferred_symbol: str = "",
) -> List[Dict[str, str]]:
    ranked = list(matches or [])
    ranked.sort(
        key=lambda item: (
            _usage_match_rank_key(item, query_text=query_text, preferred_symbol=preferred_symbol),
        ),
        reverse=True,
    )
    return ranked


def parse_line_range(line_range: str) -> Tuple[int, int]:
    raw = str(line_range or "").strip()
    if not raw:
        return 1, 1
    try:
        start_s, end_s = raw.split("-", 1)
        start = max(1, int(start_s))
        end = max(start, int(end_s))
        return start, end
    except Exception:
        return 1, 1


def expand_line_window(
    start_line: int,
    end_line: int,
    response_type: Optional[str],
    max_line_span: int,
) -> Tuple[int, int]:
    context_lines = max(4, int(config.CODE_SEARCH_CONTEXT_LINES))
    if str(response_type or "").strip().lower() in _USAGE_CODE_RESPONSE_TYPES:
        context_lines = max(context_lines, 35)

    start = max(1, int(start_line) - context_lines)
    end = max(start, int(end_line) + context_lines)
    capped_span = clamp_int(max_line_span, 20, 500)
    if (end - start + 1) > capped_span:
        end = start + capped_span - 1
    return start, end

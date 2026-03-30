import asyncio
import json
import re
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .... import rag_config
from ....core.llm_utils import (
    build_chat_template_extra_body,
    extract_completion_finish_reason,
    safe_chat_completion_create,
    stream_chat_completion_text_with_meta,
)
from ....utils.file_indexing import language_from_name


TokenCallback = Optional[Callable[[str], Awaitable[None] | None]]

_XML_DOC_TAG_RE = re.compile(
    r"^</?(?:summary|remarks|returns|param|value|example|code|span)\b[^>]*>$",
    flags=re.IGNORECASE,
)
_SECTION_HEADING_RE = re.compile(r"^(?:#{1,6}\s+|\d+\.\s+)")
_SUMMARY_PREFIX_RE = re.compile(r"^(?:요약|정리|설명)\s*:")
_USAGE_GUIDE_SECTION_TITLES = [
    "개요",
    "핵심 근거",
    "호출 흐름",
    "대표 코드",
    "주의점",
]


def _usage_bundle_prompt_payload(bundle: Dict[str, Any]) -> Dict[str, Any]:
    primary_example = dict(bundle.get("primary_example", {}) or {})
    grounded_example_snippets: List[Dict[str, Any]] = []
    for step in list(bundle.get("implementation_steps", []) or []):
        for row in list(step.get("evidence", []) or []):
            grounded_example_snippets.append(
                {
                    "step": step.get("title"),
                    "path": row.get("path"),
                    "line_range": row.get("line_range"),
                    "excerpt": row.get("excerpt"),
                }
            )
            if len(grounded_example_snippets) >= 8:
                break
        if len(grounded_example_snippets) >= 8:
            break
    return {
        "symbol": bundle.get("symbol"),
        "focus_example_dir": bundle.get("focus_example_dir"),
        "focus_example_cluster": bundle.get("focus_example_cluster"),
        "example_language": _preferred_usage_code_language(bundle),
        "example_files": list(bundle.get("example_files", []) or [])[:8],
        "primary_example": primary_example,
        "supporting_files": list(bundle.get("supporting_files", []) or [])[:8],
        "related_types": list(bundle.get("related_types", []) or [])[:8],
        "recommended_sequence": list(bundle.get("recommended_sequence", []) or []),
        "implementation_steps": list(bundle.get("implementation_steps", []) or []),
        "grounded_example_snippets": grounded_example_snippets,
        "file_profiles": list(bundle.get("file_profiles", []) or [])[:8],
        "coverage": dict(bundle.get("coverage", {}) or {}),
        "sections": dict(bundle.get("sections", {}) or {}),
        "matches": list(bundle.get("matches", []) or [])[:10],
    }


def _iter_usage_bundle_paths(bundle: Dict[str, Any]) -> List[str]:
    candidates: List[str] = []
    primary_example = dict(bundle.get("primary_example", {}) or {})
    for value in (
        primary_example.get("path"),
        *(bundle.get("example_files", []) or []),
        *(bundle.get("supporting_files", []) or []),
    ):
        path = str(value or "").strip()
        if path:
            candidates.append(path)
    for item in list(bundle.get("file_profiles", []) or []):
        path = str(item.get("path") or "").strip()
        if path:
            candidates.append(path)
    for item in list(bundle.get("matches", []) or []):
        path = str(item.get("path") or "").strip()
        if path:
            candidates.append(path)
    deduped: List[str] = []
    seen = set()
    for path in candidates:
        key = path.replace("\\", "/").lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path)
    return deduped


def _preferred_usage_code_language(bundle: Dict[str, Any]) -> str:
    primary_example = dict(bundle.get("primary_example", {}) or {})
    primary_path = str(primary_example.get("path") or "").strip()
    if primary_path:
        primary_language = language_from_name(primary_path)
        if primary_language != "text":
            return primary_language

    counts: Dict[str, int] = {}
    for path in _iter_usage_bundle_paths(bundle):
        language = language_from_name(path)
        if language == "text":
            continue
        counts[language] = counts.get(language, 0) + 1
    if not counts:
        return "text"
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _normalized_path_in_dir(path: str, directory: str) -> bool:
    normalized_path = str(path or "").replace("\\", "/").strip("/").lower()
    normalized_dir = str(directory or "").replace("\\", "/").strip("/").lower()
    return bool(normalized_path and normalized_dir) and (
        normalized_path == normalized_dir or normalized_path.startswith(f"{normalized_dir}/")
    )


def _group_row_sort_key(
    row: Dict[str, Any],
    *,
    focus_dir: str,
    primary_path: str,
) -> tuple[int, int, int, str]:
    path = str(row.get("path") or "")
    normalized = str(path or "").replace("\\", "/").lower()
    is_focus = _normalized_path_in_dir(normalized, focus_dir)
    is_primary = normalized == str(primary_path or "").replace("\\", "/").lower()
    suffix = Path(normalized).suffix.lower()
    is_header = suffix in {".h", ".hh", ".hpp", ".hxx"}
    return (
        0 if is_primary else 1,
        0 if is_focus else 1,
        1 if is_header else 0,
        normalized,
    )


def _looks_like_grounded_code_line(line: str) -> bool:
    stripped = str(line or "").strip()
    if not stripped:
        return False
    if stripped in {"{", "}", "};"}:
        return True
    if stripped.startswith(("//", "/*", "*/", "* ")):
        return False
    if _XML_DOC_TAG_RE.fullmatch(stripped):
        return False
    if _SECTION_HEADING_RE.match(stripped):
        return False
    if _SUMMARY_PREFIX_RE.match(stripped):
        return False
    code_starts = (
        "using ",
        "namespace ",
        "class ",
        "partial class ",
        "public ",
        "private ",
        "protected ",
        "internal ",
        "static ",
        "return ",
        "if ",
        "for ",
        "while ",
        "switch ",
        "case ",
        "break",
        "continue",
        "#include",
        "typedef ",
        "enum ",
        "struct ",
        "ref class ",
        "gcnew ",
        "new ",
        "try",
        "catch",
        "finally",
        "function ",
        "def ",
        "import ",
        "from ",
        "const ",
        "let ",
        "var ",
    )
    lowered = stripped.lower()
    if lowered.startswith(code_starts):
        return True
    if re.search(r"\b[A-Za-z_][A-Za-z0-9_.]*\s*\(", stripped):
        return True
    if re.search(r"\b[A-Za-z_][A-Za-z0-9_.]*\s*=", stripped):
        return True
    if ";" in stripped or "=>" in stripped or "::" in stripped or "->" in stripped:
        return True
    return False


def _clean_grounded_example_excerpt(excerpt: str) -> str:
    cleaned: List[str] = []
    for raw_line in str(excerpt or "").splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("///"):
            line = re.sub(r"^\s*///\s?", "", line)
        stripped = line.strip()
        if not stripped:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue
        if not _looks_like_grounded_code_line(stripped):
            continue
        cleaned.append(line.rstrip())

    while cleaned and cleaned[0] == "":
        cleaned.pop(0)
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned).strip()


def _build_grounded_usage_snippet(bundle: Dict[str, Any]) -> str:
    snippets: List[str] = []
    seen_ranges = set()
    primary_path = str(dict(bundle.get("primary_example", {}) or {}).get("path") or "")
    focus_dir = str(bundle.get("focus_example_dir") or "")
    preferred_categories = ("definition", "usage", "calls", "updates", "support")

    for category in preferred_categories:
        rows = sorted(
            list(dict(bundle.get("sections", {}) or {}).get(category, []) or []),
            key=lambda row: _group_row_sort_key(row, focus_dir=focus_dir, primary_path=primary_path),
        )
        for row in rows:
            path = str(row.get("path") or "")
            line_range = str(row.get("line_range") or "")
            key = f"{path}::{line_range}"
            if key in seen_ranges:
                continue
            cleaned = _clean_grounded_example_excerpt(str(row.get("excerpt") or ""))
            if not cleaned or cleaned in snippets:
                continue
            seen_ranges.add(key)
            snippets.append(cleaned)
            break

    if not snippets:
        for row in list(_usage_bundle_prompt_payload(bundle).get("grounded_example_snippets", []) or []):
            cleaned = _clean_grounded_example_excerpt(str(row.get("excerpt") or ""))
            if not cleaned or cleaned in snippets:
                continue
            snippets.append(cleaned)
            if len(snippets) >= 3:
                break

    return "\n\n".join(snippets[:4]).strip()


def _normalize_usage_guide_section_headings(answer: str) -> str:
    text = str(answer or "")
    for title in _USAGE_GUIDE_SECTION_TITLES:
        text = re.sub(
            rf"(?m)^(?:#{{0,6}}\s*)?{re.escape(title)}\s*$",
            f"## {title}",
            text,
        )
    return text


def _postprocess_usage_guide_answer(answer: str, bundle: Dict[str, Any]) -> str:
    text = _normalize_usage_guide_section_headings(str(answer or "").strip())
    snippet = _build_grounded_usage_snippet(bundle)
    if not snippet:
        return text
    if "```" in text:
        return text
    code_language = _preferred_usage_code_language(bundle) or "text"
    block = f"## 대표 코드\n\n```{code_language}\n{snippet.rstrip()}\n```"
    return (text.rstrip() + "\n\n" + block).strip()


def _usage_guide_answer_looks_incomplete(answer: str) -> bool:
    text = str(answer or "").strip()
    if not text:
        return True
    return text.count("```") % 2 == 1


def _finalize_usage_guide_answer(answer: str) -> str:
    text = str(answer or "").strip()
    if text.count("```") % 2 == 1:
        text = text.rstrip() + "\n```"
    return text


def _usage_bundle_has_tutorial_signal(bundle: Dict[str, Any]) -> bool:
    if not isinstance(bundle, dict) or not bundle:
        return False
    coverage = dict(bundle.get("coverage", {}) or {})
    primary_example = dict(bundle.get("primary_example", {}) or {})
    if primary_example.get("path"):
        return True
    if list(bundle.get("matches", []) or []):
        if bool(coverage.get("has_definition")):
            return True
        if any(bool(coverage.get(key)) for key in ("has_usage", "has_calls", "has_updates", "has_support")):
            return True
    return False


def _usage_guide_repair_payload(
    clean_message: str,
    answer: str,
    results: List[Dict[str, Any]],
    sources: List[Dict[str, Any]],
) -> Dict[str, Any]:
    evidence_rows: List[Dict[str, Any]] = []
    for item in list(results or [])[:8]:
        payload = dict(item.get("payload", {}) or {})
        evidence_rows.append(
            {
                "file_path": payload.get("file_path") or payload.get("source_file"),
                "module": payload.get("module"),
                "line_start": payload.get("line_start"),
                "line_end": payload.get("line_end"),
                "text": str(payload.get("text") or "")[:600],
                "score": item.get("combined_score", item.get("dense_score")),
            }
        )
    return {
        "question": clean_message,
        "current_answer": answer,
        "sources": list(sources or [])[:8],
        "evidence_rows": evidence_rows,
    }


async def _repair_usage_guide_answer_from_results(
    *,
    state,
    model_name: str,
    max_tokens: int,
    temperature: float,
    clean_message: str,
    answer: str,
    results: List[Dict[str, Any]],
    sources: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if getattr(state, "vllm_client", None) is None:
        return {"text": answer, "truncated": False}

    async def _continue_repair(existing_text: str) -> Dict[str, Any]:
        completion = await asyncio.to_thread(
            safe_chat_completion_create,
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": existing_text},
                {
                    "role": "user",
                    "content": "Continue exactly from where you left off. Do not repeat previous text.",
                },
            ],
            max_tokens=max(512, int(max_tokens or 1600), 3200),
            temperature=max(0.0, min(float(temperature), 0.3)),
            client=state.vllm_client,
            extra_body=build_chat_template_extra_body(rag_config.model_native_generation_enable_thinking()),
        )
        if not completion.choices:
            return {"text": existing_text, "truncated": False}
        return {
            "text": str(completion.choices[0].message.content or "").strip(),
            "truncated": extract_completion_finish_reason(completion) == "length",
        }

    system_prompt = (
        "You are repairing a Korean grounded code-usage answer that ended incomplete.\n"
        "Use only the provided evidence rows and current answer.\n"
        "Keep the structure concise and evidence-backed. Do not invent stages or files."
    )
    user_prompt = (
        "Repair this incomplete grounded usage answer.\n\n"
        f"{json.dumps(_usage_guide_repair_payload(clean_message, answer, results, sources), ensure_ascii=False)}"
    )
    completion = await asyncio.to_thread(
        safe_chat_completion_create,
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max(512, int(max_tokens or 1600), 3200),
        temperature=max(0.0, min(float(temperature), 0.3)),
        client=state.vllm_client,
        extra_body=build_chat_template_extra_body(rag_config.model_native_generation_enable_thinking()),
    )
    if not completion.choices:
        return {"text": answer, "truncated": False}
    repaired = str(completion.choices[0].message.content or "").strip()
    truncated = extract_completion_finish_reason(completion) == "length"
    attempts = 0
    while repaired and (_usage_guide_answer_looks_incomplete(repaired) or truncated) and attempts < 2:
        continuation = await _continue_repair(repaired)
        extra_text = str(continuation.get("text") or "").strip()
        if not extra_text:
            break
        repaired = repaired.rstrip() + "\n" + extra_text.lstrip()
        truncated = bool(continuation.get("truncated"))
        attempts += 1
    repaired = _finalize_usage_guide_answer(repaired)
    return {
        "text": repaired or answer,
        "truncated": truncated or _usage_guide_answer_looks_incomplete(repaired),
    }


async def _generate_usage_guide_answer_from_bundle(
    *,
    state,
    model_name: str,
    max_tokens: int,
    temperature: float,
    system_prompt_seed: str,
    clean_message: str,
    bundle: Dict[str, Any],
    token_callback: TokenCallback = None,
) -> Dict[str, Any]:
    if getattr(state, "vllm_client", None) is None:
        return {"text": "", "truncated": False}

    preferred_sections = "\n".join(f"- {title}" for title in _USAGE_GUIDE_SECTION_TITLES)
    system_prompt = (
        (str(system_prompt_seed or "").strip() + "\n\n") if str(system_prompt_seed or "").strip() else ""
    ) + (
        "You are writing a grounded Korean code-usage explanation from structured code evidence.\n"
        "Organize around the strongest confirmed evidence.\n"
        "Preferred section shape when it fits the evidence:\n"
        f"{preferred_sections}\n"
        "Only include sections that are supported by the bundle.\n"
        "Prefer bundle.primary_example.path as the main narrative anchor when present.\n"
        "Use bundle.example_language for fenced code when it is not 'text'.\n"
        "Do not invent lifecycle stages, setup steps, or framework conventions that are not present in the evidence.\n"
    )
    user_prompt = (
        f"User question:\n{clean_message}\n\n"
        "Structured usage bundle:\n"
        f"{json.dumps(_usage_bundle_prompt_payload(bundle), ensure_ascii=False)}\n\n"
        "Write the final answer now."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    extra_body = build_chat_template_extra_body(
        False if token_callback is not None else rag_config.model_native_generation_enable_thinking()
    )
    if token_callback is not None:
        return await stream_chat_completion_text_with_meta(
            model=model_name,
            messages=messages,
            max_tokens=max(256, int(max_tokens or 1600)),
            temperature=max(0.0, min(float(temperature), 0.3)),
            client=state.vllm_client,
            extra_body=extra_body,
            on_token=token_callback,
        )

    completion = await asyncio.to_thread(
        safe_chat_completion_create,
        model=model_name,
        messages=messages,
        max_tokens=max(256, int(max_tokens or 1600)),
        temperature=max(0.0, min(float(temperature), 0.3)),
        client=state.vllm_client,
        extra_body=extra_body,
    )
    if not completion.choices:
        return {"text": "", "truncated": False}
    return {
        "text": str(completion.choices[0].message.content or "").strip(),
        "truncated": extract_completion_finish_reason(completion) == "length",
    }


__all__ = [
    "_generate_usage_guide_answer_from_bundle",
    "_postprocess_usage_guide_answer",
    "_repair_usage_guide_answer_from_results",
    "_usage_bundle_has_tutorial_signal",
    "_usage_guide_answer_looks_incomplete",
]

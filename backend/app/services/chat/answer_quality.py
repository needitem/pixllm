import re
from typing import Any, Dict, List


_ANSWER_QUALITY_STOPWORDS = {
    "this",
    "that",
    "with",
    "from",
    "there",
    "which",
    "then",
    "into",
    "after",
    "before",
    "when",
    "where",
    "while",
    "uses",
    "using",
    "user",
    "flow",
    "code",
    "file",
    "method",
    "logic",
    "answer",
    "retrieved",
    "evidence",
    "therefore",
}

_CODE_LIKE_PATTERN = re.compile(
    r"(?:[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z0-9_]+|[A-Za-z_][A-Za-z0-9_]*_[A-Za-z0-9_]+|[A-Za-z0-9_]+\.(?:cs|cpp|c|h|hpp|xaml)|[A-Za-z_][A-Za-z0-9_]{2,}\s*\()"
)


def _claim_tokens(text: str) -> List[str]:
    tokens: List[str] = []
    seen = set()
    for token in re.findall(r"[A-Za-z0-9_가-힣]{2,}", str(text or "").lower()):
        if token in _ANSWER_QUALITY_STOPWORDS:
            continue
        if len(token) < 4 and not any(ch.isdigit() for ch in token):
            continue
        if token in seen:
            continue
        seen.add(token)
        tokens.append(token)
    return tokens


def build_context_pack(
    *,
    results: List[Dict[str, Any]],
    sources: List[Dict[str, Any]],
    response_type: str,
    execution_plan: Dict[str, Any],
    workspace_snapshot: Dict[str, Any] | None = None,
    local_overlay: Dict[str, Any] | None = None,
    layer_manifest: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    definitions: List[Dict[str, Any]] = []
    examples: List[Dict[str, Any]] = []
    settings: List[Dict[str, Any]] = []
    caveats: List[Dict[str, Any]] = []

    for item in list(results or [])[:20]:
        payload = dict(item.get("payload", {}) or {})
        path = str(payload.get("source_file") or payload.get("file_path") or "")
        entry = {
            "path": path,
            "line_start": payload.get("line_start"),
            "line_end": payload.get("line_end"),
            "text": str(payload.get("text") or "")[:400],
        }
        lower_path = path.replace("\\", "/").lower()
        lower_text = str(payload.get("text") or "").lower()
        if any(token in lower_text for token in ("class ", "public ref class", "namespace ", "typedef ", "enum ")):
            definitions.append(entry)
        if any(token in lower_path for token in ("/examples/", "/example/", "/sample/", "/tutorial/", "/demo/")):
            examples.append(entry)
        if any(token in lower_text for token in ("config", "setting", "configure", "register", "bind", "option")):
            settings.append(entry)
        if any(token in lower_text for token in ("warning", "caution", "주의", "must ", "should ", "cannot ", "error")):
            caveats.append(entry)

    return {
        "response_type": response_type,
        "task_family": execution_plan.get("task_family"),
        "corpus_profile": execution_plan.get("corpus_profile"),
        "layer_manifest": layer_manifest or {},
        "grounding_report": dict((local_overlay or {}).get("grounding_report") or {}),
        "definitions": definitions[:6],
        "examples": examples[:6],
        "settings": settings[:6],
        "caveats": caveats[:6],
        "sources": list(sources or [])[:8],
        "workspace_snapshot": workspace_snapshot or {},
        "local_overlay": local_overlay or {},
    }


def build_provenance_report(answer: str, results: List[Dict[str, Any]], sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    evidence_text = "\n".join(str(dict(item.get("payload", {}) or {}).get("text") or "") for item in results or [])
    evidence_paths = {str(src.get("file_path") or "") for src in sources or []}
    code_blocks = re.findall(r"```[a-zA-Z0-9_-]*\n(.*?)```", str(answer or ""), flags=re.DOTALL)

    block_reports = []
    grounded_blocks = 0
    for block in code_blocks:
        significant_lines = [line.strip() for line in block.splitlines() if line.strip() and not line.strip().startswith("//")]
        grounded = any(line in evidence_text for line in significant_lines[:5]) if significant_lines else False
        block_reports.append({"line_count": len(significant_lines), "grounded": grounded})
        if grounded:
            grounded_blocks += 1

    return {
        "code_block_count": len(code_blocks),
        "grounded_code_block_count": grounded_blocks,
        "all_code_blocks_grounded": grounded_blocks == len(code_blocks) if code_blocks else True,
        "source_count": len(evidence_paths),
        "blocks": block_reports,
    }


def detect_unsupported_claims(answer: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
    evidence_parts: List[str] = []
    for item in results or []:
        payload = dict(item.get("payload", {}) or {})
        evidence_parts.append(str(payload.get("text") or ""))
        evidence_parts.append(str(payload.get("file_path") or ""))
        evidence_parts.append(str(payload.get("source_file") or ""))
    evidence_text = " ".join(evidence_parts).lower()
    evidence_tokens = set(_claim_tokens(evidence_text))
    sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+|\n+", str(answer or "")) if segment.strip()]
    suspicious: List[str] = []
    for sentence in sentences:
        lowered = sentence.lower()
        if lowered.startswith("#"):
            continue
        if lowered.startswith("|"):
            continue
        sentence_body = re.sub(r"^[\-\*\d\.\)\s]+", "", sentence).strip()
        tokens = _claim_tokens(sentence_body)
        if not tokens:
            continue
        overlap = sum(1 for token in tokens[:12] if token in evidence_tokens)
        code_like = bool(_CODE_LIKE_PATTERN.search(sentence_body))
        if code_like and overlap == 0:
            suspicious.append(sentence)
            continue
        if len(tokens) >= 6 and overlap == 0:
            suspicious.append(sentence)
    return {
        "unsupported_count": len(suspicious),
        "unsupported_segments": suspicious[:10],
        "all_supported": len(suspicious) == 0,
    }

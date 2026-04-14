import time
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import yaml

from ... import config
from .query_terms import extract_query_compacts, extract_query_terms, extract_symbol_query_candidates
from .support import clamp_int

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_WORKFLOW_QUERY_RE = re.compile(r"(workflow|program|example|steps|guide|how to|load|display|show|render|host|만들|프로그램|예제|단계|도시|표시|로드)", re.IGNORECASE)
_WORKFLOW_SECTION_RE = re.compile(r"(workflow|steps|program|example|guide|recipe|usage|flow|minimal)", re.IGNORECASE)
_METHODS_TITLE_RE = re.compile(r"\bmethods?\b", re.IGNORECASE)

def wiki_root() -> Path:
    return _BACKEND_ROOT / config.ORCHESTRATION_CONFIG_DIR / "wiki" / "engine"


def _read_frontmatter(raw_text: str) -> Tuple[Dict[str, Any], str]:
    text = str(raw_text or "")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    try:
        meta = yaml.safe_load(text[4:end]) or {}
    except Exception:
        meta = {}
    body = text[end + 5 :]
    return meta if isinstance(meta, dict) else {}, body


def _split_sections(body: str) -> List[Dict[str, str]]:
    sections: List[Dict[str, str]] = []
    current_heading = "Overview"
    current_lines: List[str] = []

    for raw_line in str(body or "").splitlines():
        line = raw_line.rstrip()
        if line.startswith("#"):
            if current_lines:
                sections.append(
                    {
                        "heading": current_heading,
                        "text": "\n".join(current_lines).strip(),
                    }
                )
                current_lines = []
            current_heading = line.lstrip("#").strip() or current_heading
            continue
        current_lines.append(line)

    if current_lines:
        sections.append(
            {
                "heading": current_heading,
                "text": "\n".join(current_lines).strip(),
            }
        )

    return [section for section in sections if section.get("text")]


def _score_page(
    *,
    query: str,
    title: str,
    aliases: Iterable[str],
    symbols: Iterable[str],
    tags: Iterable[str],
    heading: str,
    text: str,
) -> int:
    score = 0
    title_compacts = extract_query_compacts(title, limit=12)
    heading_compacts = extract_query_compacts(heading, limit=12)
    content_compacts = extract_query_compacts(text, limit=30)
    alias_compacts = [compact for alias in aliases for compact in extract_query_compacts(alias, limit=8)]
    symbol_compacts = [compact for symbol in symbols for compact in extract_query_compacts(symbol, limit=8)]
    tag_compacts = [compact for tag in tags for compact in extract_query_compacts(tag, limit=8)]
    query_compacts = extract_query_compacts(query, limit=18)
    query_terms = [term.lower() for term in extract_query_terms(query, limit=10)]
    query_symbols = [symbol.lower() for symbol in extract_symbol_query_candidates(query, max_candidates=4)]
    title_text = title.lower()
    heading_text = heading.lower()
    body_text = text.lower()
    task_query = bool(_WORKFLOW_QUERY_RE.search(query or ""))
    workflowish_title = bool(_WORKFLOW_SECTION_RE.search(title))
    workflowish_heading = bool(_WORKFLOW_SECTION_RE.search(heading))
    workflowish_tags = any(bool(_WORKFLOW_SECTION_RE.search(str(tag or ""))) for tag in tags)
    contains_source_anchor = "source/" in body_text

    for compact in query_compacts:
        if compact in title_compacts:
            score += 18
        if compact in alias_compacts:
            score += 16
        if compact in symbol_compacts:
            score += 16
        if compact in heading_compacts:
            score += 12
        if compact in tag_compacts:
            score += 8
        if compact in content_compacts:
            score += 4

    for symbol in query_symbols:
        if symbol in title_text:
            score += 12
        if symbol in heading_text:
            score += 10
        if symbol in body_text:
            score += 5

    for term in query_terms:
        if term in title_text:
            score += 8
        if term in heading_text:
            score += 6
        if term in body_text:
            score += 2

    if task_query:
        if workflowish_title:
            score += 32
        if workflowish_heading:
            score += 24
        if workflowish_tags:
            score += 18
        if contains_source_anchor:
            score += 8
        if _METHODS_TITLE_RE.search(title or "") and not workflowish_heading:
            score -= 8

    if "verified api facts" in heading_text:
        score += 10
    if "workflow" in heading_text or "usage" in heading_text:
        score += 6
    return score


def _page_result(
    *,
    root: Path,
    file_path: Path,
    title: str,
    symbols: Iterable[str],
    tags: Iterable[str],
    section_heading: str,
    section_text: str,
    max_chars: int,
    index: int,
    score: int,
) -> Dict[str, Any]:
    rel_path = file_path.relative_to(root).as_posix()
    chunk_id = f"wiki:{rel_path}#section-{index}"
    doc_id = f"wiki:{rel_path}"
    clipped = str(section_text or "")[: max(400, clamp_int(max_chars, 400, 12000))]
    return {
        "chunk_id": chunk_id,
        "doc_id": doc_id,
        "source_url": rel_path,
        "file_path": rel_path,
        "heading_path": f"{title} > {section_heading}",
        "paragraph_range": f"section:{index}",
        "text": clipped,
        "truncated": len(clipped) < len(str(section_text or "")),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(file_path.stat().st_mtime)),
        "source_kind": "wiki",
        "document_type": "wiki",
        "score": score,
        "title": title,
        "symbols": [str(item or "").strip() for item in symbols if str(item or "").strip()],
        "tags": [str(item or "").strip() for item in tags if str(item or "").strip()],
    }


def search_wiki(
    *,
    query: str,
    top_k: int,
    max_chars: int,
) -> Dict[str, Any]:
    started_at = time.perf_counter()
    root = wiki_root()
    if not root.exists() or not root.is_dir():
        return {"query": query, "results": [], "chunks": [], "query_time_ms": 0.0, "reason": "wiki_unavailable"}

    ranked: List[Dict[str, Any]] = []
    for file_path in sorted(root.rglob("*.md")):
        raw_text = file_path.read_text(encoding="utf-8")
        meta, body = _read_frontmatter(raw_text)
        title = str(meta.get("title") or file_path.stem).strip()
        aliases = meta.get("aliases") if isinstance(meta.get("aliases"), list) else []
        symbols = meta.get("symbols") if isinstance(meta.get("symbols"), list) else []
        tags = meta.get("tags") if isinstance(meta.get("tags"), list) else []
        for index, section in enumerate(_split_sections(body), 1):
            score = _score_page(
                query=query,
                title=title,
                aliases=aliases,
                symbols=symbols,
                tags=tags,
                heading=section.get("heading") or "",
                text=section.get("text") or "",
            )
            if score <= 0:
                continue
            ranked.append(
                _page_result(
                    root=root,
                    file_path=file_path,
                    title=title,
                    symbols=symbols,
                    tags=tags,
                    section_heading=section.get("heading") or "Overview",
                    section_text=section.get("text") or "",
                    max_chars=max_chars,
                    index=index,
                    score=score,
                )
            )

    ranked.sort(key=lambda item: (int(item.get("score") or 0), item.get("heading_path") or ""), reverse=True)
    capped = ranked[: clamp_int(top_k, 1, 20)]
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    return {
        "query": query,
        "results": capped,
        "chunks": capped,
        "query_time_ms": elapsed_ms,
    }

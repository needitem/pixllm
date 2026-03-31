from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ....utils.file_indexing import language_from_name


def parse_line_bounds(line_range: str) -> Tuple[Optional[int], Optional[int]]:
    raw = str(line_range or "").strip()
    if not raw:
        return None, None
    try:
        start_s, end_s = raw.split("-", 1)
        start = max(1, int(start_s))
        end = max(start, int(end_s))
        return start, end
    except Exception:
        return None, None


def build_sources(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in results:
        md = r.get("payload", {})
        line_start = md.get("line_start")
        line_end = md.get("line_end")
        if (line_start is None or line_end is None) and md.get("line_range"):
            parsed_start, parsed_end = parse_line_bounds(str(md.get("line_range")))
            line_start = line_start if line_start is not None else parsed_start
            line_end = line_end if line_end is not None else parsed_end
        out.append(
            {
                "file_path": md.get("file_path"),
                "source_file": md.get("source_file"),
                "module": md.get("module"),
                "language": md.get("language"),
                "source_kind": md.get("source_kind"),
                "document_id": md.get("document_id"),
                "section_path": md.get("section_path") or md.get("heading_path"),
                "paragraph_range": md.get("paragraph_range"),
                "page_number": md.get("page_number"),
                "total_pages": md.get("total_pages"),
                "line_start": line_start,
                "line_end": line_end,
                "preview_text": md.get("text"),
                "score": r.get("combined_score", r.get("dense_score")),
            }
        )
    return out

def tool_evidence_to_results(evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    docs = evidence.get("docs", {}) if isinstance(evidence, dict) else {}
    code = evidence.get("code", {}) if isinstance(evidence, dict) else {}

    doc_search_rows = docs.get("search", {}).get("results", []) if isinstance(docs.get("search", {}), dict) else []
    doc_score_by_chunk = {}
    for row in doc_search_rows:
        chunk_id = str(row.get("chunk_id") or "").strip()
        if chunk_id:
            doc_score_by_chunk[chunk_id] = float(row.get("score") or 0.0)

    opened_doc_chunk_ids = set()
    for chunk in docs.get("chunks", []) or []:
        chunk_id = str(chunk.get("chunk_id") or "")
        if chunk_id:
            opened_doc_chunk_ids.add(chunk_id)
        source_url = str(chunk.get("source_url") or chunk.get("doc_id") or "document")
        file_name = Path(source_url).name or source_url
        heading_path = chunk.get("heading_path")
        if isinstance(heading_path, list):
            section_path = " > ".join(str(x) for x in heading_path if str(x).strip())
        else:
            section_path = str(heading_path or "root")
        payload = {
            "file_path": source_url,
            "source_file": source_url,
            "module": chunk.get("doc_id"),
            "document_id": chunk.get("doc_id"),
            "language": language_from_name(file_name),
            "line_start": None,
            "line_end": None,
            "section_path": section_path,
            "text": str(chunk.get("text") or ""),
            "type": "doc",
            "source_kind": "documents",
        }
        out.append(
            {
                "id": f"doc:{chunk_id}",
                "payload": payload,
                "dense_score": doc_score_by_chunk.get(chunk_id, 0.0),
                "sparse_score": 0.0,
                "combined_score": doc_score_by_chunk.get(chunk_id, 0.0),
            }
        )

    for row in doc_search_rows:
        chunk_id = str(row.get("chunk_id") or "").strip()
        if not chunk_id or chunk_id in opened_doc_chunk_ids:
            continue
        source_url = str(row.get("source_url") or row.get("doc_id") or "document")
        file_name = Path(source_url).name or source_url
        heading_path = row.get("heading_path")
        if isinstance(heading_path, list):
            section_path = " > ".join(str(x) for x in heading_path if str(x).strip())
        else:
            section_path = str(heading_path or "root")
        score = float(row.get("score") or 0.0)
        payload = {
            "file_path": source_url,
            "source_file": source_url,
            "module": row.get("doc_id"),
            "document_id": row.get("doc_id"),
            "language": language_from_name(file_name),
            "line_start": None,
            "line_end": None,
            "section_path": section_path,
            "text": str(row.get("text") or ""),
            "type": "doc_search_hit",
            "source_kind": "doc_search",
        }
        out.append(
            {
                "id": f"doc_search:{chunk_id}",
                "payload": payload,
                "dense_score": score,
                "sparse_score": 0.0,
                "combined_score": score,
            }
        )

    code_search_rows = code.get("search", {}).get("matches", []) if isinstance(code.get("search", {}), dict) else []
    code_rank_score: Dict[str, float] = {}
    for idx, row in enumerate(code_search_rows):
        key = f"{row.get('path')}::{row.get('line_range')}"
        code_rank_score[key] = max(0.01, 1.0 - (idx * 0.05))

    code_window_keys = {
        f"{str(window.get('path') or '')}::{str(window.get('line_range') or '')}"
        for window in (code.get("windows", []) or [])
        if str(window.get("path") or "").strip()
    }

    for idx, window in enumerate(code.get("windows", []) or []):
        path = str(window.get("path") or "")
        line_range = str(window.get("line_range") or "")
        start_line, end_line = parse_line_bounds(line_range)
        file_path = path
        key = f"{path}::{line_range}"
        source_kind = str(window.get("source_kind") or "code_tool").strip() or "code_tool"
        payload = {
            "file_path": file_path,
            "source_file": path,
            "module": None,
            "language": language_from_name(Path(path).name) if path else "text",
            "line_start": start_line,
            "line_end": end_line,
            "text": str(window.get("content") or ""),
            "type": "code_reference",
            "source_kind": source_kind,
        }
        out.append(
            {
                "id": f"code:{path}:{line_range or idx}",
                "payload": payload,
                "dense_score": code_rank_score.get(key, max(0.01, 0.9 - idx * 0.05)),
                "sparse_score": 0.0,
                "combined_score": code_rank_score.get(key, max(0.01, 0.9 - idx * 0.05)),
            }
        )

    for idx, row in enumerate(code_search_rows):
        path = str(row.get("path") or "")
        line_range = str(row.get("line_range") or "")
        if not path or not line_range:
            continue
        key = f"{path}::{line_range}"
        if key in code_window_keys:
            continue
        start_line, end_line = parse_line_bounds(line_range)
        file_path = path
        payload = {
            "file_path": file_path,
            "source_file": path,
            "module": None,
            "language": language_from_name(Path(path).name) if path else "text",
            "line_start": start_line,
            "line_end": end_line,
            "text": str(row.get("match") or ""),
            "type": "code_search_hit",
            "source_kind": "code_search",
        }
        out.append(
            {
                "id": f"code_search:{path}:{line_range}:{idx}",
                "payload": payload,
                "dense_score": max(0.05, 0.18 - idx * 0.015),
                "sparse_score": 0.0,
                "combined_score": max(0.05, 0.18 - idx * 0.015),
            }
        )

    return out

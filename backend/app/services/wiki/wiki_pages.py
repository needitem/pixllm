import time
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List

from .wiki_core import _extract_summary, _extract_title, _infer_kind
from .wiki_bundle import _collect_related_page_refs


def _page_payload(
    root: Path,
    file_path: Path,
    *,
    include_related: bool = False,
    max_related_pages: int = 10,
) -> Dict[str, Any]:
    raw_text = file_path.read_text(encoding="utf-8")
    rel_path = file_path.relative_to(root).as_posix()
    stat = file_path.stat()
    payload = {
        "wiki_id": root.name,
        "path": rel_path,
        "title": _extract_title(rel_path, raw_text),
        "kind": _infer_kind(rel_path),
        "content": raw_text,
        "summary": _extract_summary(raw_text),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat.st_mtime)),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat.st_ctime)),
        "version": 1,
    }
    if include_related:
        related_pages: List[Dict[str, Any]] = []
        for ref in _collect_related_page_refs(
            root,
            current_path=rel_path,
            content=raw_text,
            max_related_pages=max_related_pages,
        ):
            related_path = str(ref.get("path") or "").strip()
            if not related_path:
                continue
            related_file = root / PurePosixPath(related_path).as_posix()
            if not related_file.exists() or not related_file.is_file():
                continue
            related_payload = _page_payload(root, related_file, include_related=False)
            related_payload["relation"] = str(ref.get("relation") or "").strip()
            related_pages.append(related_payload)
        if related_pages:
            payload["related_pages"] = related_pages
            payload["related_paths"] = [str(item.get("path") or "").strip() for item in related_pages]
    return payload


__all__ = [name for name in globals() if not name.startswith("__")]

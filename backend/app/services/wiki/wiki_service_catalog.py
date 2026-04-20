import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from ... import config
from ...utils.time import now_iso
from .wiki_pages import _page_payload
from .wiki_runtime import (
    _BACKEND_ROOT,
    _CORE_COORDINATION_PATHS,
    _OPTIONAL_COORDINATION_PATHS,
    _extract_summary,
    _raw_source_root_text,
    _slugify,
    wiki_parent_root,
)

_PAGE_LIST_CACHE: Dict[str, Dict[str, object]] = {}
_MARKDOWN_INVENTORY_CACHE: Dict[str, Dict[str, object]] = {}
_MARKDOWN_INVENTORY_TTL_SECONDS = 1.0


def _markdown_inventory(root: Path) -> Dict[str, object]:
    cache_key = str(root.resolve())
    now = time.monotonic()
    cached = _MARKDOWN_INVENTORY_CACHE.get(cache_key)
    if cached and (now - float(cached.get("cached_at") or 0.0)) < _MARKDOWN_INVENTORY_TTL_SECONDS:
        return {
            "files": list(cached.get("files") or []),
            "count": int(cached.get("count") or 0),
            "latest_mtime": float(cached.get("latest_mtime") or 0.0),
        }
    files = sorted(root.rglob("*.md")) if root.exists() else []
    latest_mtime = max((item.stat().st_mtime for item in files), default=0.0)
    payload = {
        "files": files,
        "count": len(files),
        "latest_mtime": latest_mtime,
    }
    _MARKDOWN_INVENTORY_CACHE[cache_key] = {
        **payload,
        "cached_at": now,
    }
    return payload


class WikiServiceCatalogMixin:
    def _required_coordination_paths(self) -> List[str]:
        return list(_CORE_COORDINATION_PATHS)

    def _optional_coordination_paths(self) -> List[str]:
        return list(_OPTIONAL_COORDINATION_PATHS)

    def _meta(self, wiki_id: str) -> Dict[str, object]:
        normalized_wiki_id = _slugify(wiki_id, "engine")
        root = self._root(normalized_wiki_id)
        inventory = _markdown_inventory(root)
        pages = inventory["files"] if isinstance(inventory.get("files"), list) else []
        updated_at = None
        if pages:
            updated_at = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ",
                time.gmtime(float(inventory.get("latest_mtime") or 0.0)),
            )
        description = ""
        readme = root / "README.md"
        if readme.exists():
            description = _extract_summary(readme.read_text(encoding="utf-8"))
        return {
            "id": normalized_wiki_id,
            "name": normalized_wiki_id,
            "description": description,
            "root_path": root.relative_to(_BACKEND_ROOT).as_posix() if root.exists() else root.relative_to(_BACKEND_ROOT).as_posix(),
            "page_count": int(inventory.get("count") or 0),
            "updated_at": updated_at or now_iso(),
            "answer_mode": str(config.ANSWER_MODE or "wiki-only").strip() or "wiki-only",
            "raw_source_root": _raw_source_root_text(),
        }

    def _coordination_status_payload(
        self,
        *,
        wiki_id: str,
        present_paths: Iterable[str],
        missing_paths_before: Iterable[str],
        created_paths: Iterable[str],
        root_created: bool,
    ) -> Dict[str, object]:
        required_paths = self._required_coordination_paths()
        optional_paths = self._optional_coordination_paths()
        present_path_set = {str(path or "") for path in present_paths if str(path or "")}
        required_present = [path for path in required_paths if path in present_path_set]
        optional_present = [path for path in optional_paths if path in present_path_set]
        return {
            "wiki_id": _slugify(wiki_id, "engine"),
            "required_paths": required_paths,
            "optional_paths": optional_paths,
            "required_present_paths": required_present,
            "optional_present_paths": optional_present,
            "present_paths": [*required_present, *optional_present],
            "missing_paths": [path for path in required_paths if path not in required_present],
            "missing_paths_before": [str(path or "") for path in missing_paths_before if str(path or "")],
            "created_paths": [str(path or "") for path in created_paths if str(path or "")],
            "auto_bootstrapped": bool(root_created or list(created_paths)),
            "has_coordination_spine": all(path in required_present for path in required_paths),
        }

    async def list_wikis(self) -> List[Dict[str, object]]:
        parent = wiki_parent_root()
        if not parent.exists():
            return []
        items = []
        for child in sorted(parent.iterdir()):
            if not child.is_dir():
                continue
            if not list(child.rglob("*.md")):
                continue
            items.append(self._meta(child.name))
        return items

    async def list_pages(self, wiki_id: str) -> List[Dict[str, object]]:
        root = self._root(wiki_id)
        if not root.exists():
            return []
        inventory = _markdown_inventory(root)
        cache_key = str(root.resolve())
        cache_entry = _PAGE_LIST_CACHE.get(cache_key)
        file_count = int(inventory.get("count") or 0)
        latest_mtime = float(inventory.get("latest_mtime") or 0.0)
        if (
            cache_entry
            and int(cache_entry.get("count") or 0) == file_count
            and float(cache_entry.get("latest_mtime") or 0.0) == latest_mtime
        ):
            return list(cache_entry.get("pages") or [])
        pages = [_page_payload(root, file_path) for file_path in inventory.get("files") or []]
        _PAGE_LIST_CACHE[cache_key] = {
            "count": file_count,
            "latest_mtime": latest_mtime,
            "pages": pages,
        }
        return list(pages)

    async def get_page(self, wiki_id: str, page_path: str) -> Optional[Dict[str, object]]:
        file_path = self._page_file(wiki_id, page_path)
        root = self._root(wiki_id)
        if not file_path.exists() or not file_path.is_file():
            return None
        return _page_payload(root, file_path, include_related=True)


__all__ = ["WikiServiceCatalogMixin"]

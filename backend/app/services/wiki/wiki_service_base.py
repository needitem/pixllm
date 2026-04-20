from pathlib import Path
from typing import Dict

from .wiki_pages import _page_payload
from .wiki_runtime import _normalize_page_path


class WikiServiceBase:
    def _root(self, wiki_id: str) -> Path:
        return wiki_root(wiki_id)

    def _page_file(self, wiki_id: str, page_path: str) -> Path:
        root = self._root(wiki_id)
        normalized = _normalize_page_path(page_path)
        target = (root / normalized).resolve()
        if root.resolve() not in target.parents and target != root.resolve():
            raise ValueError("page path must stay inside the wiki root")
        return target

    def _write_page_text(self, wiki_id: str, page_path: str, content: str) -> Dict[str, object]:
        file_path = self._page_file(wiki_id, page_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(str(content or ""), encoding="utf-8")
        return _page_payload(self._root(wiki_id), file_path)


def wiki_root(wiki_id: str = "engine"):
    from . import wiki_runtime as runtime

    return runtime.wiki_root(wiki_id)


def raw_source_root():
    from . import wiki_runtime as runtime

    return runtime.raw_source_root()


__all__ = ["WikiServiceBase", "wiki_root", "raw_source_root"]

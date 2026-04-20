from typing import Any, Dict

from .wiki_lint_rules import run_wiki_lint


class WikiServiceLintingMixin:
    async def lint_wiki(self, wiki_id: str, *, repair: bool = False) -> Dict[str, Any]:
        return await run_wiki_lint(self, wiki_id, repair=repair)


__all__ = ["WikiServiceLintingMixin"]

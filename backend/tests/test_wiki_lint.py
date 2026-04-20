import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.wiki.service import WikiService


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class WikiLintTests(unittest.IsolatedAsyncioTestCase):
    async def test_lint_counts_bundle_pages_as_inbound_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            raw_root = Path(tmp) / "raw"
            raw_root.mkdir(parents=True, exist_ok=True)
            service = WikiService()
            with patch("app.services.wiki.wiki_runtime.wiki_root", return_value=root), patch(
                "app.services.wiki.wiki_runtime.raw_source_root", return_value=raw_root
            ):
                await service.ensure_coordination_pages("demo", create_if_missing=True)
                _write(
                    root / "workflows" / "wf-api-demo.md",
                    """---
title: Demo Workflow
aliases:
  - demo workflow
sources:
  - pages/sources/raw-source-root.md
---

# Overview
- Demo family workflow.

## Knowledge Bundle
```yaml
concept_terms:
  - demo concept
bundle_pages:
  - path: pages/howtos/demo-howto.md
    relation: family_howto
  - path: pages/concepts/demo-concept.md
    relation: family_concept
```

## Required Facts
```yaml
workflow_family: api_demo
required_facts:
  - symbol: Demo.Run
    declaration: 'void Run();'
```
""",
                )
                _write(
                    root / "pages" / "howtos" / "demo-howto.md",
                    """---
title: Demo Howto
description: How to perform the demo task.
sources:
  - pages/sources/raw-source-root.md
---

# Demo Howto
- demo 작업 하는 방법을 설명한다.
""",
                )
                _write(
                    root / "pages" / "concepts" / "demo-concept.md",
                    """---
title: Demo Concept
description: Demo concept coverage.
sources:
  - pages/sources/raw-source-root.md
---

# Demo Concept
- demo concept 설명.
""",
                )

                result = await service.lint_wiki("demo")

        orphan_paths = {
            str(item.get("path") or "")
            for item in result["findings"]
            if str(item.get("code") or "") == "orphan_page"
        }
        self.assertNotIn("pages/howtos/demo-howto.md", orphan_paths)
        self.assertNotIn("pages/concepts/demo-concept.md", orphan_paths)

    async def test_lint_flags_missing_concept_bundle_and_fact_divergence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            raw_root = Path(tmp) / "raw"
            raw_root.mkdir(parents=True, exist_ok=True)
            service = WikiService()
            with patch("app.services.wiki.wiki_runtime.wiki_root", return_value=root), patch(
                "app.services.wiki.wiki_runtime.raw_source_root", return_value=raw_root
            ):
                await service.ensure_coordination_pages("demo", create_if_missing=True)
                _write(
                    root / "workflows" / "wf-api-a.md",
                    """---
title: Workflow A
aliases:
  - workflow a
sources:
  - pages/sources/raw-source-root.md
---

# Overview
- First workflow.

## Knowledge Bundle
```yaml
concept_terms:
  - shared concept
bundle_pages:
  - path: pages/howtos/workflow-a.md
    relation: family_howto
```

## Required Facts
```yaml
workflow_family: api_demo_a
required_facts:
  - symbol: Demo.Run
    declaration: 'void Run();'
```
""",
                )
                _write(
                    root / "workflows" / "wf-api-b.md",
                    """---
title: Workflow B
aliases:
  - workflow b
sources:
  - pages/sources/raw-source-root.md
---

# Overview
- Second workflow.

## Knowledge Bundle
```yaml
concept_terms:
  - shared concept
bundle_pages:
  - path: pages/howtos/workflow-b.md
    relation: family_howto
  - path: pages/concepts/shared-concept.md
    relation: family_concept
```

## Required Facts
```yaml
workflow_family: api_demo_b
required_facts:
  - symbol: Demo.Run
    declaration: 'void Run(int mode);'
```
""",
                )
                _write(
                    root / "pages" / "howtos" / "workflow-a.md",
                    """---
title: Workflow A Howto
description: 첫번째 작업 관련 설명.
sources:
  - pages/sources/raw-source-root.md
---
""",
                )
                _write(
                    root / "pages" / "howtos" / "workflow-b.md",
                    """---
title: Workflow B Howto
description: 두번째 작업 관련 설명.
sources:
  - pages/sources/raw-source-root.md
---
""",
                )
                _write(
                    root / "pages" / "concepts" / "shared-concept.md",
                    """---
title: Shared Concept
description: shared concept 설명.
sources:
  - pages/sources/raw-source-root.md
---
""",
                )

                result = await service.lint_wiki("demo")

        codes = {str(item.get("code") or "") for item in result["findings"]}
        self.assertIn("missing_concept_bundle", codes)
        self.assertIn("workflow_fact_divergence", codes)


if __name__ == "__main__":
    unittest.main()

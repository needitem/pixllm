import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.app.services.wiki.service import WikiService


METHOD_PAGE = """---
title: Pixoneer.NXDL.NIO.XRasterIO Methods
---

# Overview

## Method Page Facts
```yaml
page_family: method_reference
qualified_type: Pixoneer.NXDL.NIO.XRasterIO
type_name: XRasterIO
namespace: Pixoneer.NXDL.NIO
method_section_prefix: "## "
```

## Runtime Usage
- Verification only.

## LoadFile
- Declaration: `Source/NXDLio/NXDLio.h:230`
- Implementation: `Source/NXDLio/XRasterIO.cpp:137`
"""


WORKFLOW_PAGE = """---
title: Raster Load Workflow
aliases:
  - Load Raster
symbols:
  - XRasterIO
  - LoadFile
tags:
  - engine
  - workflow
---

# Overview
- Goal: Load raster data with XRasterIO.

## Required Facts
```yaml
workflow_family: raster
output_shape: focused_snippet_or_helper
required_symbols:
  - XRasterIO.LoadFile
required_facts:
  - symbol: XRasterIO.LoadFile
    declaration: 'NRS::XRSLoadFile^ LoadFile(String^ strFileName, [OutAttribute] String^% strError, bool bCalcStatistics, eIOCreateXLDMode CreateXLD);'
    source: 'Source/NXDLio/NXDLio.h:230'
verification_rules:
  - use_this_workflow_as_primary_path
```
"""


def _wiki_root_factory(parent: Path):
    def _wiki_root(wiki_id: str = "engine") -> Path:
        normalized = str(wiki_id or "engine").strip().lower() or "engine"
        return parent / normalized

    return _wiki_root


class WikiServiceManifestTests(unittest.IsolatedAsyncioTestCase):
    async def test_rebuild_index_writes_runtime_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            wiki_root = _wiki_root_factory(parent)
            with patch("backend.app.services.wiki.service.wiki_parent_root", return_value=parent), patch(
                "backend.app.services.wiki.service.wiki_root",
                side_effect=wiki_root,
            ):
                svc = WikiService()
                await svc.ensure_coordination_pages("engine", create_if_missing=True)
                svc._write_page_text("engine", "methods/Methods_T_Pixoneer_NXDL_NIO_XRasterIO.md", METHOD_PAGE)
                svc._write_page_text("engine", "workflows/wf-raster-load.md", WORKFLOW_PAGE)

                await svc.rebuild_index("engine")

                manifest_path = parent / "engine" / ".runtime" / "manifest.json"
                self.assertTrue(manifest_path.exists(), "runtime manifest should be generated during rebuild")

                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                methods_index = payload.get("methods_index") or []
                workflow_index = payload.get("workflow_index") or []

                self.assertTrue(
                    any(
                        str(record.get("qualified_symbol") or "") == "Pixoneer.NXDL.NIO.XRasterIO.LoadFile"
                        for record in methods_index
                    ),
                    "compiled methods index should include XRasterIO.LoadFile",
                )
                self.assertTrue(workflow_index, "compiled workflow index should not be empty")
                workflow = workflow_index[0]
                self.assertEqual(workflow.get("path"), "workflows/wf-raster-load.md")
                self.assertIn("XRasterIO.LoadFile", workflow.get("required_symbols") or [])
                self.assertIn(
                    "Pixoneer.NXDL.NIO.XRasterIO.LoadFile",
                    workflow.get("linked_method_symbols") or [],
                )

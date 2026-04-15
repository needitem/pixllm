import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from backend.app.services.tools import doc_runtime
from backend.app.services.tools import runtime as tool_runtime
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


class DocRuntimeManifestFirstTests(unittest.IsolatedAsyncioTestCase):
    async def test_workflow_bundle_prefers_compiled_manifest_before_search_fallback(self):
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

            doc_runtime._read_wiki_manifest_cached.cache_clear()
            doc_runtime._load_methods_api_index_legacy.cache_clear()

            with patch("backend.app.services.tools.doc_runtime._wiki_root", side_effect=wiki_root), patch(
                "backend.app.services.tools.doc_runtime.search_wiki"
            ) as search_wiki_mock:
                bundle = doc_runtime._build_workflow_first_bundle(
                    query="How do I call XRasterIO.LoadFile to load raster data?",
                    top_k=8,
                    doc_open_limit=4,
                    max_chars=4000,
                    explicit_wiki_id="engine",
                )

            search_wiki_mock.assert_not_called()
            self.assertTrue(bundle.get("sources"), "manifest-first bundle should return wiki sources")
            self.assertEqual(bundle["sources"][0].get("file_path"), "workflows/wf-raster-load.md")
            self.assertIn(
                "methods/Methods_T_Pixoneer_NXDL_NIO_XRasterIO.md",
                bundle.get("slot_status", {}).get("method_paths") or [],
            )
            self.assertIn(
                "symbol:Pixoneer.NXDL.NIO.XRasterIO.LoadFile",
                bundle.get("slot_status", {}).get("required_slots") or [],
            )
            self.assertEqual(
                bundle.get("slot_status", {}).get("workflow_paths"),
                ["workflows/wf-raster-load.md"],
            )
            self.assertIn(
                "XRasterIO.LoadFile",
                bundle.get("slot_status", {}).get("required_symbols") or [],
            )
            self.assertIn(
                "use_this_workflow_as_primary_path",
                bundle.get("slot_status", {}).get("verification_rules") or [],
            )
            self.assertTrue(
                any(
                    str(item.get("symbol") or "") == "XRasterIO.LoadFile"
                    for item in (bundle.get("slot_status", {}).get("required_facts") or [])
                    if isinstance(item, dict)
                ),
                "workflow slot bundle should carry required facts for downstream prompt grounding",
            )


class DocRuntimeLookupTargetTests(unittest.TestCase):
    def test_extract_lookup_targets_ignores_csharp_language_marker(self):
        records = [
            {
                "type_name": "XRSLoadFile",
                "qualified_type": "Pixoneer.NXDL.NRS.XRSLoadFile",
                "member_name": "GetBandAt",
                "qualified_symbol": "Pixoneer.NXDL.NRS.XRSLoadFile.GetBandAt",
            }
        ]

        targets = doc_runtime._extract_lookup_targets(
            "XRSLoadFile GetBandAt C# signature",
            records,
        )

        self.assertEqual(targets.get("type_candidates"), ["XRSLoadFile"])
        self.assertIn("GetBandAt", targets.get("member_candidates") or [])
        self.assertNotIn("C", targets.get("member_candidates") or [])


class ToolRuntimeCodeEvidenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_collect_code_evidence_stops_after_enough_matches(self):
        first_matches = [
            {"path": "a.cs", "line_range": "10-10", "evidence_type": "implementation"},
            {"path": "b.cs", "line_range": "20-20", "evidence_type": "declaration"},
        ]
        search_code_mock = AsyncMock(
            side_effect=[
                {"matches": first_matches},
                {"matches": [{"path": "c.cs", "line_range": "30-30", "evidence_type": "implementation"}]},
            ]
        )

        with patch(
            "backend.app.services.tools.runtime.extract_symbol_query_candidates",
            return_value=["GetBandAt", "SetBand"],
        ), patch(
            "backend.app.services.tools.runtime.search_code",
            search_code_mock,
        ):
            result = await tool_runtime._collect_code_evidence_async(
                redis=None,
                session_id="session-1",
                query="XRSLoadFile GetBandAt C# signature",
                extra_query_candidates=["XRasterIO.LoadFile"],
                capped_limit=2,
                max_chars=4000,
                max_line_span=50,
                response_type="general",
                search_only=True,
                code_window_cap=8,
                code_tools=None,
            )

        self.assertEqual(result, [])
        self.assertEqual(search_code_mock.await_count, 1)

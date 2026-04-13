import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.tools import doc_runtime


class LookupSourcesAndCodeTests(unittest.IsolatedAsyncioTestCase):
    async def test_collect_sources_prefers_wiki_and_skips_doc_search_when_wiki_exists(self):
        wiki_rows = [
            {
                "chunk_id": "wiki:workflow#section-1",
                "doc_id": "wiki:workflow",
                "source_url": "workflows/imageview-xdm-display-workflow.md",
                "file_path": "workflows/imageview-xdm-display-workflow.md",
                "heading_path": "ImageView XDM Display Workflow > Verified Steps",
                "paragraph_range": "section:1",
                "text": "verified steps",
            }
        ]

        with patch.object(doc_runtime, "search_wiki", return_value={"results": wiki_rows, "chunks": wiki_rows}), \
             patch.object(doc_runtime, "search_docs", new=AsyncMock(side_effect=AssertionError("search_docs should not run when wiki results exist"))):
            sources = await doc_runtime.collect_sources(
                redis=None,
                search_svc=None,
                embed_model=None,
                session_id="sess",
                query="ImageView XDM load display",
                filters=None,
                top_k=5,
                doc_open_limit=5,
                max_chars=800,
                active_collection="documents",
                search_only=False,
            )

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["source_url"], "workflows/imageview-xdm-display-workflow.md")

    async def test_doc_lookup_stays_doc_only(self):
        sources = [
            {
                "chunk_id": "wiki:test#section-1",
                "doc_id": "wiki:test",
                "source_url": "methods/test.md",
                "heading_path": "Test > Overview",
                "paragraph_range": "section:1",
                "text": "overview",
            }
        ]
        collect_code = AsyncMock(return_value=({"matches": [], "limit": 5}, [], []))

        with patch.object(doc_runtime, "resolve_tool_user_context", new=AsyncMock(return_value={"session_id": "sess"})), \
             patch.object(doc_runtime, "collect_sources", new=AsyncMock(return_value=sources)):
            result = await doc_runtime.lookup_sources_and_code(
                redis=None,
                search_svc=None,
                embed_model=None,
                code_tools=None,
                session_id="sess",
                user_id=None,
                query="documentation only",
                filters=None,
                mode="auto",
                top_k=3,
                limit=5,
                max_chars=800,
                max_line_span=40,
                response_type="doc_lookup",
                search_only=False,
                collection=None,
                collect_code_evidence_async=collect_code,
            )

        self.assertEqual(result["query"], "documentation only")
        self.assertEqual(len(result["sources"]), 1)
        self.assertEqual(result["code_windows"], [])
        self.assertEqual(result["citations"][0]["kind"], "doc")
        collect_code.assert_not_awaited()

    async def test_general_query_uses_wiki_anchors_to_read_code(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "Source"
            header_path = source_root / "NXDLio" / "NXDLio.h"
            impl_path = source_root / "NXDLio" / "XRasterIO.cpp"
            header_path.parent.mkdir(parents=True, exist_ok=True)
            impl_path.parent.mkdir(parents=True, exist_ok=True)
            header_path.write_text("\n".join(f"header line {idx}" for idx in range(1, 240)), encoding="utf-8")
            impl_path.write_text("\n".join(f"impl line {idx}" for idx in range(1, 120)), encoding="utf-8")

            sources = [
                {
                    "chunk_id": "wiki:xrasterio#section-1",
                    "doc_id": "wiki:xrasterio",
                    "source_url": "methods/Methods_T_Pixoneer_NXDL_NIO_XRasterIO.md",
                    "heading_path": "Pixoneer.NXDL.NIO.XRasterIO Methods > Initialize",
                    "paragraph_range": "section:2",
                    "text": "\n".join(
                        [
                            "## Initialize",
                            "- Description: initialize io drivers.",
                            "- Declaration: `Source/NXDLio/NXDLio.h:198`",
                            "- Implementation: `Source/NXDLio/XRasterIO.cpp:72`",
                        ]
                    ),
                }
            ]
            collect_code = AsyncMock(return_value=({"matches": [], "limit": 5}, [], []))

            with patch.object(doc_runtime, "resolve_tool_user_context", new=AsyncMock(return_value={"session_id": "sess"})), \
                 patch.object(doc_runtime, "collect_sources", new=AsyncMock(return_value=sources)):
                result = await doc_runtime.lookup_sources_and_code(
                    redis=None,
                    search_svc=None,
                    embed_model=None,
                    code_tools=SimpleNamespace(configured_roots=[temp_dir]),
                    session_id="sess",
                    user_id=None,
                    query="How does XRasterIO.Initialize work?",
                    filters=None,
                    mode="auto",
                    top_k=3,
                    limit=5,
                    max_chars=800,
                    max_line_span=40,
                    response_type="general",
                    search_only=False,
                    collection=None,
                    collect_code_evidence_async=collect_code,
                )

        paths = {row.get("path") for row in result["code_windows"]}
        evidence_types = {row.get("evidence_type") for row in result["code_windows"]}
        self.assertIn("Source/NXDLio/NXDLio.h", paths)
        self.assertIn("Source/NXDLio/XRasterIO.cpp", paths)
        self.assertIn("declaration", evidence_types)
        self.assertIn("implementation", evidence_types)
        collect_code.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()

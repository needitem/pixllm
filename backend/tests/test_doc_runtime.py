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
            self.assertEqual(
                bundle.get("slot_status", {}).get("forbidden_answer_patterns"),
                [],
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

    def test_effective_lookup_response_type_downgrades_non_specific_workflow_guidance(self):
        methods_bundle = {
            "records": [
                {
                    "type_name": "NXImageView",
                    "qualified_type": "Pixoneer.NXDL.NXImage.NXImageView",
                    "member_name": "AddImageLayer",
                    "qualified_symbol": "Pixoneer.NXDL.NXImage.NXImageView.AddImageLayer",
                }
            ],
            "type_lookup": {
                "nximageview": "NXImageView",
                "pixoneernxdlnximagenximageview": "Pixoneer.NXDL.NXImage.NXImageView",
            },
            "record_lookup": {},
        }

        with patch(
            "backend.app.services.tools.doc_runtime._methods_lookup_bundle",
            return_value=methods_bundle,
        ):
            effective = doc_runtime._effective_lookup_response_type(
                query="c#에서 ImageView를 이용하여 XDM 파일 로드하여 화면에 도시하는 방법 알려줘",
                response_type="api_lookup",
                workflow_first=True,
                wiki_id="engine",
            )

        self.assertEqual(effective, "general")


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


class DocRuntimeLookupTimingTests(unittest.IsolatedAsyncioTestCase):
    async def test_collect_sources_uses_precomputed_workflow_bundle(self):
        precomputed_bundle = {
            "sources": [
                {
                    "file_path": "workflows/wf-raster-load.md",
                    "chunk_id": "wiki:engine:workflows/wf-raster-load.md#manifest",
                }
            ],
            "slot_status": {"slots_complete": True},
        }

        with patch(
            "backend.app.services.tools.doc_runtime._build_workflow_first_bundle",
            side_effect=AssertionError("workflow bundle should not be rebuilt"),
        ), patch(
            "backend.app.services.tools.doc_runtime.search_wiki",
            side_effect=AssertionError("search_wiki should not run when bundle sources exist"),
        ):
            sources = await doc_runtime.collect_sources(
                redis=None,
                search_svc=None,
                embed_model=None,
                session_id="session-1",
                query="How do I call XRasterIO.LoadFile to load raster data?",
                filters={"wiki_id": "engine"},
                top_k=8,
                doc_open_limit=4,
                max_chars=4000,
                active_collection="documents",
                search_only=True,
                response_type="api_lookup",
                workflow_first=True,
                workflow_bundle=precomputed_bundle,
            )

        self.assertEqual(sources, precomputed_bundle["sources"])

    async def test_lookup_sources_and_code_returns_timings_and_builds_workflow_bundle_once(self):
        workflow_bundle = {
            "sources": [
                {
                    "file_path": "workflows/wf-raster-load.md",
                    "chunk_id": "wiki:engine:workflows/wf-raster-load.md#manifest",
                }
            ],
            "slot_status": {"slots_complete": True},
        }
        collect_sources_mock = AsyncMock(return_value=workflow_bundle["sources"])
        collect_wiki_windows_mock = AsyncMock(return_value=[])
        collect_code_evidence_mock = AsyncMock(return_value=[])

        with patch(
            "backend.app.services.tools.doc_runtime.resolve_tool_user_context",
            AsyncMock(return_value={}),
        ), patch(
            "backend.app.services.tools.doc_runtime._build_workflow_first_bundle",
            return_value=workflow_bundle,
        ) as build_bundle_mock, patch(
            "backend.app.services.tools.doc_runtime.collect_sources",
            collect_sources_mock,
        ), patch(
            "backend.app.services.tools.doc_runtime.collect_wiki_anchor_code_windows",
            collect_wiki_windows_mock,
        ), patch(
            "backend.app.services.tools.doc_runtime.extract_doc_symbol_candidates",
            return_value=[],
        ), patch(
            "backend.app.services.tools.doc_runtime.build_citations",
            return_value=[],
        ):
            result = await doc_runtime.lookup_sources_and_code(
                redis=None,
                search_svc=None,
                embed_model=None,
                code_tools=None,
                session_id="session-1",
                user_id="user-1",
                query="How do I call XRasterIO.LoadFile to load raster data?",
                filters={"wiki_id": "engine"},
                top_k=8,
                limit=8,
                max_chars=4000,
                max_line_span=80,
                response_type="general",
                workflow_first=True,
                search_only=False,
                collection="documents",
                collect_code_evidence_async=collect_code_evidence_mock,
            )

        self.assertEqual(build_bundle_mock.call_count, 1)
        self.assertIs(collect_sources_mock.await_args.kwargs["workflow_bundle"], workflow_bundle)
        self.assertIn("build_workflow_bundle", result["timings_ms"])
        self.assertIn("collect_sources", result["timings_ms"])
        self.assertIn("total", result["timings_ms"])

    async def test_lookup_sources_and_code_skips_broad_code_evidence_when_workflow_anchors_are_strong(self):
        workflow_bundle = {
            "sources": [
                {
                    "file_path": "workflows/imageview-xdm-display-workflow.md",
                    "chunk_id": "wiki:engine:workflows/imageview-xdm-display-workflow.md#manifest",
                }
            ],
            "slot_status": {"slots_complete": True},
        }
        wiki_windows = [
            {"path": f"file{i}.cs", "line_range": f"{i}-{i}"}
            for i in range(1, 7)
        ]
        collect_code_evidence_mock = AsyncMock(side_effect=AssertionError("broad code evidence should be skipped"))

        with patch(
            "backend.app.services.tools.doc_runtime.resolve_tool_user_context",
            AsyncMock(return_value={}),
        ), patch(
            "backend.app.services.tools.doc_runtime._build_workflow_first_bundle",
            return_value=workflow_bundle,
        ), patch(
            "backend.app.services.tools.doc_runtime.collect_sources",
            AsyncMock(return_value=workflow_bundle["sources"]),
        ), patch(
            "backend.app.services.tools.doc_runtime.collect_wiki_anchor_code_windows",
            AsyncMock(return_value=wiki_windows),
        ), patch(
            "backend.app.services.tools.doc_runtime.extract_doc_symbol_candidates",
            return_value=["XRasterIO", "XRSLoadFile"],
        ), patch(
            "backend.app.services.tools.doc_runtime.build_citations",
            return_value=[],
        ):
            result = await doc_runtime.lookup_sources_and_code(
                redis=None,
                search_svc=None,
                embed_model=None,
                code_tools=None,
                session_id="session-1",
                user_id="user-1",
                query="c#에서 ImageView를 이용하여 XDM 파일 로드하여 화면에 도시하는 방법 알려줘",
                filters={"wiki_id": "engine"},
                top_k=8,
                limit=8,
                max_chars=4000,
                max_line_span=120,
                response_type="general",
                workflow_first=True,
                search_only=False,
                collection="documents",
                collect_code_evidence_async=collect_code_evidence_mock,
            )

        self.assertEqual(result["code_windows"], wiki_windows)
        self.assertEqual(result["timings_ms"]["collect_code_evidence"], 0.0)

    async def test_lookup_sources_and_code_downgrades_non_specific_api_lookup_for_workflow_guidance(self):
        workflow_bundle = {
            "sources": [
                {
                    "file_path": "workflows/imageview-xdm-display-workflow.md",
                    "chunk_id": "wiki:engine:workflows/imageview-xdm-display-workflow.md#manifest",
                }
            ],
            "slot_status": {"slots_complete": True},
        }
        wiki_windows = [
            {"path": f"file{i}.cs", "line_range": f"{i}-{i}"}
            for i in range(1, 7)
        ]
        collect_sources_mock = AsyncMock(return_value=workflow_bundle["sources"])
        collect_wiki_windows_mock = AsyncMock(return_value=wiki_windows)
        collect_code_evidence_mock = AsyncMock(side_effect=AssertionError("broad code evidence should be skipped"))

        with patch(
            "backend.app.services.tools.doc_runtime.resolve_tool_user_context",
            AsyncMock(return_value={}),
        ), patch(
            "backend.app.services.tools.doc_runtime._build_workflow_first_bundle",
            return_value=workflow_bundle,
        ), patch(
            "backend.app.services.tools.doc_runtime.collect_sources",
            collect_sources_mock,
        ), patch(
            "backend.app.services.tools.doc_runtime.collect_wiki_anchor_code_windows",
            collect_wiki_windows_mock,
        ), patch(
            "backend.app.services.tools.doc_runtime.extract_doc_symbol_candidates",
            return_value=["NXImageView", "XRasterIO"],
        ), patch(
            "backend.app.services.tools.doc_runtime.build_citations",
            return_value=[],
        ), patch(
            "backend.app.services.tools.doc_runtime._methods_lookup_bundle",
            return_value={
                "records": [
                    {
                        "type_name": "NXImageView",
                        "qualified_type": "Pixoneer.NXDL.NXImage.NXImageView",
                        "member_name": "AddImageLayer",
                        "qualified_symbol": "Pixoneer.NXDL.NXImage.NXImageView.AddImageLayer",
                    }
                ],
                "type_lookup": {
                    "nximageview": "NXImageView",
                    "pixoneernxdlnximagenximageview": "Pixoneer.NXDL.NXImage.NXImageView",
                },
                "record_lookup": {},
            },
        ):
            result = await doc_runtime.lookup_sources_and_code(
                redis=None,
                search_svc=None,
                embed_model=None,
                code_tools=None,
                session_id="session-1",
                user_id="user-1",
                query="c#에서 ImageView를 이용하여 XDM 파일 로드하여 화면에 도시하는 방법 알려줘",
                filters={"wiki_id": "engine"},
                top_k=8,
                limit=8,
                max_chars=4000,
                max_line_span=120,
                response_type="api_lookup",
                workflow_first=True,
                search_only=False,
                collection="documents",
                collect_code_evidence_async=collect_code_evidence_mock,
            )

        self.assertEqual(result["effective_response_type"], "general")
        self.assertEqual(result["code_windows"], wiki_windows)
        self.assertEqual(result["timings_ms"]["collect_code_evidence"], 0.0)
        self.assertEqual(collect_sources_mock.await_args.kwargs["response_type"], "general")
        self.assertEqual(collect_wiki_windows_mock.await_args.kwargs["response_type"], "general")

    def test_build_workflow_first_bundle_skips_method_matching_for_non_specific_lookup(self):
        workflow_bundle = {
            "records": [
                {
                    "path": "workflows/wf-raster-load.md",
                    "title": "Raster Load Workflow",
                    "content": WORKFLOW_PAGE,
                    "symbols": ["XRasterIO", "LoadFile"],
                    "required_symbols": ["XRasterIO.LoadFile"],
                    "tags": ["engine", "workflow"],
                    "required_facts": [
                        {
                            "symbol": "XRasterIO.LoadFile",
                            "declaration": "NRS::XRSLoadFile^ LoadFile(...);",
                            "source": "Source/NXDLio/NXDLio.h:230",
                        }
                    ],
                    "verification_rules": ["use_this_workflow_as_primary_path"],
                    "forbidden_answer_patterns": [],
                    "aliases": ["Load Raster"],
                    "route_terms": ["Raster Load Workflow", "XRasterIO", "LoadFile"],
                }
            ],
            "path_lookup": {
                "workflows/wf-raster-load.md": {
                    "path": "workflows/wf-raster-load.md",
                    "title": "Raster Load Workflow",
                    "content": WORKFLOW_PAGE,
                    "symbols": ["XRasterIO", "LoadFile"],
                    "required_symbols": ["XRasterIO.LoadFile"],
                    "tags": ["engine", "workflow"],
                    "required_facts": [
                        {
                            "symbol": "XRasterIO.LoadFile",
                            "declaration": "NRS::XRSLoadFile^ LoadFile(...);",
                            "source": "Source/NXDLio/NXDLio.h:230",
                        }
                    ],
                    "verification_rules": ["use_this_workflow_as_primary_path"],
                    "forbidden_answer_patterns": [],
                    "aliases": ["Load Raster"],
                    "route_terms": ["Raster Load Workflow", "XRasterIO", "LoadFile"],
                }
            },
            "search_entries": [
                {
                    "record": {
                        "path": "workflows/wf-raster-load.md",
                        "title": "Raster Load Workflow",
                        "content": WORKFLOW_PAGE,
                        "symbols": ["XRasterIO", "LoadFile"],
                        "required_symbols": ["XRasterIO.LoadFile"],
                        "tags": ["engine", "workflow"],
                        "required_facts": [
                            {
                                "symbol": "XRasterIO.LoadFile",
                                "declaration": "NRS::XRSLoadFile^ LoadFile(...);",
                                "source": "Source/NXDLio/NXDLio.h:230",
                            }
                        ],
                        "verification_rules": ["use_this_workflow_as_primary_path"],
                        "forbidden_answer_patterns": [],
                        "aliases": ["Load Raster"],
                        "route_terms": ["Raster Load Workflow", "XRasterIO", "LoadFile"],
                    }
                }
            ],
            "generated_at": "2026-01-01T00:00:00Z",
        }
        methods_bundle = {
            "records": [],
            "type_lookup": {},
            "record_lookup": {},
        }

        with patch(
            "backend.app.services.tools.doc_runtime._workflow_lookup_bundle",
            return_value=workflow_bundle,
        ), patch(
            "backend.app.services.tools.doc_runtime._methods_lookup_bundle",
            return_value=methods_bundle,
        ), patch(
            "backend.app.services.tools.doc_runtime._match_method_records_from_candidates",
            side_effect=AssertionError("method matching should not run for non-specific workflow guidance"),
        ):
            bundle = doc_runtime._build_workflow_first_bundle(
                query="How do I load raster data?",
                top_k=8,
                doc_open_limit=4,
                max_chars=4000,
                explicit_wiki_id="engine",
            )

        self.assertEqual(bundle["slot_status"]["required_slots"], ["workflow", "method_or_anchor"])


class DocRuntimeAnchorBudgetTests(unittest.TestCase):
    def test_wiki_anchor_window_budget_limits_general_workflow_only_queries(self):
        budget = doc_runtime.wiki_anchor_window_budget(
            doc_chunks=[{"file_path": "workflows/imageview-xdm-display-workflow.md"}],
            response_type="general",
            code_window_cap=12,
        )

        self.assertEqual(budget, 6)

    def test_wiki_anchor_window_budget_keeps_api_lookup_capacity(self):
        budget = doc_runtime.wiki_anchor_window_budget(
            doc_chunks=[{"file_path": "workflows/imageview-xdm-display-workflow.md"}],
            response_type="api_lookup",
            code_window_cap=12,
        )

        self.assertEqual(budget, 12)

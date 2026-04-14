import unittest

from backend.app.services.tools.doc_runtime import (
    build_exact_api_lookup_summary,
    extract_doc_symbol_candidates,
    prioritize_wiki_source_anchors,
    windows_overlap_strongly,
)


class DocRuntimeSelectionTests(unittest.TestCase):
    def test_extract_doc_symbol_candidates_prefers_workflow_symbols(self):
        doc_chunks = [
            {
                "symbols": [
                    "NXImageView",
                    "NXImageLayerComposites",
                    "XRasterIO",
                    "XRSLoadFile",
                    "XDMComposite",
                    "XDMCompManager",
                    "AddImageLayer",
                ],
                "text": (
                    "- `XRasterIO.Initialize` -> `Source/NXDLio/NXDLio.h:198`\n"
                    "- `XDMCompManager.AddXDMComposite` -> `Source/NXDLrs/XDMCompManager.cpp:68`\n"
                ),
            }
        ]
        candidates = extract_doc_symbol_candidates(doc_chunks, max_candidates=8)
        self.assertEqual(
            candidates[:6],
            [
                "NXImageView",
                "NXImageLayerComposites",
                "XRasterIO",
                "XRSLoadFile",
                "XDMComposite",
                "XDMCompManager",
            ],
        )

    def test_prioritize_wiki_source_anchors_prefers_unique_symbols_before_duplicates(self):
        anchors = [
            {
                "path": "Source/NXImage/NXImageLayerComposites.h",
                "line_range": "122-122",
                "symbols": ["NXImageLayerComposites"],
                "_chunk_index": 0,
                "_line_index": 0,
                "evidence_type": "reference",
            },
            {
                "path": "Source/NXImage/NXImageLayerComposites.cpp",
                "line_range": "56-56",
                "symbols": ["NXImageLayerComposites"],
                "_chunk_index": 0,
                "_line_index": 1,
                "evidence_type": "reference",
            },
            {
                "path": "Source/NXDLrs/XDMComposite.cpp",
                "line_range": "81-81",
                "symbols": ["XDMComposite"],
                "_chunk_index": 1,
                "_line_index": 0,
                "evidence_type": "reference",
            },
            {
                "path": "Source/NXDLrs/XDMCompManager.cpp",
                "line_range": "68-68",
                "symbols": ["XDMCompManager"],
                "_chunk_index": 1,
                "_line_index": 1,
                "evidence_type": "reference",
            },
        ]
        ordered = prioritize_wiki_source_anchors(anchors, max_candidates=4)
        ordered_symbols = [tuple(item.get("symbols") or []) for item in ordered[:3]]
        self.assertIn(("XDMComposite",), ordered_symbols)
        self.assertIn(("XDMCompManager",), ordered_symbols)

    def test_windows_overlap_strongly_detects_near_duplicate_ranges(self):
        existing = [{"path": "nxdl/source/NXDLio/NXDLio.h", "line_range": "163-233"}]
        candidate = {"path": "nxdl/source/NXDLio/NXDLio.h", "line_range": "187-257"}
        self.assertTrue(windows_overlap_strongly(existing, candidate))

    def test_exact_api_lookup_summary_reports_exact_match(self):
        summary = build_exact_api_lookup_summary("NXImageView AddImageLayer method signature")
        self.assertIsNotNone(summary)
        self.assertEqual(summary["status"], "exact_match")
        self.assertEqual(summary["matched_api"]["qualified_symbol"], "Pixoneer.NXDL.NXImage.NXImageView.AddImageLayer")

    def test_exact_api_lookup_summary_reports_no_exact_match_with_related_api(self):
        summary = build_exact_api_lookup_summary("XRSLoadFile Load method signature bool string")
        self.assertIsNotNone(summary)
        self.assertEqual(summary["status"], "no_exact_match")
        related_symbols = [item["qualified_symbol"] for item in summary["related_apis"]]
        self.assertIn("Pixoneer.NXDL.NIO.XRasterIO.LoadFile", related_symbols)
        self.assertIn("No exact verified API match found", summary["negative_evidence"])


if __name__ == "__main__":
    unittest.main()

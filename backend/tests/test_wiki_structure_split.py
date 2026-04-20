import json
import tempfile
import unittest
from pathlib import Path

from app.services.wiki.methods_index import (
    METHODS_INDEX_RELATIVE_PATH,
    build_methods_index_from_raw_source,
    build_method_chunk_results_for_root,
    build_method_page_results_for_root,
    load_methods_index_for_root,
    methods_index_file_for_root,
)
from app.services.wiki.service import _build_runtime_manifest


class WikiStructureSplitTests(unittest.TestCase):
    def test_build_methods_index_from_raw_source_extracts_public_methods(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw_root = Path(tmp)
            header_dir = raw_root / "NXDLio"
            cpp_dir = raw_root / "NXDLio"
            header_dir.mkdir(parents=True, exist_ok=True)
            cpp_dir.mkdir(parents=True, exist_ok=True)

            (header_dir / "NXDLio.h").write_bytes(
                "\n".join(
                    [
                        "namespace Pixoneer",
                        "{",
                        "namespace NXDL",
                        "{",
                        "namespace NIO",
                        "{",
                        "public ref class XRasterIO",
                        "{",
                        "public:",
                        "    /// <summary> Initialize 클래스 요약 </summary>",
                        "    bool Initialize([OutAttribute] String^% strError);",
                        "    /// <summary> LoadFile 클래스 요약 </summary>",
                        "    NRS::XRSLoadFile^ LoadFile(String^ strFileName, [OutAttribute] String^% strError, bool bCalcStatistics, eIOCreateXLDMode CreateXLD);",
                        "private:",
                        "    void Hidden();",
                        "};",
                        "}",
                        "}",
                        "}",
                    ]
                ).encode("cp949"),
            )
            (cpp_dir / "XRasterIO.cpp").write_text(
                "\n".join(
                    [
                        "bool XRasterIO::Initialize([OutAttribute] String^% strError)",
                        "{",
                        "    return true;",
                        "}",
                        "NRS::XRSLoadFile^ XRasterIO::LoadFile(String^ strFileName, [OutAttribute] String^% strError, bool bCalcStatistics, eIOCreateXLDMode CreateXLD)",
                        "{",
                        "    return nullptr;",
                        "}",
                    ]
                ),
                encoding="utf-8",
            )

            records = build_methods_index_from_raw_source(raw_root)
            symbols = [record["qualified_symbol"] for record in records]

            self.assertIn("Pixoneer.NXDL.NIO.XRasterIO.Initialize", symbols)
            self.assertIn("Pixoneer.NXDL.NIO.XRasterIO.LoadFile", symbols)
            self.assertNotIn("Pixoneer.NXDL.NIO.XRasterIO.Hidden", symbols)
            initialize_record = next(record for record in records if record["member_name"] == "Initialize")
            self.assertIn("클래스 요약", initialize_record["text"])

    def test_runtime_manifest_keeps_workflow_links_without_embedding_methods_index(self):
        workflow_page = {
            "path": "workflows/wf-api-raster.md",
            "kind": "workflow",
            "title": "Raster and XDM API Workflow",
            "summary": "Load raster data.",
            "content": "\n".join(
                [
                    "---",
                    "title: Raster and XDM API Workflow",
                    "symbols:",
                    "  - XRasterIO",
                    "---",
                    "",
                    "# Overview",
                    "- Goal: load raster data",
                    "",
                    "## Required Facts",
                    "```yaml",
                    "required_symbols:",
                    "  - XRasterIO.Initialize",
                    "```",
                    "",
                    "## Knowledge Bundle",
                    "```yaml",
                    "concept_terms:",
                    "  - band",
                    "routing_hints:",
                    "  - all_of: [raster, load]",
                    "bundle_pages:",
                    "  - path: pages/howtos/raster-load-and-composite.md",
                    "    relation: family_howto",
                    "```",
                ]
            ),
        }
        methods_index = [
            {
                "qualified_type": "Pixoneer.NXDL.NIO.XRasterIO",
                "type_name": "XRasterIO",
                "member_name": "Initialize",
                "qualified_symbol": "Pixoneer.NXDL.NIO.XRasterIO.Initialize",
                "heading_path": "Pixoneer.NXDL.NIO.XRasterIO Methods > Initialize",
                "text": "## Initialize\n- Declaration: `Source/NXDLio/NXDLio.h:198`",
                "source_refs": [],
            }
        ]

        manifest = _build_runtime_manifest(Path.cwd(), [workflow_page], methods_index)

        self.assertNotIn("methods_index", manifest)
        self.assertNotIn("required_output_files", manifest["workflow_index"][0])
        self.assertEqual(
            ["Pixoneer.NXDL.NIO.XRasterIO.Initialize"],
            manifest["workflow_index"][0]["linked_method_symbols"],
        )
        self.assertEqual(
            [{"path": "pages/howtos/raster-load-and-composite.md", "relation": "family_howto"}],
            manifest["workflow_index"][0]["bundle_pages"],
        )
        self.assertEqual(["band"], manifest["workflow_index"][0]["concept_terms"])
        self.assertEqual([{"all_of": ["raster", "load"], "any_of": []}], manifest["workflow_index"][0]["routing_hints"])
        self.assertIn("Load raster data.", manifest["workflow_index"][0]["semantic_terms"])

    def test_runtime_methods_index_serves_search_without_method_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index_file = methods_index_file_for_root(root)
            index_file.parent.mkdir(parents=True, exist_ok=True)
            payload = [
                {
                    "qualified_type": "Pixoneer.NXDL.NIO.XRasterIO",
                    "type_name": "XRasterIO",
                    "member_name": "Initialize",
                    "qualified_symbol": "Pixoneer.NXDL.NIO.XRasterIO.Initialize",
                    "heading_path": "Pixoneer.NXDL.NIO.XRasterIO Methods > Initialize",
                    "text": "## Initialize\n- Declaration: `Source/NXDLio/NXDLio.h:198`",
                    "source_refs": [],
                }
            ]
            index_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            loaded = load_methods_index_for_root(root)
            results = build_method_chunk_results_for_root(
                root,
                query="XRasterIO.Initialize method",
                top_k=5,
                max_chars=1200,
            )

            self.assertEqual(1, len(loaded))
            self.assertEqual(1, len(results))
            self.assertEqual(METHODS_INDEX_RELATIVE_PATH, results[0]["file_path"])
            self.assertTrue(str(results[0]["doc_id"]).endswith(":methods-index"))

    def test_search_pages_method_kind_uses_runtime_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index_file = methods_index_file_for_root(root)
            index_file.parent.mkdir(parents=True, exist_ok=True)
            payload = [
                {
                    "qualified_type": "Pixoneer.NXDL.NIO.XRasterIO",
                    "type_name": "XRasterIO",
                    "member_name": "Initialize",
                    "qualified_symbol": "Pixoneer.NXDL.NIO.XRasterIO.Initialize",
                    "heading_path": "Pixoneer.NXDL.NIO.XRasterIO Methods > Initialize",
                    "text": "## Initialize\n- Declaration: `Source/NXDLio/NXDLio.h:198`",
                    "source_refs": [],
                }
            ]
            index_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            page_results = build_method_page_results_for_root(
                root,
                query="XRasterIO.Initialize method",
                limit=5,
                include_content=False,
            )

            self.assertEqual(1, len(page_results))
            self.assertEqual(
                f"{METHODS_INDEX_RELATIVE_PATH}#Pixoneer.NXDL.NIO.XRasterIO.Initialize",
                page_results[0]["path"],
            )


if __name__ == "__main__":
    unittest.main()

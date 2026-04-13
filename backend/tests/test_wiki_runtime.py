import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.tools import doc_runtime, wiki_runtime


class WikiRuntimeTests(unittest.TestCase):
    def test_extract_wiki_source_anchors_accepts_workflow_docs(self):
        anchors = doc_runtime.extract_wiki_source_anchors(
            [
                {
                    "source_url": "workflows/imageview-xdm-display-workflow.md",
                    "heading_path": "ImageView XDM Display Workflow > Required Calls",
                    "text": "- Load the file: `XRasterIO.LoadFile` -> `Source/NXDLio/NXDLio.h:222`, `Source/NXDLio/XRasterIO.cpp:137`",
                }
            ]
        )

        paths = {item["path"] for item in anchors}
        evidence = {item["evidence_type"] for item in anchors}
        self.assertIn("Source/NXDLio/NXDLio.h", paths)
        self.assertIn("Source/NXDLio/XRasterIO.cpp", paths)
        self.assertIn("reference", evidence)

    def test_workflow_page_ranks_above_methods_for_task_query(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "methods").mkdir(parents=True, exist_ok=True)
            (root / "workflows").mkdir(parents=True, exist_ok=True)

            (root / "methods" / "Methods_T_Pixoneer_NXDL_NXImage_NXImageView.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    title: Pixoneer.NXDL.NXImage.NXImageView Methods
                    aliases:
                      - NXImageView Methods
                    symbols:
                      - NXImageView
                      - AddImageLayer
                    tags:
                      - methods
                      - imageview
                    ---

                    # AddImageLayer
                    - Description: add image layer.
                    - Declaration: `Source/NXImage/NXImageView.h:836`
                    """
                ),
                encoding="utf-8",
            )

            (root / "workflows" / "imageview-xdm-display-workflow.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    title: ImageView XDM Display Workflow
                    aliases:
                      - NXImageView XDM display C#
                      - c#으로 ImageView를 이용하여 XDM 파일 로드하여 화면에 도시
                    symbols:
                      - NXImageView
                      - XRasterIO
                      - AddImageLayer
                      - LoadFile
                    tags:
                      - workflow
                      - imageview
                      - xdm
                      - csharp
                    ---

                    # Minimal Program
                    - Build a program that loads an XDM file, adds the composite layer, and refreshes the view.
                    - Declaration: `Source/NXImage/NXImageView.h:836`
                    - Declaration: `Source/NXDLio/NXDLio.h:222`
                    """
                ),
                encoding="utf-8",
            )

            with patch.object(wiki_runtime, "wiki_root", return_value=root):
                result = wiki_runtime.search_wiki(
                    query="c#으로 ImageView를 이용하여 XDM 파일 로드하여 화면에 도시하는 프로그램 만들어줘",
                    top_k=5,
                    max_chars=1000,
                )

        self.assertGreater(len(result["results"]), 0)
        self.assertEqual(result["results"][0]["source_url"], "workflows/imageview-xdm-display-workflow.md")


if __name__ == "__main__":
    unittest.main()

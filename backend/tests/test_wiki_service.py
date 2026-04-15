import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.app.services.wiki.service import WikiService


class WikiServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_context_bootstraps_coordination_files_for_existing_generated_wiki(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            backend_root = Path(temp_dir)
            wiki_root = backend_root / ".profiles" / "wiki" / "engine"
            (wiki_root / "methods").mkdir(parents=True, exist_ok=True)
            (wiki_root / "01-method-wiki-index.md").write_text("# Generated Index\n", encoding="utf-8")
            (wiki_root / "methods" / "Sample.md").write_text("# Sample Method\n", encoding="utf-8")

            with patch("backend.app.services.wiki.service._BACKEND_ROOT", backend_root):
                service = WikiService()
                context = await service.get_context("engine")

            coordination = context["coordination_status"]
            created_paths = set(coordination["created_paths"])

            self.assertTrue(coordination["auto_bootstrapped"])
            self.assertTrue(coordination["has_coordination_spine"])
            self.assertTrue(
                {
                    "README.md",
                    "SCHEMA.md",
                    "index.md",
                    "log.md",
                    "pages/home.md",
                }.issubset(created_paths)
            )
            self.assertIn("01-method-wiki-index.md", coordination["present_paths"])

            for expected in ("README.md", "SCHEMA.md", "index.md", "log.md", "pages/home.md"):
                self.assertTrue((wiki_root / expected).exists())

    async def test_get_context_initializes_new_wiki_with_core_spine(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            backend_root = Path(temp_dir)

            with patch("backend.app.services.wiki.service._BACKEND_ROOT", backend_root):
                service = WikiService()
                context = await service.get_context("project-alpha")

            coordination = context["coordination_status"]
            wiki_root = backend_root / ".profiles" / "wiki" / "project-alpha"

            self.assertTrue(coordination["auto_bootstrapped"])
            self.assertTrue(coordination["has_coordination_spine"])
            self.assertEqual(
                set(coordination["created_paths"]),
                {"README.md", "SCHEMA.md", "index.md", "log.md", "pages/home.md"},
            )
            self.assertTrue((wiki_root / "README.md").exists())
            self.assertTrue((wiki_root / "pages" / "home.md").exists())
            self.assertEqual(context["wiki"]["id"], "project-alpha")

    async def test_ingest_source_document_creates_raw_source_topic_and_updates_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            backend_root = Path(temp_dir)

            with patch("backend.app.services.wiki.service._BACKEND_ROOT", backend_root):
                service = WikiService()
                result = await service.ingest_source_document(
                    "project-alpha",
                    source_path="docs/alpha-overview.md",
                    raw_text="# Alpha Overview\n\n## Capabilities\n\nAlpha supports wiki-first ingestion.\n",
                    title="Alpha Overview",
                    project="project-alpha",
                    source_kind="imported_doc",
                    document_id="doc-1",
                    revision_id="rev-1",
                    content_hash="hash-1",
                    object_name="imports/project-alpha/job-1/docs/alpha-overview.md",
                    imported_at="2026-04-15T00:00:00Z",
                )

                wiki_root = backend_root / ".profiles" / "wiki" / "project-alpha"
                index_text = (wiki_root / "index.md").read_text(encoding="utf-8")
                log_text = (wiki_root / "log.md").read_text(encoding="utf-8")

            self.assertTrue((wiki_root / "raw" / "processed" / "docs" / "alpha-overview.md.source.md").exists())
            self.assertTrue((wiki_root / "pages" / "sources" / "alpha-overview.md").exists())
            self.assertTrue((wiki_root / "pages" / "topics" / "alpha-overview.md").exists())
            self.assertEqual(result["source_page"]["path"], "pages/sources/alpha-overview.md")
            self.assertIn("pages/sources/alpha-overview.md", index_text)
            self.assertIn("pages/topics/alpha-overview.md", index_text)
            self.assertIn("Ingest Alpha Overview", log_text)

    async def test_lint_wiki_reports_broken_links_and_missing_provenance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            backend_root = Path(temp_dir)

            with patch("backend.app.services.wiki.service._BACKEND_ROOT", backend_root):
                service = WikiService()
                await service.get_context("project-alpha")
                await service.write_page(
                    "project-alpha",
                    "pages/topics/broken.md",
                    "# Broken Topic\n\nSee [missing](../sources/does-not-exist.md).\n",
                )

                lint_result = await service.lint_wiki("project-alpha", repair=False)

            codes = {finding["code"] for finding in lint_result["findings"]}
            self.assertIn("broken_relative_link", codes)
            self.assertIn("missing_provenance", codes)


if __name__ == "__main__":
    unittest.main()

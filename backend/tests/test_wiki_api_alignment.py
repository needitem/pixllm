import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.wiki.methods_index import METHODS_INDEX_RELATIVE_PATH


class WikiApiAlignmentTests(unittest.TestCase):
    def test_rebuild_index_response_matches_generated_runtime_files(self):
        with TestClient(app) as client:
            response = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual("index.md", payload["data"]["path"])

        methods_index_path = Path(
            r"D:\Pixoneer_Source\PIX_RAG_Source\backend\.profiles\wiki\engine\.runtime\methods_index.json"
        )
        manifest_path = Path(
            r"D:\Pixoneer_Source\PIX_RAG_Source\backend\.profiles\wiki\engine\.runtime\manifest.json"
        )
        source_manifest_path = Path(
            r"D:\Pixoneer_Source\PIX_RAG_Source\backend\.profiles\wiki\engine\.runtime\source_manifest.json"
        )
        nxdlio_source_page = Path(
            r"D:\Pixoneer_Source\PIX_RAG_Source\backend\.profiles\wiki\engine\pages\sources\nxdlio.md"
        )
        self.assertTrue(methods_index_path.exists())
        self.assertTrue(manifest_path.exists())
        self.assertTrue(source_manifest_path.exists())
        self.assertTrue(nxdlio_source_page.exists())

        methods_index = json.loads(methods_index_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
        self.assertGreater(len(methods_index), 0)
        self.assertIn("workflow_index", manifest)
        self.assertNotIn("methods_index", manifest)
        self.assertGreater(source_manifest.get("module_count", 0), 0)

    def test_method_search_api_returns_runtime_index_backed_results(self):
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "XRasterIO.Initialize method",
                    "limit": 3,
                    "include_content": False,
                    "kind": "method",
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        data = payload["data"]
        self.assertGreaterEqual(data["total"], 1)
        first = data["results"][0]
        self.assertEqual("method", first["kind"])
        self.assertTrue(str(first["path"]).startswith(f"{METHODS_INDEX_RELATIVE_PATH}#"))
        self.assertIn("XRasterIO", first["title"])
        self.assertIn("excerpt", first)

    def test_workflow_page_read_returns_related_bundle_pages(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/page/read",
                json={
                    "wiki_id": "engine",
                    "path": "workflows/wf-api-imageview.md",
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        related_pages = payload["data"].get("related_pages") or []
        related_paths = {str(item.get("path") or "") for item in related_pages}
        self.assertTrue(all(".." not in path for path in related_paths))
        self.assertIn("pages/howtos/imageview-display-recipes.md", related_paths)
        self.assertIn("pages/concepts/layer-composite-display-pipeline.md", related_paths)
        self.assertIn("workflows/wf-api-raster.md", related_paths)
        self.assertIn("pages/sources/nximage.md", related_paths)

    def test_workflow_search_routes_coordinate_transform_by_manifest_terms(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "coordinate transform",
                    "limit": 5,
                    "include_content": False,
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        data = payload["data"]
        first = data["results"][0]
        self.assertEqual("workflows/wf-api-coordinate.md", first["path"])
        self.assertEqual("workflow", first["kind"])
        self.assertIn("rank", first)
        self.assertNotIn("score", first)

    def test_workflow_search_routes_raster_load_by_manifest_terms(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "raster load",
                    "limit": 5,
                    "include_content": False,
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        data = payload["data"]
        first = data["results"][0]
        self.assertEqual("workflows/wf-api-raster.md", first["path"])
        self.assertEqual("workflow", first["kind"])
        self.assertIn("rank", first)
        self.assertNotIn("score", first)

    def test_workflow_search_uses_bundle_semantics_for_grayscale_color_question(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "ImageView에서 입력한 파일 밴드 수에 따라 흑백 또는 칼라로 도시하는 방법 알려줘",
                    "limit": 5,
                    "include_content": False,
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        data = payload["data"]
        first = data["results"][0]
        self.assertEqual("workflows/wf-api-raster.md", first["path"])

    def test_workflow_search_routes_core_utils_alias_to_core_utils(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "license check",
                    "limit": 5,
                    "include_content": False,
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual("workflows/wf-api-core-utils.md", payload["data"]["results"][0]["path"])

    def test_workflow_search_routes_planet_group_registration_to_planetview(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "Planet 엔진에 PBI group을 등록하는 방법 알려줘",
                    "limit": 5,
                    "include_content": False,
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual("workflows/wf-api-planetview.md", payload["data"]["results"][0]["path"])

    def test_workflow_search_routes_imageview_video_layer_question_to_videoview(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "ImageView 비디오 레이어에 채널 연결하는 방법 알려줘",
                    "limit": 5,
                    "include_content": False,
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual("workflows/wf-api-videoview.md", payload["data"]["results"][0]["path"])

    def test_workflow_search_routes_scene_selection_clear_to_scene_editor(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "scene 선택을 모두 해제하는 방법 알려줘",
                    "limit": 5,
                    "include_content": False,
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual("workflows/wf-api-scene-editor.md", payload["data"]["results"][0]["path"])

    def test_workflow_search_routes_dfs_export_progress_to_dfs(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "DFS export 진행률을 확인하는 방법 알려줘",
                    "limit": 5,
                    "include_content": False,
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual("workflows/wf-api-dfs.md", payload["data"]["results"][0]["path"])

    def test_workflow_search_routes_imageview_comp_link_front_setting_to_imageview(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "합성 1 Front 설정하는 방법 알려줘",
                    "limit": 5,
                    "include_content": False,
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual("workflows/wf-api-imageview.md", payload["data"]["results"][0]["path"])

    def test_workflow_search_routes_image_center_map_coordinate_to_sensor_model(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "영상 중심점의 지도 좌표를 얻는 방법 알려줘",
                    "limit": 5,
                    "include_content": False,
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual("workflows/wf-api-sensor-model.md", payload["data"]["results"][0]["path"])

    def test_workflow_search_routes_space_to_world_to_uspaceview(self):
        with TestClient(app) as client:
            rebuild = client.post("/api/v1/wiki/index/rebuild", json={"wiki_id": "engine"})
            self.assertEqual(200, rebuild.status_code)
            response = client.post(
                "/api/v1/wiki/search",
                json={
                    "wiki_id": "engine",
                    "query": "공간 좌표를 world 좌표로 바꾸는 방법 알려줘",
                    "limit": 5,
                    "include_content": False,
                },
            )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual("workflows/wf-api-uspaceview.md", payload["data"]["results"][0]["path"])


if __name__ == "__main__":
    unittest.main()

import unittest

from app.main import app


class ApiSurfaceTests(unittest.TestCase):
    def test_api_surface_only_exposes_health_wiki_and_runs_prefixes(self):
        prefixes = set()
        api_paths = []

        for route in app.routes:
            path = getattr(route, "path", "")
            if not path.startswith("/api/v1/"):
                continue
            api_paths.append(path)
            suffix = path[len("/api/v1/") :]
            prefixes.add(suffix.split("/", 1)[0])

        self.assertEqual({"health", "wiki", "runs"}, prefixes)
        self.assertTrue(api_paths)
        self.assertFalse(any("tool-runtime" in path for path in api_paths))


if __name__ == "__main__":
    unittest.main()

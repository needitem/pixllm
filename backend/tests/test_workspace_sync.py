import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.app.services.tools import workspace_sync


class _FakeRedis:
    def __init__(self, mapping):
        self._mapping = mapping

    async def smembers(self, key):
        return self._mapping.get(key, set())

    async def get(self, key):
        return self._mapping.get(key)


class _FakeResponse:
    def __init__(self, data: bytes):
        self._data = data

    def read(self):
        return self._data

    def close(self):
        return None

    def release_conn(self):
        return None


class _FakeMinio:
    def __init__(self, data: bytes):
        self._data = data

    def get_object(self, bucket, object_name):
        return _FakeResponse(self._data)


class WorkspaceSyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_restore_retries_after_transient_filenotfound(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            import_root = Path(temp_dir)
            target_path = import_root / "project-a" / "nested" / "XDMBandMapConv.h"
            doc_id = "doc-1"
            revision_id = "rev-1"
            redis = _FakeRedis(
                {
                    "doc:index": {doc_id},
                    f"doc:{doc_id}": json.dumps(
                        {
                            "source_type": "import_code",
                            "project": "project-a",
                            "current_revision_id": revision_id,
                            "source_key": f"path::{target_path.as_posix()}",
                        }
                    ),
                    f"doc_rev:{revision_id}": json.dumps(
                        {
                            "source_file": "nested/XDMBandMapConv.h",
                            "content_hash": "",
                            "object_name": "obj-1",
                        }
                    ),
                }
            )
            minio = _FakeMinio(b"test-data")

            real_write_bytes = Path.write_bytes
            call_count = {"value": 0}

            def flaky_write_bytes(self, data):
                if self == target_path and call_count["value"] == 0:
                    call_count["value"] += 1
                    raise FileNotFoundError("transient write race")
                call_count["value"] += 1
                return real_write_bytes(self, data)

            with patch("pathlib.Path.write_bytes", new=flaky_write_bytes):
                result = await workspace_sync.restore_import_code_workspace(
                    redis,
                    minio,
                    "documents",
                    str(import_root),
                    overwrite=True,
                )

            self.assertEqual(result["restored"], 1)
            self.assertEqual(result["errors"], 0)
            self.assertTrue(target_path.exists())
            self.assertEqual(target_path.read_bytes(), b"test-data")

    async def test_restore_preserves_existing_file_when_write_raises_filenotfound(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            import_root = Path(temp_dir)
            target_path = import_root / "project-a" / "nested" / "XDMBandMapConv.h"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(b"existing-data")
            doc_id = "doc-1"
            revision_id = "rev-1"
            redis = _FakeRedis(
                {
                    "doc:index": {doc_id},
                    f"doc:{doc_id}": json.dumps(
                        {
                            "source_type": "import_code",
                            "project": "project-a",
                            "current_revision_id": revision_id,
                            "source_key": f"path::{target_path.as_posix()}",
                        }
                    ),
                    f"doc_rev:{revision_id}": json.dumps(
                        {
                            "source_file": "nested/XDMBandMapConv.h",
                            "content_hash": "",
                            "object_name": "obj-1",
                        }
                    ),
                }
            )
            minio = _FakeMinio(b"new-data")

            def always_missing(self, data):
                if self == target_path:
                    raise FileNotFoundError("mounted overwrite failure")
                return Path.write_bytes(self, data)

            with patch("pathlib.Path.write_bytes", new=always_missing):
                result = await workspace_sync.restore_import_code_workspace(
                    redis,
                    minio,
                    "documents",
                    str(import_root),
                    overwrite=True,
                )

            self.assertEqual(result["restored"], 0)
            self.assertEqual(result["skipped"], 1)
            self.assertEqual(result["errors"], 0)
            self.assertEqual(target_path.read_bytes(), b"existing-data")

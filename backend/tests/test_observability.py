import os
import re
import sys
import unittest


BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.observability import (  # noqa: E402
    build_request_log,
    make_test_request,
    normalize_request_id,
    request_id_headers,
)


class ObservabilityTests(unittest.TestCase):
    def test_normalize_request_id_sanitizes_and_truncates(self):
        normalized = normalize_request_id("  team/audit request?#1  ")

        self.assertEqual(normalized, "team-audit-request-1")
        self.assertLessEqual(len(normalized), 128)

    def test_normalize_request_id_generates_id_for_empty_values(self):
        normalized = normalize_request_id("")

        self.assertRegex(normalized, r"^[a-f0-9]{32}$")

    def test_build_request_log_uses_request_context_and_session_kind(self):
        request = make_test_request(
            method="POST",
            path="/api/v1/runs",
            query="page=1",
            request_id="req-123",
            user_agent="desktop-test",
            client_ip="10.0.0.8",
        )

        payload = build_request_log(
            request,
            status_code=202,
            duration_ms=18.345,
            api_session={"kind": "issued"},
        )

        self.assertEqual(payload["event"], "http_request")
        self.assertEqual(payload["request_id"], "req-123")
        self.assertEqual(payload["method"], "POST")
        self.assertEqual(payload["path"], "/api/v1/runs")
        self.assertEqual(payload["query"], "page=1")
        self.assertEqual(payload["status_code"], 202)
        self.assertEqual(payload["duration_ms"], 18.34)
        self.assertEqual(payload["client_ip"], "10.0.0.8")
        self.assertEqual(payload["user_agent"], "desktop-test")
        self.assertEqual(payload["api_session_kind"], "issued")

    def test_request_id_headers_returns_propagation_header(self):
        request = make_test_request(request_id="trace-42")

        headers = request_id_headers(request)

        self.assertEqual(headers, {"X-Request-ID": "trace-42"})


if __name__ == "__main__":
    unittest.main()

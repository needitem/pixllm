import os
import sys
import unittest


BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.metrics import MetricsRegistry, render_health_metrics  # noqa: E402


class MetricsTests(unittest.TestCase):
    def test_registry_renders_http_counters_histograms_and_scrapes(self):
        registry = MetricsRegistry()
        registry.record_http_request(
            method="GET",
            path="/api/v1/health",
            status_code=200,
            duration_ms=42.5,
        )
        registry.record_http_request(
            method="POST",
            path="/api/v1/runs",
            status_code=500,
            duration_ms=510.0,
        )
        registry.record_exception(
            method="POST",
            path="/api/v1/runs",
            error_type="RuntimeError",
        )
        registry.record_scrape()

        payload = registry.render_prometheus()

        self.assertIn("pixllm_process_uptime_seconds", payload)
        self.assertIn('pixllm_metrics_scrapes_total{service="api"} 1', payload)
        self.assertIn('pixllm_http_requests_total{method="GET",path="/api/v1/health",status_code="200"} 1', payload)
        self.assertIn('pixllm_http_errors_total{method="POST",path="/api/v1/runs",status_code="500"} 1', payload)
        self.assertIn('pixllm_http_exceptions_total{error_type="RuntimeError",method="POST",path="/api/v1/runs"} 1', payload)
        self.assertIn('pixllm_http_request_duration_ms_count{method="GET",path="/api/v1/health"} 1', payload)
        self.assertIn('pixllm_http_request_duration_ms_bucket{le="+Inf",method="POST",path="/api/v1/runs"} 1', payload)

    def test_render_health_metrics_includes_overall_readiness_and_components(self):
        payload = render_health_metrics({
            "status": "degraded",
            "ready": False,
            "components": {
                "redis": {"status": "ok"},
                "llm": {"status": "error"},
            },
        })

        joined = "\n".join(payload)
        self.assertIn('pixllm_health_status{service="api"} 0', joined)
        self.assertIn('pixllm_readiness_status{service="api"} 0', joined)
        self.assertIn('pixllm_health_component_status{component="redis"} 1', joined)
        self.assertIn('pixllm_health_component_status{component="llm"} 0', joined)


if __name__ == "__main__":
    unittest.main()

import threading
import time
from collections import defaultdict


HTTP_DURATION_BUCKETS_MS = (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000)


def _escape_label(value) -> str:
    text = str(value or "")
    return text.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def _labels_to_text(labels: dict[str, str]) -> str:
    if not labels:
        return ""
    serialized = ",".join(
        f'{key}="{_escape_label(value)}"'
        for key, value in sorted(labels.items())
    )
    return f"{{{serialized}}}"


def metric_path_label(request) -> str:
    scope = getattr(request, "scope", {}) or {}
    route = scope.get("route")
    route_path = str(getattr(route, "path", "") or "").strip()
    if route_path:
        return route_path
    url = getattr(request, "url", None)
    return str(getattr(url, "path", "") or "")


def _status_value(status: str) -> int:
    normalized = str(status or "").strip().lower()
    return 1 if normalized in {"ok", "ready", "disabled"} else 0


def render_health_metrics(health_payload: dict | None = None) -> list[str]:
    payload = health_payload if isinstance(health_payload, dict) else {}
    components = payload.get("components") if isinstance(payload.get("components"), dict) else {}
    lines = [
        "# HELP pixllm_health_status Overall service health status. 1 means healthy, 0 means degraded.",
        "# TYPE pixllm_health_status gauge",
        f'pixllm_health_status{_labels_to_text({"service": "api"})} {_status_value(payload.get("status") or "")}',
    ]
    if "ready" in payload:
        lines.extend([
            "# HELP pixllm_readiness_status Readiness state. 1 means ready to serve, 0 means not ready.",
            "# TYPE pixllm_readiness_status gauge",
            f'pixllm_readiness_status{_labels_to_text({"service": "api"})} {1 if bool(payload.get("ready")) else 0}',
        ])
    if components:
        lines.extend([
            "# HELP pixllm_health_component_status Health state by component. 1 means healthy, 0 means unhealthy.",
            "# TYPE pixllm_health_component_status gauge",
        ])
        for component, data in sorted(components.items()):
            status = ""
            if isinstance(data, dict):
                status = str(data.get("status") or "")
            lines.append(
                f'pixllm_health_component_status{_labels_to_text({"component": component})} {_status_value(status)}'
            )
    return lines


class MetricsRegistry:
    def __init__(self):
        self._lock = threading.Lock()
        self._started_at = time.time()
        self._http_requests = defaultdict(int)
        self._http_errors = defaultdict(int)
        self._http_duration_buckets = defaultdict(lambda: [0] * len(HTTP_DURATION_BUCKETS_MS))
        self._http_duration_sum_ms = defaultdict(float)
        self._http_duration_count = defaultdict(int)
        self._http_exceptions = defaultdict(int)
        self._scrapes_total = 0

    def record_http_request(self, *, method: str, path: str, status_code: int, duration_ms: float) -> None:
        request_key = (str(method or "").upper(), str(path or ""), str(int(status_code)))
        latency_key = (str(method or "").upper(), str(path or ""))
        with self._lock:
            self._http_requests[request_key] += 1
            if int(status_code) >= 400:
                self._http_errors[request_key] += 1
            self._http_duration_sum_ms[latency_key] += float(duration_ms)
            self._http_duration_count[latency_key] += 1
            for index, bucket in enumerate(HTTP_DURATION_BUCKETS_MS):
                if float(duration_ms) <= bucket:
                    self._http_duration_buckets[latency_key][index] += 1

    def record_exception(self, *, method: str, path: str, error_type: str) -> None:
        key = (str(method or "").upper(), str(path or ""), str(error_type or "Exception"))
        with self._lock:
            self._http_exceptions[key] += 1

    def record_scrape(self) -> None:
        with self._lock:
            self._scrapes_total += 1

    def render_prometheus(self, *, extra_lines: list[str] | None = None) -> str:
        with self._lock:
            http_requests = dict(self._http_requests)
            http_errors = dict(self._http_errors)
            http_duration_buckets = {
                key: list(values)
                for key, values in self._http_duration_buckets.items()
            }
            http_duration_sum_ms = dict(self._http_duration_sum_ms)
            http_duration_count = dict(self._http_duration_count)
            http_exceptions = dict(self._http_exceptions)
            scrapes_total = self._scrapes_total
            uptime_seconds = max(0.0, time.time() - self._started_at)

        lines = [
            "# HELP pixllm_process_uptime_seconds Process uptime in seconds.",
            "# TYPE pixllm_process_uptime_seconds gauge",
            f'pixllm_process_uptime_seconds{_labels_to_text({"service": "api"})} {uptime_seconds:.3f}',
            "# HELP pixllm_metrics_scrapes_total Number of Prometheus scrape requests served.",
            "# TYPE pixllm_metrics_scrapes_total counter",
            f'pixllm_metrics_scrapes_total{_labels_to_text({"service": "api"})} {scrapes_total}',
            "# HELP pixllm_http_requests_total Total HTTP requests processed.",
            "# TYPE pixllm_http_requests_total counter",
        ]

        for (method, path, status_code), value in sorted(http_requests.items()):
            labels = _labels_to_text({
                "method": method,
                "path": path,
                "status_code": status_code,
            })
            lines.append(f"pixllm_http_requests_total{labels} {value}")

        lines.extend([
            "# HELP pixllm_http_errors_total Total HTTP error responses with status >= 400.",
            "# TYPE pixllm_http_errors_total counter",
        ])
        for (method, path, status_code), value in sorted(http_errors.items()):
            labels = _labels_to_text({
                "method": method,
                "path": path,
                "status_code": status_code,
            })
            lines.append(f"pixllm_http_errors_total{labels} {value}")

        lines.extend([
            "# HELP pixllm_http_exceptions_total Total exceptions observed while handling requests.",
            "# TYPE pixllm_http_exceptions_total counter",
        ])
        for (method, path, error_type), value in sorted(http_exceptions.items()):
            labels = _labels_to_text({
                "method": method,
                "path": path,
                "error_type": error_type,
            })
            lines.append(f"pixllm_http_exceptions_total{labels} {value}")

        lines.extend([
            "# HELP pixllm_http_request_duration_ms HTTP request latency in milliseconds.",
            "# TYPE pixllm_http_request_duration_ms histogram",
        ])
        for (method, path), buckets in sorted(http_duration_buckets.items()):
            labels = {"method": method, "path": path}
            cumulative = 0
            for index, bucket in enumerate(HTTP_DURATION_BUCKETS_MS):
                cumulative += buckets[index]
                bucket_labels = _labels_to_text({**labels, "le": str(bucket)})
                lines.append(f"pixllm_http_request_duration_ms_bucket{bucket_labels} {cumulative}")
            count = http_duration_count.get((method, path), 0)
            inf_labels = _labels_to_text({**labels, "le": "+Inf"})
            lines.append(f"pixllm_http_request_duration_ms_bucket{inf_labels} {count}")
            base_labels = _labels_to_text(labels)
            lines.append(f"pixllm_http_request_duration_ms_sum{base_labels} {http_duration_sum_ms.get((method, path), 0.0):.3f}")
            lines.append(f"pixllm_http_request_duration_ms_count{base_labels} {count}")

        if extra_lines:
            lines.extend(extra_lines)

        return "\n".join(lines) + "\n"


metrics_registry = MetricsRegistry()

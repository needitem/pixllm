#!/usr/bin/env python3
"""validate_code_mode_meta.py — 코드 모드 메타 등록 규칙 검증 스크립트.

Redis에 저장된 모든 import job을 조회하여 mode=code 인 작업에 대해
embedded_chunks == 0 AND total_chunks == 0 규칙이 지켜지는지 확인합니다.
위반 항목은 콘솔에 출력되며 종료 코드로 결과를 알립니다.

사용 예:
    python scripts/validate_code_mode_meta.py
    python scripts/validate_code_mode_meta.py --redis-url redis://localhost:6379
    python scripts/validate_code_mode_meta.py --dry-run   # Redis 없이 mock 데이터로 실행

종료 코드:
    0 — 모든 항목 정상
    1 — 1개 이상의 위반 항목 발견
    2 — Redis 연결 실패 (--dry-run 없이 실행 시)
"""

import argparse
import json
import sys


# ---------------------------------------------------------------------------
# Mock data for --dry-run mode
# ---------------------------------------------------------------------------
_DRY_RUN_JOBS = [
    {"job_id": "dry-ok-1", "mode": "code", "status": "completed", "embedded_chunks": 0, "total_chunks": 0},
    {"job_id": "dry-ok-2", "mode": "docs", "status": "completed", "embedded_chunks": 5, "total_chunks": 5},
    {"job_id": "dry-fail-1", "mode": "code", "status": "completed", "embedded_chunks": 3, "total_chunks": 3},
]


def _parse_args():
    parser = argparse.ArgumentParser(description="코드 모드 메타 등록 규칙 검증")
    parser.add_argument("--redis-url", default="redis://localhost:6379", help="Redis 연결 URL")
    parser.add_argument("--dry-run", action="store_true", help="Redis 없이 mock 데이터로 실행")
    parser.add_argument("--include-failed", action="store_true", help="status=failed 인 잡도 포함하여 검사")
    return parser.parse_args()


def _check_job(job: dict, include_failed: bool) -> tuple[str, bool, str]:
    """Return (label, is_ok, reason)."""
    job_id = job.get("job_id", "<unknown>")
    mode = (job.get("mode") or "").strip().lower()
    status = (job.get("status") or "").strip().lower()

    if mode != "code":
        return job_id, True, "skip (not code mode)"

    # Optionally skip non-completed jobs
    if not include_failed and status in {"failed", "cancelled", "queued", "running"}:
        return job_id, True, f"skip (status={status})"

    embedded = int(job.get("embedded_chunks") or 0)
    total = int(job.get("total_chunks") or 0)

    if embedded == 0 and total == 0:
        return job_id, True, f"OK  mode=code  status={status}  embedded_chunks=0  total_chunks=0"
    return (
        job_id,
        False,
        f"VIOLATION  mode=code  status={status}  embedded_chunks={embedded}  total_chunks={total}",
    )


def _run_redis(redis_url: str, include_failed: bool):
    """Fetch all import jobs from Redis and validate."""
    try:
        import redis as _redis
    except ImportError:
        print("ERROR: 'redis' 패키지가 설치되지 않았습니다. pip install redis 를 실행해 주세요.", file=sys.stderr)
        return 2

    try:
        client = _redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=5)
        client.ping()
    except Exception as exc:
        print(f"ERROR: Redis 연결 실패 ({redis_url}): {exc}", file=sys.stderr)
        return 2

    index_key = "import_job:index"
    job_ids = client.smembers(index_key)
    if not job_ids:
        print("INFO: import 잡이 없습니다 (Redis 인덱스가 비어 있음).")
        return 0

    jobs = []
    for job_id in job_ids:
        raw = client.get(f"import_job:{job_id}")
        if raw:
            try:
                jobs.append(json.loads(raw))
            except json.JSONDecodeError:
                print(f"WARN: job {job_id} JSON 파싱 실패, 건너뜁니다.", file=sys.stderr)

    return _report(jobs, include_failed)


def _run_dry(include_failed: bool):
    print("DRY-RUN 모드: mock 데이터로 실행합니다.\n")
    return _report(_DRY_RUN_JOBS, include_failed)


def _report(jobs: list[dict], include_failed: bool) -> int:
    code_jobs_checked = 0
    violations = []

    for job in jobs:
        label, is_ok, reason = _check_job(job, include_failed)
        mode = (job.get("mode") or "").strip().lower()
        if mode == "code":
            code_jobs_checked += 1
            if is_ok:
                print(f"[OK]   {label}  {reason}")
            else:
                print(f"[FAIL] {label}  {reason}")
                violations.append(label)
        # Non-code jobs silently skipped unless verbose flag added later

    print()
    print(f"Summary: code-mode 잡 {code_jobs_checked}개 검사, 위반 {len(violations)}건")

    if violations:
        print("\n위반 job_id 목록:")
        for v in violations:
            print(f"  - {v}")
        return 1
    return 0


def main():
    args = _parse_args()
    if args.dry_run:
        sys.exit(_run_dry(args.include_failed))
    else:
        sys.exit(_run_redis(args.redis_url, args.include_failed))


if __name__ == "__main__":
    main()

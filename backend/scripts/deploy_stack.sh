#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${BACKEND_DIR}/.." && pwd)"

UPDATE_MODE="auto"
SKIP_UPDATE="false"
SKIP_HEALTH="false"
BUILD_MODE="build"
DEPLOY_SCOPE="all"

print_usage() {
  cat <<'EOF'
Usage:
  ./backend/scripts/deploy_stack.sh [options]

Options:
  --update-mode auto|svn|git|none   Select update source. Default: auto
  --skip-update                     Do not run svn update / git pull
  --skip-health                     Skip post-deploy health checks
  --no-build                        Run docker compose up without --build
  --app-only                        Deploy only agent-api
  -h, --help                        Show this help

Behavior:
  1. Detect or run source update
  2. Run docker compose up -d [--build]
  3. Wait for backend health
  4. Print api / data service URLs
EOF
}

log() {
  printf '[deploy] %s\n' "$*"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 1
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --update-mode)
      UPDATE_MODE="${2:-}"
      shift 2
      ;;
    --skip-update)
      SKIP_UPDATE="true"
      shift
      ;;
    --skip-health)
      SKIP_HEALTH="true"
      shift
      ;;
    --no-build)
      BUILD_MODE="nobuild"
      shift
      ;;
    --app-only)
      DEPLOY_SCOPE="app"
      shift
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      print_usage >&2
      exit 1
      ;;
  esac
done

require_cmd docker
require_cmd curl

run_update() {
  local mode="$1"
  case "$mode" in
    none)
      log "Skipping source update"
      return 0
      ;;
    svn)
      require_cmd svn
      log "Running svn update"
      svn update "${PROJECT_ROOT}"
      ;;
    git)
      require_cmd git
      log "Running git pull --ff-only"
      git -C "${PROJECT_ROOT}" pull --ff-only
      ;;
    auto)
      if [[ -d "${PROJECT_ROOT}/.svn" ]]; then
        require_cmd svn
        log "Detected svn working copy"
        svn update "${PROJECT_ROOT}"
      elif [[ -d "${PROJECT_ROOT}/.git" ]]; then
        require_cmd git
        log "Detected git repository"
        git -C "${PROJECT_ROOT}" pull --ff-only
      else
        log "No svn or git metadata found. Continuing without update"
      fi
      ;;
    *)
      printf 'Invalid --update-mode: %s\n' "$mode" >&2
      exit 1
      ;;
  esac
}

if [[ "${SKIP_UPDATE}" != "true" ]]; then
  run_update "${UPDATE_MODE}"
fi

cd "${BACKEND_DIR}"

COMPOSE_ARGS=(up -d)
if [[ "${BUILD_MODE}" == "build" ]]; then
  COMPOSE_ARGS+=(--build)
fi

if [[ "${DEPLOY_SCOPE}" == "app" ]]; then
  COMPOSE_ARGS+=(agent-api)
fi

log "Running: docker compose ${COMPOSE_ARGS[*]}"
docker compose "${COMPOSE_ARGS[@]}"

if [[ "${SKIP_HEALTH}" != "true" ]]; then
  log "Waiting for backend health"
  ATTEMPTS=30
  SLEEP_SEC=2
  HEALTH_OK="false"
  for ((i=1; i<=ATTEMPTS; i++)); do
    if HEALTH_BODY="$(curl -fsS http://127.0.0.1:8000/api/v1/health 2>/dev/null)"; then
      HEALTH_OK="true"
      log "Backend health ok"
      printf '%s\n' "${HEALTH_BODY}"
      break
    fi
    sleep "${SLEEP_SEC}"
  done

  if [[ "${HEALTH_OK}" != "true" ]]; then
    log "Backend health check failed after ${ATTEMPTS} attempts"
    docker compose ps
    exit 1
  fi

fi

log "Container status"
docker compose ps

cat <<'EOF'

API:
  http://127.0.0.1:8000/api/v1/health

Qdrant:
  http://127.0.0.1:6333/

MinIO Console:
  http://127.0.0.1:9001/

Neo4j:
  http://127.0.0.1:7474/
EOF

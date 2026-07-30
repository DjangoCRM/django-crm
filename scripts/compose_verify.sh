#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
ENV_FILE="${ENV_FILE:-${ROOT_DIR}/.env}"
POLL_SECONDS="${POLL_SECONDS:-120}"
LOGIN_PATH="${LOGIN_PATH:-/456-admin/login/}"
TIME_BUDGET_SECONDS="${TIME_BUDGET_SECONDS:-600}"
VERIFY_BACKUP="${VERIFY_BACKUP:-0}"
DRY_RUN=0

usage() {
    cat <<'EOF'
Usage: scripts/compose_verify.sh [--dry-run]

End-to-end verification of the documented Docker Compose deployment.
Measures wall-clock time from "docker compose up" to admin login readiness.

Environment variables:
  TIME_BUDGET_SECONDS  Fail if readiness exceeds this budget (default: 600)
  VERIFY_BACKUP        Set to 1 to run backup/restore validation (default: 0)
  ENV_FILE             Path to .env (default: ./.env)
EOF
}

log_phase() {
    printf '[%s] %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$1"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

cd "${ROOT_DIR}"

if [[ "${DRY_RUN}" == "1" ]]; then
    log_phase 'DRY-RUN begin'
    log_phase "Would require ${ENV_FILE} (copy from .env.example)"
    log_phase 'Would run: docker compose -f '"${COMPOSE_FILE}"' up -d --build'
    log_phase 'Would assert: docker compose port db 5432 fails (unpublished)'
    log_phase 'Would poll admin login at '"${LOGIN_PATH}"' up to '"${POLL_SECONDS}"'s'
    log_phase 'Would run: docker compose exec app python manage.py setupdata'
    if [[ "${VERIFY_BACKUP}" == "1" ]]; then
        log_phase 'Would pg_dump database and archive media volume'
        log_phase 'Would restore into fresh stack and re-check login'
    fi
    log_phase 'Would compare elapsed seconds against TIME_BUDGET_SECONDS='"${TIME_BUDGET_SECONDS}"
    log_phase 'Would run: docker compose down -v --remove-orphans'
    log_phase 'DRY-RUN complete'
    exit 0
fi

if [[ ! -f "${ENV_FILE}" ]]; then
    echo "Missing ${ENV_FILE}. Copy .env.example and fill placeholders before running." >&2
    exit 1
fi

BACKUP_DIR="$(mktemp -d)"
cleanup() {
    docker compose -f "${COMPOSE_FILE}" logs --no-color >&2 || true
    docker compose -f "${COMPOSE_FILE}" down -v --remove-orphans >/dev/null 2>&1 || true
    rm -rf "${BACKUP_DIR}"
}
trap cleanup EXIT

log_phase 'Phase: compose up --build'
start_epoch="$(date +%s)"
docker compose -f "${COMPOSE_FILE}" up -d --build

log_phase 'Phase: assert db port unpublished'
if docker compose -f "${COMPOSE_FILE}" port db 5432 >/dev/null 2>&1; then
    echo "Database port 5432 is published; expected internal-only access." >&2
    exit 1
fi

log_phase 'Phase: wait for admin login'
ready=0
while (( $(date +%s) - start_epoch < POLL_SECONDS )); do
    if docker compose -f "${COMPOSE_FILE}" ps --status running --services | grep -qx 'app'; then
        status="$(docker compose -f "${COMPOSE_FILE}" exec -T app python - <<PY
import urllib.error
import urllib.request
try:
    with urllib.request.urlopen('http://127.0.0.1:8000${LOGIN_PATH}') as response:
        print(response.status)
except urllib.error.HTTPError as exc:
    print(exc.code)
except Exception:
    print('000')
PY
)"
        if [[ "${status}" == "200" || "${status}" == "302" ]]; then
            ready=1
            ready_epoch="$(date +%s)"
            break
        fi
    fi
    sleep 2
done

if [[ "${ready}" != "1" ]]; then
    echo "Application did not become ready within ${POLL_SECONDS}s." >&2
    exit 1
fi

elapsed="$(( ready_epoch - start_epoch ))"
log_phase "Phase: login ready in ${elapsed}s"

log_phase 'Phase: setupdata'
docker compose -f "${COMPOSE_FILE}" exec -T app python manage.py setupdata

if [[ "${VERIFY_BACKUP}" == "1" ]]; then
    log_phase 'Phase: backup database and media'
    # shellcheck disable=SC1090
    set -a && source "${ENV_FILE}" && set +a
    docker compose -f "${COMPOSE_FILE}" exec -T db \
        pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -Fc > "${BACKUP_DIR}/crm-backup.dump"
    media_volume="$(docker volume ls --format '{{.Name}}' | grep 'media$' | head -1)"
    if [[ -z "${media_volume}" ]]; then
        echo "Could not locate media volume for backup." >&2
        exit 1
    fi
    docker run --rm -v "${media_volume}:/data" -v "${BACKUP_DIR}:/backup" alpine \
        tar czf /backup/media-backup.tar.gz -C /data .

    log_phase 'Phase: recreate stack for restore test'
    docker compose -f "${COMPOSE_FILE}" down -v --remove-orphans
    docker compose -f "${COMPOSE_FILE}" up -d --build
    sleep 5
    docker compose -f "${COMPOSE_FILE}" exec -T db \
        pg_restore -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --clean --if-exists < "${BACKUP_DIR}/crm-backup.dump"
    docker run --rm -v "${media_volume}:/data" -v "${BACKUP_DIR}:/backup" alpine \
        tar xzf /backup/media-backup.tar.gz -C /data
    status="$(docker compose -f "${COMPOSE_FILE}" exec -T app python - <<PY
import urllib.error
import urllib.request
try:
    with urllib.request.urlopen('http://127.0.0.1:8000${LOGIN_PATH}') as response:
        print(response.status)
except urllib.error.HTTPError as exc:
    print(exc.code)
except Exception:
    print('000')
PY
)"
    if [[ "${status}" != "200" && "${status}" != "302" ]]; then
        echo "Admin login failed after restore (status=${status})." >&2
        exit 1
    fi
    log_phase 'Phase: restore verification passed'
fi

if (( elapsed > TIME_BUDGET_SECONDS )); then
    echo "TIMING_SUMMARY elapsed_seconds=${elapsed} budget_seconds=${TIME_BUDGET_SECONDS} status=FAIL" >&2
    exit 1
fi

echo "TIMING_SUMMARY elapsed_seconds=${elapsed} budget_seconds=${TIME_BUDGET_SECONDS} status=PASS"
log_phase 'Compose verification passed.'

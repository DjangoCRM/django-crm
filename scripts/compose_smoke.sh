#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
ENV_FILE="${ENV_FILE:-${ROOT_DIR}/.env}"
POLL_SECONDS="${POLL_SECONDS:-120}"
LOGIN_PATH="${LOGIN_PATH:-/456-admin/login/}"
RUN_SETUPDATA="${RUN_SETUPDATA:-0}"

cd "${ROOT_DIR}"

if [[ ! -f "${ENV_FILE}" ]]; then
    echo "Missing ${ENV_FILE}. Copy .env.example and fill in placeholders before running." >&2
    exit 1
fi

cleanup() {
    docker compose -f "${COMPOSE_FILE}" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Starting compose stack..."
docker compose -f "${COMPOSE_FILE}" up -d --build

if docker compose -f "${COMPOSE_FILE}" port db 5432 >/dev/null 2>&1; then
    echo "Database port 5432 is published to the host; expected internal-only access." >&2
    exit 1
fi

start_epoch="$(date +%s)"
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
            break
        fi
    fi
    sleep 2
done

if [[ "${ready}" != "1" ]]; then
    echo "Application did not become ready within ${POLL_SECONDS}s." >&2
    docker compose -f "${COMPOSE_FILE}" logs --no-color >&2 || true
    exit 1
fi

if [[ "${RUN_SETUPDATA}" == "1" ]]; then
    echo "Loading committed fixtures via manage.py setupdata..."
    docker compose -f "${COMPOSE_FILE}" exec -T app python manage.py setupdata
fi

echo "Compose smoke check passed."

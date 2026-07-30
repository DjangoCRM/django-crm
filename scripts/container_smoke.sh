#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="${IMAGE_NAME:-django-crm:smoke}"
LOGIN_PATH="${LOGIN_PATH:-/456-admin/login/}"
POLL_SECONDS="${POLL_SECONDS:-60}"
STARTUP_BUDGET_SECONDS="${STARTUP_BUDGET_SECONDS:-20}"

cd "${ROOT_DIR}"

SECRET_KEY="$("${ROOT_DIR}/.venv/bin/python" - <<'PY'
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
PY
)"

echo "Building image ${IMAGE_NAME}..."
docker build -t "${IMAGE_NAME}" .

echo "Verifying non-root runtime user..."
uid="$(docker run --rm --entrypoint id "${IMAGE_NAME}" -u)"
if [[ "${uid}" != "10001" ]]; then
    echo "Expected UID 10001, got ${uid}" >&2
    exit 1
fi

container_id="$(
    docker run -d \
        -e DJANGO_SECRET_KEY="${SECRET_KEY}" \
        -e DJANGO_DEBUG=true \
        -e DATABASE_URL=sqlite:////app/data/crm.db \
        -e RUN_MIGRATIONS=1 \
        -e RUN_COLLECTSTATIC=1 \
        "${IMAGE_NAME}"
)"

cleanup() {
    docker rm -f "${container_id}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

start_epoch="$(date +%s)"
ready=0
while (( $(date +%s) - start_epoch < POLL_SECONDS )); do
    if ! docker ps -q --filter "id=${container_id}" | grep -q .; then
        echo "Container exited before becoming ready." >&2
        docker logs "${container_id}" >&2 || true
        exit 1
    fi
    status="$(docker exec "${container_id}" python - <<PY
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
    sleep 1
done

if [[ "${ready}" != "1" ]]; then
    echo "Login page did not become ready within ${POLL_SECONDS}s." >&2
    docker logs "${container_id}" >&2 || true
    exit 1
fi

elapsed="$(( $(date +%s) - start_epoch ))"
echo "Startup to ready: ${elapsed}s"
if (( elapsed > STARTUP_BUDGET_SECONDS )); then
    echo "Warning: startup exceeded ${STARTUP_BUDGET_SECONDS}s budget (warm image expectation)." >&2
fi

echo "Container smoke check passed."

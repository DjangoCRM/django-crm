#!/usr/bin/env bash
set -euo pipefail

RUN_MIGRATIONS="${RUN_MIGRATIONS:-1}"
RUN_COLLECTSTATIC="${RUN_COLLECTSTATIC:-1}"

python <<'PY'
import os
import sys
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')

max_retries = int(os.environ.get('DB_WAIT_RETRIES', '30'))
wait_seconds = int(os.environ.get('DB_WAIT_SECONDS', '2'))

import django

django.setup()
from django.db import connection

for attempt in range(1, max_retries + 1):
    try:
        connection.ensure_connection()
        break
    except Exception as exc:
        if attempt == max_retries:
            print(f'Database not ready after {max_retries} attempts: {exc}', file=sys.stderr)
            sys.exit(1)
        print(f'Waiting for database (attempt {attempt}/{max_retries})...')
        time.sleep(wait_seconds)
PY

if [[ "${RUN_MIGRATIONS}" == "1" ]]; then
    python manage.py migrate --noinput
fi

if [[ "${RUN_COLLECTSTATIC}" == "1" ]]; then
    python manage.py collectstatic --noinput
fi

exec "$@"

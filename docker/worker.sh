#!/usr/bin/env bash
set -euo pipefail

python manage.py run_mail_workers &
mail_pid=$!
python manage.py run_schedulers &
sched_pid=$!

terminate() {
    kill -TERM "${mail_pid}" "${sched_pid}" 2>/dev/null || true
    wait "${mail_pid}" "${sched_pid}" 2>/dev/null || true
}
trap terminate TERM INT

wait -n "${mail_pid}" "${sched_pid}"
exit $?

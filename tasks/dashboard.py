"""Tasks dashboard counter providers."""

from django.db.models import Count
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime
from django.utils.timezone import now

from tasks.utils.hide_main_tasks import hide_main_tasks
from sharedkernel.dashboard import register_counter
from sharedkernel.dashboard import set_counters
from tasks.models import Memo
from tasks.models import Task


def register_tasks_dashboard_providers() -> None:
    register_counter('tasks_open_tasks', 10, 'tasks', apply_task_count)
    register_counter('tasks_pending_memos', 20, 'tasks', apply_memo_count)


def apply_memo_count(request, models) -> None:
    memo_count = Memo.objects.filter(
        stage=Memo.PENDING,
        to=request.user,
    ).count()
    if not memo_count:
        return
    model_name = Memo._meta.verbose_name_plural
    memo = next((m for m in models if m['name'] == model_name), None)
    if memo is None:
        return
    memo['name'] = mark_safe(
        f"{model_name} "
        f"(<span style='color: var(--error-fg)'>{memo_count}</span>)"
    )


def apply_task_count(request, models) -> None:
    today = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
    qs = Task.objects.filter(
        stage__active=True,
        responsible=request.user,
    )
    qs = hide_main_tasks(request, qs)
    counts = qs.aggregate(
        regular=Count('pk', filter=Q(next_step_date__isnull=True)
                      | Q(next_step_date__gte=today)),
        urgent=Count('pk', filter=Q(next_step_date__isnull=False)
                     & Q(next_step_date__lt=today)),
    )
    if counts['urgent'] or counts['regular']:
        set_counters(Task, models, counts)

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models.query import QuerySet

from tasks.models import Task


def hide_main_tasks(request: WSGIRequest, queryset: QuerySet) -> QuerySet:
    """
    Hides for the user the main tasks that have no active subtasks
    or has an active subtask with hide_main_task=True
    """
    active_subtask = Task.objects.filter(
        task=OuterRef('pk'),
        stage__active=True,
        responsible=request.user
    )

    hide = Task.objects.filter(
        task=OuterRef('pk'),
        stage__active=False,
        hide_main_task=True,
        responsible=request.user
    )

    return queryset.annotate(
        is_active_subtask=Exists(active_subtask),
        hide=Exists(hide),
    ).exclude(
        task__isnull=True,
        is_active_subtask=False,
        hide=True
    )

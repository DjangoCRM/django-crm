"""CRM dashboard counter providers."""

from django.db.models import Count
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime
from django.utils.timezone import now

from crm.models import CrmEmail
from crm.models import Request
from sharedkernel.dashboard import register_counter
from sharedkernel.dashboard import set_counters


def register_crm_dashboard_providers() -> None:
    register_counter('crm_outbox_email', 10, 'crm', apply_outbox_email_count)
    register_counter('crm_pending_requests', 20, 'crm', apply_request_count)


def _crm_counter_roles(request) -> bool:
    return any((
        request.user.is_manager,
        request.user.is_operator,
        request.user.is_superoperator,
        request.user.is_superuser,
        request.user.is_chief,
    ))


def apply_outbox_email_count(request, models) -> None:
    if not _crm_counter_roles(request):
        return
    outbox_count = CrmEmail.objects.filter(
        owner=request.user,
        sent=False,
        incoming=False,
        trash=False,
    ).count()
    if not outbox_count:
        return
    model_name = CrmEmail._meta.verbose_name_plural
    post = next((m for m in models if m['name'] == model_name), None)
    if post:
        post['name'] = mark_safe(
            f"{model_name}: "
            f"<span style='color: var(--error-fg)'>outbox ({outbox_count})</span>"
        )


def apply_request_count(request, models) -> None:
    if not _crm_counter_roles(request):
        return
    today = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
    qs = Request.objects.filter(pending=True)
    q_params = Q()
    if any((
        request.user.is_operator,
        request.user.is_superoperator,
        request.user.is_superuser,
        request.user.is_chief,
    )) and not request.user.is_manager:
        q_params = Q(owner__groups__name__in=('superoperators', 'operators'))
        q_params |= Q(owner__isnull=True)
        if request.user.department_id:
            qs = qs.filter(department_id=request.user.department_id)
    elif request.user.is_manager:
        q_params = Q(owner=request.user) | Q(co_owner=request.user)

    counts = qs.filter(q_params).aggregate(
        regular=Count('pk', filter=Q(creation_date__gte=today)),
        urgent=Count('pk', filter=Q(creation_date__lt=today)),
    )
    if counts['urgent'] or counts['regular']:
        set_counters(Request, models, counts)

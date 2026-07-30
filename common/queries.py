"""ORM query helpers separated from presentation and workflow utilities."""

from __future__ import annotations

from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models.query import QuerySet

from chat.models import ChatMessage


def add_chat_context(request, extra_context, object_id, content_type):
    chat = ChatMessage.objects.filter(
        object_id=object_id,
        content_type=content_type,
    )
    extra_context['is_chat'] = chat.exists()
    if extra_context['is_chat']:
        extra_context['is_unread_chat'] = chat.filter(
            recipients=request.user,
        ).exists()


def add_phone_q_params(phone: str, q_params: Q = None) -> Q:
    q_params = q_params or Q()
    digits = [i for i in phone if i.isdigit()]
    if len(digits) > 4:
        digits_re = ''.join((f'[^0-9]*[{i}]{{1}}' for i in digits))
        phone_re = fr'{digits_re}'
        q_params |= Q(phone__iregex=phone_re)
        q_params |= Q(other_phone__iregex=phone_re)
        q_params |= Q(mobile__iregex=phone_re)
    return q_params


def annotate_chat(request: WSGIRequest, queryset: QuerySet) -> QuerySet:
    content_type = ContentType.objects.get_for_model(queryset.model)
    chat = ChatMessage.objects.filter(
        object_id=OuterRef('pk'),
        content_type=content_type,
    )
    if not any((request.user.is_superuser, request.user.is_chief)):  # NOQA
        chat = chat.filter(
            Q(owner_id=request.user.id) | Q(to=request.user.id),
        ).distinct()
    return queryset.annotate(
        is_chat=Exists(chat),
        is_unread_chat=Exists(chat.filter(recipients=request.user)),
    )


def get_active_users() -> QuerySet:
    return User.objects.exclude(
        Q(is_active=False) | Q(is_staff=False),
    )


def get_manager_departments():
    """Return department groups that have users with the managers role."""
    return apps.get_model('auth', 'Group').objects.filter(
        department__isnull=False,
        user__groups__name='managers',
    ).distinct()


def get_department_id(user):
    department = user.groups.filter(
        department__isnull=False,
    ).first()
    return department.id if department else None

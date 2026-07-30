"""CRM notification email composition helpers."""

from __future__ import annotations

from django.contrib.auth.models import User
from django.template.defaultfilters import truncatechars
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe


def _obj_name(obj) -> str:
    if hasattr(obj, 'name'):
        return obj.name
    return getattr(obj, 'request_for', '')


def compose_message(obj, message: str) -> SafeString:
    obj_name = _obj_name(obj)
    link = f'<a href="{obj.get_absolute_url()}">{obj_name}.</a>'
    return mark_safe(f'CRM: {message} - {link}')


def compose_subject(obj, message: str, user: User = None) -> str:
    """Compose a subject for CRM emails."""
    obj_name = _obj_name(obj)
    obj_name = ' '.join(obj_name.splitlines())
    obj_name = truncatechars(obj_name, 90)
    if user:
        return f'CRM: {message} ({user.username}) - {obj_name}'
    return f'CRM: {message} - {obj_name}'

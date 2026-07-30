"""Timezone-aware date helpers for CRM workflows."""

from __future__ import annotations

from datetime import timedelta

from django.utils.timezone import localtime
from django.utils.timezone import now


def get_now():
    return localtime(now())


def get_today():
    return get_now().date()


def get_delta_date(delta):
    today = get_today()
    weekday = today.weekday()
    if weekday in (4, 5):
        return today + timedelta(delta + 6 - weekday)
    return today + timedelta(delta)

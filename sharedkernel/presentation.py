"""Stateless presentation constants and formatting helpers."""

from __future__ import annotations

from django.utils.formats import date_format
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime
from django.utils.timezone import now
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_lazy

COPY_STR = gettext_lazy('Copy')
CONTENT_COPY_ICON = (
    '<i class="material-icons"style="font-size: 17px;vertical-align: middle;">content_copy</i>'
)
CONTENT_COPY_LINK = '<a href="{}" title="{}">{}</a>'
CRM_NOTICE = (
    '<i class ="material-icons" style="color: var(--body-quiet-color);'
    'font-size: 17px;vertical-align: middle;">message</i>:'
)
FRIDAY_SATURDAY_SUNDAY_MSG = _(
    'Attention! Mass mailings are not carried out on: Fridays, Saturdays and Sundays.',
)
LEADERS = '- - - -'
OBJ_DOESNT_EXIT_STR = gettext_lazy(
    "{} with ID '{}' doesn’t exist. Perhaps it was deleted?",
)
ONCLICK_STR = "window.open('{}', '{}','width=800,height=700'); return false;"
SAFE_ATTACH_FILE_ICON = mark_safe(
    '<i class="material-icons" style="color: var(--body-quiet-color)">attach_file</i>',
)
SAFE_SUBJECT_ICON = mark_safe(
    '<i class="material-icons" style="color: var(--body-quiet-color)">subject</i>',
)


def get_formatted_short_date() -> str:
    """Return today's date formatted with SHORT_DATE_FORMAT."""
    return date_format(
        localtime(now()).date(),
        format='SHORT_DATE_FORMAT',
        use_l10n=True,
    )


def get_verbose_name(model, field: str) -> str:
    """Return the translated verbose name of a model field."""
    verbose_name = model._meta.get_field(field).verbose_name  # NOQA
    if hasattr(verbose_name, '_proxy____args'):
        title = gettext(verbose_name._args[0])  # NOQA
    else:
        title = gettext(verbose_name)
    return title


def popup_window(url: str, window_name: str = '') -> str:
    """Return onClick value for a popup link tag."""
    window_name = window_name or 'WindowName'
    return ONCLICK_STR.format(url, window_name)

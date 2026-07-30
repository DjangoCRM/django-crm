"""CRM notification delivery and admin messaging helpers."""

from __future__ import annotations

from django.apps import apps
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import mail_admins
from django.utils.translation import gettext_lazy as _


def save_message(user, msg: str, level: str = 'INFO') -> None:
    """Save a message to the user's profile inbox."""
    user.profile.append_message(msg, level)


def send_crm_email(subject: str = '', body: str = '', to: list | None = None) -> None:
    """Send CRM notification emails through the worker or test mail backend."""
    from django.core.mail import EmailMessage

    app_config = apps.get_app_config('common')
    nes = getattr(app_config, 'nes', None)
    if nes is not None:
        nes.send_msg(subject, body, to)
        return

    if settings.TESTING:
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to,
            reply_to=settings.CRM_REPLY_TO,
        )
        msg.content_subtype = 'html'
        msg.send()
        return

    raise AttributeError(
        'Notification email sender is unavailable; enable RUN_BACKGROUND_WORKERS '
        'or run the scheduler worker service.',
    )


def notify_admins_no_email(user) -> None:
    """Notify admins that the user's email address is not specified."""
    if not settings.DEBUG:
        mail_admins(
            ' No email address for User - %s.' % user,
            'CRM cannot send an email to %s.' % user,
        )


def set_toggle_tooltip(key: str, request: WSGIRequest, extra_context: dict) -> None:
    if key in request.session:
        extra_context['toggle_title'] = _('sort by creation date')
    else:
        extra_context['toggle_title'] = _('sort by next step date')

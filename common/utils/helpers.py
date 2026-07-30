import secrets
from datetime import timedelta
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import mail_admins
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.safestring import SafeString
from django.utils.timezone import localtime
from django.utils.timezone import now
from django.utils.translation import gettext
from django.utils.translation import override

# Temporary compatibility re-exports — import from common.queries instead.
from common.queries import add_chat_context
from common.queries import add_phone_q_params
from common.queries import annotate_chat
from common.queries import get_active_users
from common.queries import get_department_id
from common.queries import get_manager_departments

# Temporary compatibility re-exports — import from sharedkernel.presentation instead.
from sharedkernel.presentation import CONTENT_COPY_ICON
from sharedkernel.presentation import CONTENT_COPY_LINK
from sharedkernel.presentation import COPY_STR
from sharedkernel.presentation import CRM_NOTICE
from sharedkernel.presentation import FRIDAY_SATURDAY_SUNDAY_MSG
from sharedkernel.presentation import LEADERS
from sharedkernel.presentation import OBJ_DOESNT_EXIT_STR
from sharedkernel.presentation import ONCLICK_STR
from sharedkernel.presentation import SAFE_ATTACH_FILE_ICON
from sharedkernel.presentation import SAFE_SUBJECT_ICON
from sharedkernel.presentation import get_formatted_short_date
from sharedkernel.presentation import get_verbose_name
from sharedkernel.presentation import popup_window


USER_MODEL = get_user_model()


def get_trans_for_lang(text: str, language_code: str) -> str:
    """Get translation for a specific language"""
    with override(language_code):
        return gettext(text)


def get_trans_for_user(text: str, user) -> str:
    """Translation function into the user's language"""
    code = get_user_language_code(user)
    return get_trans_for_lang(text, code)


def get_user_language_code(user) -> str:
    if settings.USE_I18N:
        return user.profile.language_code or settings.LANGUAGE_CODE
    return settings.LANGUAGE_CODE


def notify_admins_no_email(user) -> None:
    """Notify admins that the user's email address is not specified."""
    if not settings.DEBUG:
        mail_admins(
            " No email address for User - %s." % user,
            "CRM cannot send an email to %s." % user,
        )


def get_delta_date(delta):
    today = get_today()
    n = today.weekday()
    if n in (4, 5):
        return today + timedelta(delta + 6 - n)
    else:
        return today + timedelta(delta)


def get_now():
    return localtime(now())


def get_obj_name(obj):
    if hasattr(obj, 'name'):
        obj_name = obj.name
    else:
        obj_name = getattr(obj, 'request_for', '')
    return obj_name


def compose_message(obj, message: str) -> SafeString:
    obj_name = get_obj_name(obj)
    link = f'<a href="{obj.get_absolute_url()}">{obj_name}.</a>'
    msg = mark_safe(f"CRM: {message} - {link}")
    return msg


def compose_subject(obj, message: str, user: User = None) -> str:
    """Compose a subject for CRM emails.
    This function creates a subject line that includes the object name,
    a message, and optionally the username of the responsible user.
    Args:
        obj (Task, Project, Memo): Object for which the subject is composed.
        message (str): Main message for the subject.
        user (auth.User, optional): Defaults to None.

    Returns:
        str: Composed subject line.
    """
    obj_name = get_obj_name(obj)
    obj_name = " ".join(obj_name.splitlines())
    obj_name = truncatechars(obj_name, 90)
    if user:
        subject = f"CRM: {message} ({user.username}) - {obj_name}"
    else:
        subject = f"CRM: {message} - {obj_name}"
    return subject


def get_today():
    return get_now().date()


def save_message(user, msg: str, level: str = 'INFO'):
    """Save message to not current user."""
    profile = user.profile
    profile.messages.extend([msg, level])
    profile.save(update_fields=['messages'])


def send_crm_email(
        subject: str = "",
        body: str = "",
        to: list = None
) -> None:
    """Helps to send CRM notification emails."""
    from django.conf import settings
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
        msg.content_subtype = "html"
        msg.send()
        return

    raise AttributeError(
        "Notification email sender is unavailable; enable RUN_BACKGROUND_WORKERS "
        "or run the scheduler worker service."
    )


def set_toggle_tooltip(key: str, request: WSGIRequest, extra_context: dict) -> None:
    if key in request.session:
        extra_context['toggle_title'] = _("sort by creation date")
    else:
        extra_context['toggle_title'] = _("sort by next step date")


def token_default():
    return secrets.token_urlsafe(8)

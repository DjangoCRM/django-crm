import secrets
from datetime import timedelta
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import mail_admins
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models.query import QuerySet
from django.template.defaultfilters import truncatechars
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.safestring import SafeString
from django.utils.timezone import localtime
from django.utils.timezone import now
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy

from chat.models import ChatMessage

COPY_STR = gettext_lazy("Copy")
CONTENT_COPY_ICON = '<i class="material-icons"style="font-size: 17px;vertical-align: middle;">content_copy</i>'
CONTENT_COPY_LINK = '<a href="{}" title="{}">{}</a>'
CRM_NOTICE = '<i class ="material-icons" style="color: var(--body-quiet-color);\
    font-size: 17px;vertical-align: middle;">message</i>:'
LEADERS = '- - - - -'
OBJ_DOESNT_EXIT_STR = gettext_lazy("{} with ID '{}' doesn’t exist. "
                                   "Perhaps it was deleted?")
ONCLICK_STR = "window.open('{}', '{}','width=800,height=700'); return false;"
USER_MODEL = get_user_model()


def add_chat_context(request, extra_context, object_id, content_type):
    chat = ChatMessage.objects.filter(
        object_id=object_id,
        content_type=content_type
    )
    extra_context['is_chat'] = chat.exists()
    if extra_context['is_chat']:
        extra_context['is_unread_chat'] = chat.filter(
            recipients=request.user
        ).exists()


def annotate_chat(request: WSGIRequest, queryset: QuerySet) -> QuerySet:
    content_type = ContentType.objects.get_for_model(queryset.model)
    chat = ChatMessage.objects.filter(
        object_id=OuterRef('pk'),
        content_type=content_type
    )
    if not any((request.user.is_superuser, request.user.is_chief)):  # NOQA
        chat = chat.filter(
            Q(owner_id=request.user.id) |
            Q(to=request.user.id)
        ).distinct()
    qs = queryset.annotate(
        is_chat=Exists(chat),
        is_unread_chat=Exists(chat.filter(recipients=request.user))
    )
    return qs


def get_active_users() -> QuerySet:
    return USER_MODEL.objects.exclude(
        Q(is_active=False) |
        Q(is_staff=False)
    )


def get_manager_departments():
    """Returns department groups that have
    users with the group 'managers'."""
    
    return apps.get_model('auth', 'Group').objects.filter(
        department__isnull=False,
        user__groups__name='managers'
    ).distinct()


def get_department_id(user):
    department = user.groups.filter(
        department__isnull=False
    ).first()
    return department.id if department else None


def get_formatted_short_date():
    return date_format(
        get_today(),
        format='SHORT_DATE_FORMAT',
        use_l10n=True
    )


def add_phone_q_params(phone: str, q_params: Q = None) -> Q:
    q_params = q_params or Q()
    digits = [i for i in phone if i.isdigit()]
    if len(digits) > 4:
        digits_re = ''.join((f'[^0-9]*[{i}]{{1}}' for i in digits))
        phone_re = fr"{digits_re}"
        q_params |= Q(phone__iregex=phone_re)
        q_params |= Q(other_phone__iregex=phone_re)
        q_params |= Q(mobile__iregex=phone_re)
    return q_params


def get_verbose_name(model, field: str) -> str:
    """Returns the translated verbose name of the model field."""
    verbose_name = model._meta.get_field(field).verbose_name  # NOQA
    if hasattr(verbose_name, '_proxy____args'):
        title = gettext(verbose_name._args[0])  # NOQA
    else:
        title = gettext(verbose_name)
    return title


def popup_window(url: str, window_name: str = '') -> str:
    """Return onClick value for a link tag."""
    window_name = window_name or 'WindowName'
    return ONCLICK_STR.format(url, window_name)


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
    msg = mark_safe(f"CRM: {message} - {link} ({obj.owner})")
    return msg


def compose_subject(obj, message) -> str:
    obj_name = get_obj_name(obj)
    obj_name = " ".join(obj_name.splitlines())
    obj_name = truncatechars(obj_name, 90)
    subject = f"CRM: {message} - {obj_name} ({obj.owner})"
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
    """Helps to send CPM notification emails."""

    app_config = apps.get_app_config('common')
    app_config.nes.send_msg(subject, body, to)


def token_default():
    return secrets.token_urlsafe(8)

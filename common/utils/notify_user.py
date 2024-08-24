from importlib import import_module
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext as _
from django.utils.translation import override

from common.utils.helpers import compose_message
from common.utils.helpers import compose_subject
from common.utils.helpers import notify_admins_no_email
from common.utils.helpers import save_message
from common.utils.email_to_participants import email_to_participants

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


def notify_user(obj, user: User, subject: str, message='', *,
                level='INFO', responsible: User =None, request: WSGIRequest = None) -> None:
    composed_subject = composed_message = ''
    code = user.profile.language_code  # NOQA
    with override(code):
        if subject:
            composed_subject = compose_subject(obj, _(subject))
        if message:
            composed_message = compose_message(obj, _(message))
    if request and request.user == user:
        messages.info(request, composed_message)
    else:
        save_message(user, composed_message or composed_subject, level)
    if hasattr(user, 'email'):
        email_to_participants(obj, subject, [user], composed_subject, responsible)
    else:
        notify_admins_no_email(user)

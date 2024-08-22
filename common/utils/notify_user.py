from importlib import import_module
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest

from common.utils.helpers import compose_message
from common.utils.helpers import compose_subject
from common.utils.helpers import notify_admins_no_email
from common.utils.helpers import save_message
from common.utils.email_to_participants import email_to_participants

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


def notify_user(obj, user: User, subject: str, message='', *,
                level='INFO', responsible: User =None, request: WSGIRequest = None) -> None:
    if subject:
        composed_subject = compose_subject(obj, subject)
    if request and request.user == user:
        msg = compose_message(obj, message)
        messages.info(request, msg)
    else:
        save_message(user, message or composed_subject, level)
    if hasattr(user, 'email'):
        email_to_participants(obj, composed_subject, [user], responsible)
    else:
        notify_admins_no_email(user)

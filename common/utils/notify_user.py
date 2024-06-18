from importlib import import_module
from django.conf import settings
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest

from common.utils.helpers import notify_admins_no_email
from common.utils.helpers import save_message
from common.utils.helpers import USER_MODEL
from common.utils.email_to_participants import email_to_participants

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


def notify_user(obj, user: USER_MODEL, subject: str, message='', *,
                level='INFO', responsible=None, request: WSGIRequest = None) -> None:
    if request and request.user == user:
        messages.info(request, message)
    else:
        save_message(user, message or subject, level)
    if hasattr(user, 'email'):
        email_to_participants(obj, subject, [user.email], responsible)
    else:
        notify_admins_no_email(user)

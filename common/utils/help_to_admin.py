from django.contrib.messages import constants
from django.contrib.messages.storage.session import SessionStorage
from django.contrib.messages.storage.base import Message
from django.http import HttpRequest


def help_to_admin(request: HttpRequest) -> None:
    session_storage = request._messages         # NOQA
    notice = "It's help for admin"
    level = constants.WARNING
    message = Message(constants.WARNING, notice)
    if type(session_storage) == SessionStorage:
        messages, _ = session_storage._get()    # NOQA
        if not messages or message not in messages:
            session_storage.add(level, notice)

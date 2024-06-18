from typing import Union
from unittest import skip
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.test import Client
from django.test import override_settings
from django.test import TestCase
from django.utils.translation import gettext as _

from common.utils.helpers import USER_MODEL
from tasks.models import Task
from tasks.models import TaskStage
from tests.utils.helpers import get_adminform_initials


def task_completed(request: WSGIRequest, token: str,
                   object_id: int) -> Union[HttpResponse, TemplateResponse]:
    try:
        task = Task.objects.get(token=token)
    except Task.DoesNotExist:
        return HttpResponse(_("The Task does not exist"))
    try:
        user = USER_MODEL.objects.get(id=object_id)
    except USER_MODEL.DoesNotExist:
        return HttpResponse(_("The user does not exist"))
    tc = TaskCompleted()
    tc.do(task, user)
    msg = _("The task is closed")
    return TemplateResponse(
        request,
        "common/centered_msg.html", {'msg': f"CRM: {msg}"}
    )


@skip("This is not a test")
class TaskCompleted(TestCase):
    """Mark the task as completed in the email"""

    @override_settings(
        SECURE_HSTS_SECONDS=0,
        SECURE_SSL_REDIRECT=False,
        SECURE_HSTS_PRELOAD=False
    )
    def do(self, task, user) -> None:
        self.client = Client(SERVER_NAME='localhost')
        self.client.force_login(user)
        url = task.get_absolute_url()
        response = self.client.get(
            url,
            HTTP_ACCEPT_LANGUAGE=settings.LANGUAGE_CODE
        )
        data = get_adminform_initials(response)
        data['stage'] = str(TaskStage.objects.get(done=True).id)
        data['hide_main_task'] = True

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

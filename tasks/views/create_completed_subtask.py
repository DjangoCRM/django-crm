from typing import Union
from unittest import skip
from django.conf import settings
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import mail_admins
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.test import Client
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from common.utils.helpers import USER_MODEL
from tasks.models import Task
from tasks.models import TaskStage
from tasks.site.taskadmin import TaskAdmin
from tests.utils.helpers import get_adminform_initials


def check_subtasks(object_id: int, request: WSGIRequest) -> str:
    redirect_url = None
    if request.user.is_authenticated:

        data = Task.objects.filter(
            task_id=object_id,
            responsible=request.user
        ).aggregate(
            active_subtask=Count('pk', filter=Q(stage__active=True)),
            closed_subtasks=Count('pk', filter=Q(stage__active=False, hide_main_task=True))
        )
        if data['active_subtask'] or data['closed_subtasks']:
            url = reverse('site:tasks_task_changelist')
            redirect_url = url
            if data['active_subtask']:
                redirect_url = f"{url}?task__id__exact={object_id}&responsible={request.user.username}"
                messages.warning(
                    request,
                    _("The task cannot be marked as completed because you have an active subtask.")
                )
    return redirect_url


def create_completed_subtask(request: WSGIRequest, object_id: int) -> HttpResponseRedirect:
    redirect_url = check_subtasks(object_id, request)       # NOQA
    if redirect_url:
        return HttpResponseRedirect(redirect_url)

    add_subtask_url = TaskAdmin.get_add_subtask_url(object_id)
    cs = CreateSubtask()
    err = cs.do(add_subtask_url, request.user)
    if err:
        messages.error(request, err)
    return HttpResponseRedirect(reverse('site:tasks_task_changelist'))


def email_subtask_completion(request: WSGIRequest, token: str, object_id: int
                             ) -> Union[HttpResponseRedirect, HttpResponse, TemplateResponse]:
    redirect_url = check_subtasks(object_id, request)
    if redirect_url:
        return HttpResponseRedirect(redirect_url)

    try:
        task = Task.objects.get(token=token)
    except Task.DoesNotExist:
        return HttpResponse(_("The Task does not exist"))
    try:
        user = USER_MODEL.objects.get(id=object_id)
    except USER_MODEL.DoesNotExist:
        return HttpResponse(_("The user does not exist"))
    add_subtask_url = TaskAdmin.get_add_subtask_url(task.id)
    cs = CreateSubtask()
    err = cs.do(add_subtask_url, user)
    msg = _("The task is closed")
    if err:
        messages.error(request, err)
        msg = err
    return TemplateResponse(
        request,
        "common/centered_msg.html", {'msg': f"CRM: {msg}"}
    )


@skip("This is not a test")
class CreateSubtask(TestCase):
    """Creates a completed subtask."""


    @override_settings(
        SECURE_HSTS_SECONDS=0,
        SECURE_SSL_REDIRECT=False,
        SECURE_HSTS_PRELOAD=False
    )
    def do(self, url, user) -> str:
        """
        Creates a completed subtask.
        Returns the error string or an empty string.
        """
        err = ''
        self.client = Client(SERVER_NAME='localhost')
        self.client.force_login(user)
        response = self.client.get(
            url,
            HTTP_ACCEPT_LANGUAGE=settings.LANGUAGE_CODE
        )
        data = get_adminform_initials(response)
        data['responsible'] = [str(user.id)]
        data['stage'] = str(TaskStage.objects.get(done=True).id)
        data['hide_main_task'] = True

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        form = response.context_data
        if 'adminform' in form:
            err = _("An error occurred while creating the subtask. Contact the CRM Administrator.")
            mail_admins(
                "Exception: CreateSubtask.do()",
                f'''
                \nUser: {user}
                \nException: {form['adminform'].errors.as_text()}''',
                fail_silently=False,
            )

        return err

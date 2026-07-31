from django.contrib.sites.models import Site
from django.template import Library
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from tasks.models import Task
from tasks.site.taskadmin import COMPLETED_TITLE

register = Library()


@register.filter
def task_completed_button(obj: Task, responsible) -> str:
    """It is used to generate the button code in the template
    of the notification email to the responsible (user)."""
    button_code = ''
    if obj.__class__ == Task:
        site = Site.objects.get_current()
        if obj.responsible.count() == 1:
            path_name = "task_completed"
            button_name = _("Task completed")
            title = _("I completed the task")
        else:
            path_name = "email-subtask_completed"
            button_name = _("Completed")
            title = COMPLETED_TITLE
        complete_url = reverse(path_name, args=(obj.token, responsible.id))
        button_code = mark_safe(
            f'<a title="{title}" href="https://{site.domain}{complete_url}">'
            f'<button>{button_name}</button></a>&emsp;'
        )
    return button_code

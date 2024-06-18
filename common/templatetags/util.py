from django.core.mail import mail_admins
from django.contrib.sites.models import Site
from django.db import models
from django.template import Library     # NOQA
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

from common.models import TheFile
from common.utils.helpers import USER_MODEL
from tasks.models import Task
from tasks.site.taskadmin import COMPLETED_TITLE

register = Library()
FILE_ERROR_SUBJ = "TheFile error: ID{}"


@register.filter
def crmadmin_urlname(value, arg):
    return 'site:%s_%s_%s' % (value.app_label, value.model_name, arg)


@register.filter
def priority(obj) -> int:
    value = None
    if hasattr(obj, 'priority'):
        value = next(p for i, p in obj.PRIORITY_CHOICES if i == obj.priority)
    return value


@register.filter
def get_url(file: TheFile) -> str:
    try:
        url = file.file.url
    except ValueError as err:
        url = None
        content_object = file.content_object
        site = Site.objects.get_current()
        path = reverse(
            f'site:{content_object._meta.app_label}_{content_object._meta.model_name}_change',  # NoQA
            args=[str(content_object.id)]
        )
        content_object_url = f"https://{site.domain}{path}"
        mail_admins(
            FILE_ERROR_SUBJ.format(file.id),
            f"""
            \n     Error: {err}            
            \n     Content object of the file: 
            \n     {content_object._meta.label}: "{content_object}"
            \n     {content_object_url}
            \n     File name: {file.file.name}
            \n     Owner: {getattr(content_object, "owner", None) or "No owner"}
            """,
            fail_silently=True
        )
    return url


@register.filter
def replace_lang(value: str, language_code: str) -> str:
    language_code_str = f"/{language_code}"
    if value.startswith(language_code_str):
        return value
    url_str_lst = value.replace("/", '', 1).split("/")
    url_str_lst.pop(0)
    url_str_lst.insert(0, language_code_str)
    url = "/".join(url_str_lst)
    return url
    

@register.filter
def responsible_list(obj) -> str:
    value = None
    if hasattr(obj, 'responsible'):
        value = ", ".join([str(u) for u in obj.responsible.all()])
    return value


@register.filter
def stage(obj) -> str:
    if hasattr(obj, 'stage'):
        field = obj._meta.get_field('stage')    # NOQA
        if isinstance(field, models.ForeignKey):
            return str(obj.stage)
        elif isinstance(field, models.CharField):
            return obj.get_stage_display()
    return ''


@register.filter
def task_completed_button(obj: Task, responsible: USER_MODEL) -> str:
    """It is used to generate the button code in the template 
    of the notification email to the responsible."""
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


@register.filter
def verbose_name(obj):
    return obj._meta.verbose_name   # NoQA

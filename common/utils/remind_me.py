from typing import Union
from datetime import datetime as dt
from datetime import time
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone

from common.models import Reminder
from crm.forms.admin_forms import DealForm
from tasks.forms import TaskForm
from tasks.forms import ProjectForm


def remind_me(request: WSGIRequest,
              form: Union[DealForm, TaskForm, ProjectForm], change: bool) -> None:
    obj = form.instance
    params = {
        "content_type": ContentType.objects.get_for_model(obj),
        "object_id": obj.id,
        "description": obj.next_step,
        "owner": request.user,
        "active": True
    }
    if obj.remind_me:
        t = time(
            settings.BUSINESS_TIME_START['hour'],
            settings.BUSINESS_TIME_START['minute'] + 10
        )
        reminder_date = dt.combine(obj.next_step_date, t)
        if settings.USE_TZ:
            reminder_date = timezone.make_aware(reminder_date)
        if any((not change,
                'remind_me' in form.changed_data)):
            Reminder.objects.create(
                **params,
                subject=obj.next_step,
                reminder_date=reminder_date
            )
        elif 'next_step_date' in form.changed_data and 'next_step' not in form.changed_data:
            Reminder.objects.filter(**params).update(
                reminder_date=reminder_date
            )
        elif 'next_step' in form.changed_data and 'next_step_date' not in form.changed_data:
            del params['description']
            params["reminder_date"] = reminder_date
            Reminder.objects.filter(**params).update(
                subject=obj.next_step,
                description=obj.next_step
            )
        elif 'next_step' in form.changed_data and 'next_step_date' in form.changed_data:
            del params['description']
            Reminder.objects.filter(**params).update(
                subject=obj.next_step,
                description=obj.next_step,
                reminder_date=reminder_date
            )
    else:
        if 'remind_me' in form.changed_data:
            Reminder.objects.filter(**params).delete()

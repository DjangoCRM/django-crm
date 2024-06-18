from random import random
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.template import loader
from django.core import mail
from django.test import tag
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.formats import time_format
from django.utils import timezone

from common.utils.helpers import USER_MODEL
from common.utils.reminders_sender import send_remainders
from tasks.models import Task
from tasks.models import TaskStage
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials

# manage.py test tests.common.test_reminder --keepdb


@tag('TestCase')
class TestReminder(BaseTestCase):
    """Test reminder"""

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_task_reminder(self):
        username_list = ("Sergey.Co-worker.Head.Bookkeeping",
                         "Masha.Co-worker.Bookkeeping")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        self.sergey = users.get(username="Sergey.Co-worker.Head.Bookkeeping")
        self.masha = users.get(username="Masha.Co-worker.Bookkeeping")
        self.default_stage = TaskStage.objects.get(default=True)        
        content = random()
        task = Task.objects.create(
            name="Test task for reminder",
            priority='2',
            description=content,
            stage=self.default_stage,
            owner=self.sergey
        )
        task.responsible.add(self.masha)
        
        content_type = ContentType.objects.get_for_model(Task)
        params = f"?content_type={content_type.id }&object_id={task.id}"
        url = reverse("site:common_reminder_add")
        add_reminder_url = url + params
        self.client.force_login(self.masha)
        response = self.client.get(add_reminder_url + params)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        now = timezone.now()
        data = get_adminform_initials(response)
        # fill the form
        data['subject'] = "reminder for task"
        data['description'] = content        
        data['reminder_date_0'] = date_format(now.date(), format="SHORT_DATE_FORMAT")   # str: 11.05.2021
        data['reminder_date_1'] = time_format(now.time(), format="H:i:s")               # str: 13:03:18
        data['active'] = True
        data['send_notification_email'] = True
        response = self.client.post(add_reminder_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)

        site = Site.objects.get_current()
        template = loader.get_template("common/reminder_message.html")
        # with self.settings(TESTING=True):
        send_remainders()
        self.assertEqual(1, len(mail.outbox))
        self.assertIn(data['subject'], mail.outbox[0].subject)
        mail.outbox = []

from random import random
from django.test import tag
from django.urls import reverse

from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from massmail.models import EmlMessage
from tests.base_test_classes import BaseTestCase

# manage.py test tests.massmail.views.test_message_copy --keepdb


@tag('TestCase')
class TestCopyMessage(BaseTestCase):
    """Massmail message copy test"""

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_message_copy(self):
        username_list = ("Andrew.Manager.Global",
                         "Darian.Manager.Co-worker.Head.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        owner = users.get(username="Andrew.Manager.Global")
        new_owner = users.get(
            username="Darian.Manager.Co-worker.Head.Global")
        subject = f"Happy New Year {random()}"
        message = EmlMessage.objects.create(
            subject=subject,
            content="Test content",
            owner=owner,
            department_id=get_department_id(owner)
        )
        change_url = reverse(
            'site:massmail_emlmessage_change', args=(message.id,))
        self.client.force_login(new_owner)
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertIn(subject, response.rendered_content)
        copy_url = reverse("copy_message", args=(message.id,))
        response = self.client.get(copy_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertIn(subject, response.rendered_content)
        try:
            new_message = EmlMessage.objects.get(
                subject=subject,
                owner=new_owner
            )
            new_change_url = reverse(
                'site:massmail_emlmessage_change', args=(new_message.id,))
            self.assertEqual(new_change_url, response.redirect_chain[-1][0])
        except EmlMessage.DoesNotExist as err:
            self.fail(err)

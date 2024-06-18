from django.conf import settings
from django.contrib.auth.models import Group
from django.test import TestCase

from common.utils.helpers import save_message, USER_MODEL


# manage.py test tests.common.utils.test_save_message --keepdb


class TestSaveMessage(TestCase):

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_save_message(self):
        Group.objects.create(name='co-workers')
        user = USER_MODEL.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        msg = "Message for store in the user profile."
        save_message(user, msg)
        self.client.force_login(user)
        url = f"/{settings.SECRET_CRM_PREFIX}"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertContains(response, msg, status_code=200, html=False)

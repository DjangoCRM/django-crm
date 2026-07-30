"""Unit tests for common.services.notifications."""

from django.conf import settings
from django.contrib.auth.models import Group
from django.core import mail
from django.test import RequestFactory
from django.test import TestCase

from common.services.notifications import save_message
from common.services.notifications import send_crm_email
from common.services.notifications import set_toggle_tooltip
from common.utils.helpers import USER_MODEL


class NotificationServiceTests(TestCase):
    def test_save_message_delegates_to_user_profile(self):
        Group.objects.create(name='co-workers')
        user = USER_MODEL.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        save_message(user, 'Stored message', 'INFO')
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.messages[-2], 'Stored message')

    def test_send_crm_email_uses_test_outbox(self):
        send_crm_email('Subject', '<p>Body</p>', ['user@example.com'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Subject')
        mail.outbox.clear()

    def test_set_toggle_tooltip_respects_session_key(self):
        request = RequestFactory().get('/')
        request.session = {}
        context = {}
        set_toggle_tooltip('tasks', request, context)
        self.assertIn('toggle_title', context)

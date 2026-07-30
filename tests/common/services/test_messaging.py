"""Unit tests for common.services.messaging."""

from types import SimpleNamespace

from django.test import SimpleTestCase
from django.utils.safestring import SafeString

from common.services.messaging import compose_message
from common.services.messaging import compose_subject


class MessagingServiceTests(SimpleTestCase):
    def test_compose_message_wraps_html_link(self):
        obj = SimpleNamespace(
            name='Acme deal',
            get_absolute_url=lambda: '/crm/deal/1/',
        )
        message = compose_message(obj, 'Updated')
        self.assertIsInstance(message, SafeString)
        self.assertIn('Acme deal', message)
        self.assertIn('/crm/deal/1/', message)

    def test_compose_subject_includes_username_when_provided(self):
        obj = SimpleNamespace(name='Line1\nLine2', request_for='')
        user = SimpleNamespace(username='john.doe')
        subject = compose_subject(obj, 'Reminder', user=user)
        self.assertIn('john.doe', subject)
        self.assertIn('CRM: Reminder', subject)

    def test_compose_subject_without_user(self):
        obj = SimpleNamespace(name='Task', request_for='')
        subject = compose_subject(obj, 'Closed')
        self.assertEqual(subject, 'CRM: Closed - Task')

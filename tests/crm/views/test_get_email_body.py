from django.test import tag

from common.utils.helpers import USER_MODEL
from crm.views.view_original_email import get_context
from massmail.models.email_account import EmailAccount
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_email_message, attach_file_to_email_msg

# manage.py test tests.crm.views.test_get_email_body --keepdb


@tag('TestCase')
class TestGetEmailBody(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.ea = EmailAccount.objects.create(
            name='CRM Email Account',
            email_host='smtp.example.com',
            email_port=587,
            email_host_user='andrew@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            owner=cls.owner,
        )

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.msg, self.content, self.subject_str = get_email_message()

    def test_get_email_body(self):
        context, err = get_context(self.msg)
        self.assertEqual('', err)
        self.assertIn(self.content, context['body'])
        self.assertEqual([], context['attachments'])

    def test_get_email_body_with_file(self):
        file_name = attach_file_to_email_msg(self.msg)
        context, err = get_context(self.msg)
        self.assertEqual('', err)
        self.assertIn(self.content, context['body'])
        self.assertEqual([file_name], context['attachments'])

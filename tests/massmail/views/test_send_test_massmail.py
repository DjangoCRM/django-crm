from django.core import mail
from django.test import tag
from django.urls import reverse
from django.utils.translation import gettext as _

from common.utils.helpers import USER_MODEL
from massmail.models.email_account import EmailAccount
from massmail.models.email_message import EmlMessage
from massmail.models.signature import Signature
from massmail.views.send_tests import NEED_TWO_EML_ACCOUNTS
from tests.base_test_classes import BaseTestCase

# manage.py test tests.massmail.views.test_send_test_massmail --keepdb


@tag('TestCase')
class TestSendTestMassMil(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.department = cls.owner.groups.filter(
            department__isnull=False
        ).first()
        cls.ea = EmailAccount.objects.create(
            name='Email Account',
            email_host='smtp.example.com',
            email_host_user='andrew@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            owner=cls.owner,
        )
        cls.signature = Signature.objects.create(
            name="Test signature",
            type='Plain text',
            content="Test signature",
            default=True,
            owner=cls.owner
        )
        cls.eml = EmlMessage.objects.create(
            subject="Test email",
            content="content",
            signature=cls.signature,
            is_html=False,
            owner=cls.owner,
            department=cls.department
        )
        cls.change_eml_url = reverse(
            'site:massmail_emlmessage_change', args=(cls.eml.id,))
        cls.send_test_url = reverse('send_test', args=(cls.eml.id,))

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.owner)

    def test_send_with_one_eml_account(self):
        response = self.client.get(self.send_test_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(0, len(mail.outbox))
        mail.outbox = []
        self.assertEqual(self.change_eml_url, response.redirect_chain[-1][0])
        self.assertContains(response, _(NEED_TWO_EML_ACCOUNTS))

    def test_send_test_massmail(self):
        EmailAccount.objects.create(
            name='Email Account 2',
            email_host='smtp.example.com',
            email_host_user='andrew2@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            owner=self.owner,
        )
        response = self.client.get(self.send_test_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(self.eml.subject, mail.outbox[0].subject)
        self.assertEqual(self.change_eml_url, response.redirect_chain[-1][0])
        mail.outbox = []

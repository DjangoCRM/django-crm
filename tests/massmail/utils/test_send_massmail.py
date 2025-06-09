from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import tag
from django.urls import reverse
from django.utils.translation import gettext as _

from crm.models import Lead
from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from massmail.models.email_account import EmailAccount
from massmail.models.eml_accounts_queue import EmlAccountsQueue
from massmail.models.email_message import EmlMessage
from massmail.models.mass_contact import MassContact
from massmail.models.mailing_out import MailingOut
from massmail.models.signature import Signature
from massmail.utils.sendmassmail import send_massmail
from settings.models import MassmailSettings
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials

# manage.py test tests.massmail.utils.test_send_massmail --keepdb
# It's complicated to test with TransactionTestCase


@tag('TestCase')
class TestMassMil(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.ea = EmailAccount.objects.create(
            name='Email Account',
            email_host='smtp.example.com',
            email_port=587,
            email_host_user='andrew@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            main=True,
            massmail=True,
            owner=cls.owner,
        )
        cls.ea2 = EmailAccount.objects.create(
            name='Email Account 2',
            email_host='smtp.example.com',
            email_port=587,
            email_host_user='andrew2@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            main=False,
            massmail=True,
            owner=cls.owner,
        )
        queue = EmlAccountsQueue(
            owner=cls.owner,
        )
        queue.add_id(cls.ea2.id)
        queue.add_id(cls.ea.id)
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
            is_html=False
        )
        cls.lead1 = Lead.objects.create(
            first_name='Bruno',
            email='Bruno@company.com',
            phone='+0182345678',
            company_name='Bruno Company LLC',
            owner=cls.owner
        )
        cls.lead2 = Lead.objects.create(
            first_name='Michael',
            email='Michael@testcompany.com',
            phone='+0182345678',
        )
        cls.lead_content_type = ContentType.objects.get_for_model(Lead)
        cls.mc = MassContact.objects.create(
            content_type=cls.lead_content_type,
            object_id=cls.lead1.id,
            email_account=cls.ea,
            massmail=True
        )
        cls.massmail_settings = MassmailSettings.objects.get(id=1)

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.mo = MailingOut.objects.create(
            name="Test Mailing Out",
            message=self.eml,
            status='A',
            content_type=self.lead_content_type,
            recipients_number=1,
            recipient_ids=f"{self.lead1.id},{self.lead2.id}",
            owner=self.owner,
            department_id=get_department_id(self.owner)
        )

    def test_send_2_recipient(self):
        # with self.settings(TESTING=True):
        send_massmail(self.massmail_settings)
        self.assertEqual(2, len(mail.outbox))   # NOQA
        self.assertEqual(self.eml.subject, mail.outbox[0].subject)
        mail.outbox = []

    def test_send_without_message(self):
        self.client.force_login(self.owner)
        change_url = reverse(
            "site:massmail_mailingout_change", args=(self.mo.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        del data['message']
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        errors = response.context['adminform'].form.errors
        self.assertEqual(errors['message'][0], _('This field is required.'))

    def test_file_not_found_error(self):
        eml = EmlMessage.objects.create(
            subject="Test email",
            content="<img src='{% cid_media 'mail/company-logo.png'%}'",
            signature=self.signature,
            is_html=False
        )
        self.mo.message = eml
        self.mo.save(update_fields=['message'])
        # with self.settings(TESTING=True):
        send_massmail(self.massmail_settings)
        self.mo.refresh_from_db()
        self.assertEqual(0, len(mail.outbox))   # NOQA
        mail.outbox = []
        self.assertEqual('E', self.mo.status)

from datetime import datetime
from pathlib import Path
from unittest import mock

from django.core import mail
from django.test import override_settings, tag
from django.contrib.contenttypes.models import ContentType

from common.queries import get_department_id
from crm.models import Lead
from crm.utils.crm_imap import CrmIMAP
from common.utils.helpers import USER_MODEL
from massmail.models import EmailAccount, EmlMessage, MailingOut, MassContact, Signature
from massmail.utils.sendmassmail import report as massmail_report
from sharedkernel.credentials import CREDENTIAL_MASK
from tests.base_test_classes import BaseTestCase
from tests.fixtures.mail_diagnostics_sentinels import (
    SENTINEL_APP_PASSWORD,
    SENTINEL_HOST_PASSWORD,
    SENTINEL_PII_BODY,
)


FIXTURES_DIR = Path(__file__).resolve().parents[1] / 'fixtures'


@tag('TestCase')
@override_settings(
    ADMINS=[('Admin', 'admin@example.com')],
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
)
class MailDiagnosticsIntegrationTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = USER_MODEL.objects.get(username='Andrew.Manager.Global')
        cls.account = EmailAccount.objects.create(
            name='Diagnostics account',
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_host_user='diagnostics@example.com',
            email_host_password=SENTINEL_HOST_PASSWORD,
            email_app_password=SENTINEL_APP_PASSWORD,
            from_email='diagnostics@example.com',
            owner=cls.owner,
            department_id=get_department_id(cls.owner),
        )
        cls.signature = Signature.objects.create(
            name='Diagnostics signature',
            type='Plain text',
            content='Signature',
            default=True,
            owner=cls.owner,
        )
        cls.eml = EmlMessage.objects.create(
            subject='Diagnostics message',
            content='content',
            signature=cls.signature,
            is_html=False,
            owner=cls.owner,
        )
        cls.lead = Lead.objects.create(
            first_name='Jane',
            last_name='Example',
            email='jane@example.com',
            company_name='Example LLC',
            owner=cls.owner,
        )
        cls.lead_content_type = ContentType.objects.get_for_model(Lead)
        cls.imap_fixture = (
            FIXTURES_DIR / 'mail_diagnostics_imap_response.txt'
        ).read_text()
        cls.mime_fixture = (
            FIXTURES_DIR / 'mail_diagnostics_sample.eml'
        ).read_bytes()

    def setUp(self):
        mail.outbox.clear()

    @mock.patch('crm.utils.crm_imap.imaplib.IMAP4_SSL')
    def test_imap_connect_failure_email_contains_no_sentinels(self, mock_imap):
        mock_imap.side_effect = RuntimeError(
            f'connection failed after LOGIN {SENTINEL_HOST_PASSWORD}'
        )
        crmimap = CrmIMAP(self.account.email_host_user)
        crmimap.ea = self.account
        crmimap._connect()

        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        self.assertNotIn(SENTINEL_HOST_PASSWORD, body)
        self.assertNotIn(SENTINEL_APP_PASSWORD, body)
        self.assertIn('Account id: {}'.format(self.account.pk), body)

    def test_massmail_report_stores_sanitized_account_report(self):
        mailing_out = MailingOut.objects.create(
            name='Diagnostics mailing',
            message=self.eml,
            status='A',
            owner=self.owner,
            content_type=self.lead_content_type,
            recipients_number=1,
            recipient_ids=str(self.lead.pk),
            department_id=get_department_id(self.owner),
        )
        mc = MassContact.objects.create(
            content_type=self.lead_content_type,
            object_id=self.lead.pk,
            email_account=self.account,
        )
        error = RuntimeError(
            f'SMTP auth failed PASS {SENTINEL_HOST_PASSWORD} {SENTINEL_PII_BODY}'
        )

        massmail_report(
            self.account,
            mailing_out,
            mc,
            datetime.now(),
            error,
            off=True,
        )

        self.account.refresh_from_db()
        self.assertNotIn(SENTINEL_HOST_PASSWORD, self.account.report)
        self.assertIn(CREDENTIAL_MASK, self.account.report)
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotIn(SENTINEL_HOST_PASSWORD, mail.outbox[0].body)

    def test_fixture_secrets_are_masked_by_sanitizer(self):
        from sharedkernel.mail_diagnostics import sanitize_text, summarize_payload

        sanitized = sanitize_text(self.imap_fixture)
        self.assertNotIn(SENTINEL_HOST_PASSWORD, sanitized)
        self.assertNotIn(SENTINEL_APP_PASSWORD, sanitized)

        mime_summary = summarize_payload(self.mime_fixture, content_type='message/rfc822')
        self.assertEqual(mime_summary['payload_bytes'], len(self.mime_fixture))
        self.assertNotIn(SENTINEL_PII_BODY, str(mime_summary))

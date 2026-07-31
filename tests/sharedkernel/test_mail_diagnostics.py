from django.core.cache import cache
from django.core import mail
from django.test import SimpleTestCase, TestCase, override_settings

from sharedkernel.credentials import CREDENTIAL_MASK
from sharedkernel.mail_diagnostics import (
    build_incident_summary,
    report_mail_incident,
    sanitize_text,
    summarize_payload,
)
from tests.fixtures.mail_diagnostics_sentinels import (
    SENTINEL_APP_PASSWORD,
    SENTINEL_HOST_PASSWORD,
    SENTINEL_REFRESH_TOKEN,
)


class SanitizeTextTests(SimpleTestCase):
    def test_masks_protocol_and_token_patterns(self):
        cases = [
            (
                f'LOGIN user@example.com {SENTINEL_HOST_PASSWORD}',
                SENTINEL_HOST_PASSWORD,
            ),
            (
                f'AUTHENTICATE PLAIN {SENTINEL_APP_PASSWORD}',
                SENTINEL_APP_PASSWORD,
            ),
            (
                f'PASS {SENTINEL_HOST_PASSWORD}',
                SENTINEL_HOST_PASSWORD,
            ),
            (
                f'refresh_token={SENTINEL_REFRESH_TOKEN}',
                SENTINEL_REFRESH_TOKEN,
            ),
            (
                'access_token=oauth-access-token-value',
                'oauth-access-token-value',
            ),
            (
                'client_secret=oauth-client-secret-value',
                'oauth-client-secret-value',
            ),
            (
                f'email_host_password={SENTINEL_HOST_PASSWORD}',
                SENTINEL_HOST_PASSWORD,
            ),
        ]
        for raw, secret in cases:
            with self.subTest(raw=raw):
                sanitized = sanitize_text(raw)
                self.assertIn(CREDENTIAL_MASK, sanitized)
                self.assertNotIn(secret, sanitized)


class SummarizePayloadTests(SimpleTestCase):
    def test_summarize_bytes_without_content(self):
        metadata = summarize_payload(
            b'secret-bytes',
            folder='INBOX',
            uid='42',
            content_type='message/rfc822',
        )
        self.assertEqual(metadata['payload_bytes'], len(b'secret-bytes'))
        self.assertEqual(metadata['folder'], 'INBOX')
        self.assertEqual(metadata['uid'], '42')
        self.assertNotIn('secret-bytes', str(metadata))


@override_settings(
    ADMINS=[('Admin', 'admin@example.com')],
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    MAIL_DIAGNOSTICS_DEDUP_SECONDS=300,
)
class ReportMailIncidentTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()

    def test_report_mail_incident_sends_one_admin_email_per_window(self):
        for _ in range(3):
            report_mail_incident(
                account=None,
                operation='imap_connect',
                exception=RuntimeError(SENTINEL_HOST_PASSWORD),
                context={'account_id': 9001, 'owner_id': 1},
                subject='Mail incident test',
            )

        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        self.assertNotIn(SENTINEL_HOST_PASSWORD, body)
        self.assertIn('Occurrence count: 3', body)

    def test_build_incident_summary_includes_required_fields(self):
        summary = build_incident_summary(
            account_id=9001,
            owner_id=1,
            operation='imap_execute:LOGIN',
            exception_class='RuntimeError',
            exception_summary='login failed',
            context={
                'folder': 'INBOX',
                'uid': '7',
                'payload': summarize_payload(b'0123456789'),
            },
            occurrence_count=1,
        )
        self.assertIn('Account id: 9001', summary)
        self.assertIn('Owner id: 1', summary)
        self.assertIn('Operation: imap_execute:LOGIN', summary)
        self.assertIn('folder: INBOX', summary)
        self.assertIn('payload: payload_bytes=10', summary)
        self.assertIn('uid: 7', summary)

"""URL stability tests for views relocated out of common."""

from django.conf import settings
from django.test import SimpleTestCase
from django.test import tag
from django.urls import reverse


RELOCATED_URL_NAMES = {
    'select_emails_import_request': f'/en/{settings.SECRET_CRM_PREFIX}select-emails-import/request/',
    'select_email_account': f'/en/{settings.SECRET_CRM_PREFIX}select-email-account/',
    'user_transfer': f'/en/{settings.SECRET_CRM_PREFIX}user-transfer/',
    'export_objects': f'/en/{settings.SECRET_CRM_PREFIX}export-objects/',
}


@tag('TestCase')
class RelocatedViewUrlTests(SimpleTestCase):
    def test_relocated_url_names_reverse_to_same_paths(self):
        for name, expected_path in RELOCATED_URL_NAMES.items():
            with self.subTest(name=name):
                self.assertEqual(reverse(name), expected_path)

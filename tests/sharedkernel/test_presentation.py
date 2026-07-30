"""Direct tests for sharedkernel.presentation symbols.

No new JSON fixtures are required — these helpers are pure formatting utilities.
"""

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.utils.functional import Promise
from django.utils.safestring import SafeString

from sharedkernel import presentation


class SharedKernelPresentationTests(SimpleTestCase):
    def test_constants_import_cleanly(self):
        self.assertIsInstance(presentation.COPY_STR, Promise)
        self.assertIsInstance(presentation.SAFE_ATTACH_FILE_ICON, SafeString)
        self.assertEqual(presentation.LEADERS, '- - - -')

    def test_popup_window_handles_empty_window_name(self):
        result = presentation.popup_window('https://example.test/empty', '')
        self.assertIn('WindowName', result)

    def test_get_verbose_name_with_non_ascii_field_label(self):
        user_model = get_user_model()
        field = user_model._meta.get_field('first_name')
        expected = str(field.verbose_name)
        title = presentation.get_verbose_name(user_model, 'first_name')
        self.assertEqual(title, expected)

    def test_get_formatted_short_date_returns_string(self):
        value = presentation.get_formatted_short_date()
        self.assertIsInstance(value, str)
        self.assertTrue(value)

    def test_crm_notice_contains_message_icon(self):
        self.assertIn('message', presentation.CRM_NOTICE)

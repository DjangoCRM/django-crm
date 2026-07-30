"""Characterization tests for presentation symbols re-exported from helpers.

These tests import through ``common.utils.helpers`` to ensure the compatibility
shim preserves byte-identical constants and formatter output. Existing JSON
fixtures are reused; no new fixtures are required for these pure helpers.
"""

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.utils.functional import Promise
from django.utils.safestring import SafeString

from common.utils import helpers


class HelpersPresentationCharacterizationTests(SimpleTestCase):
    def test_copy_constants_are_unchanged(self):
        self.assertEqual(str(helpers.COPY_STR), 'Copy')
        self.assertEqual(
            helpers.CONTENT_COPY_ICON,
            '<i class="material-icons"style="font-size: 17px;vertical-align: middle;">content_copy</i>',
        )
        self.assertEqual(helpers.CONTENT_COPY_LINK, '<a href="{}" title="{}">{}</a>')
        self.assertEqual(helpers.LEADERS, '- - - -')
        self.assertEqual(
            helpers.ONCLICK_STR,
            "window.open('{}', '{}','width=800,height=700'); return false;",
        )

    def test_mark_safe_icons_are_safe_strings(self):
        self.assertIsInstance(helpers.SAFE_ATTACH_FILE_ICON, SafeString)
        self.assertIsInstance(helpers.SAFE_SUBJECT_ICON, SafeString)
        self.assertIn('attach_file', helpers.SAFE_ATTACH_FILE_ICON)
        self.assertIn('subject', helpers.SAFE_SUBJECT_ICON)

    def test_lazy_translation_objects_remain_lazy(self):
        self.assertIsInstance(helpers.COPY_STR, Promise)
        self.assertIsInstance(helpers.OBJ_DOESNT_EXIT_STR, Promise)
        self.assertIsInstance(helpers.FRIDAY_SATURDAY_SUNDAY_MSG, Promise)

    def test_popup_window_default_and_named_window(self):
        self.assertEqual(
            helpers.popup_window('https://example.test/view'),
            "window.open('https://example.test/view', 'WindowName','width=800,height=700'); return false;",
        )
        self.assertEqual(
            helpers.popup_window('https://example.test/view', 'MailWin'),
            "window.open('https://example.test/view', 'MailWin','width=800,height=700'); return false;",
        )

    def test_get_formatted_short_date_matches_sharedkernel(self):
        from sharedkernel import presentation

        self.assertEqual(
            helpers.get_formatted_short_date(),
            presentation.get_formatted_short_date(),
        )

    def test_get_verbose_name_for_user_username(self):
        user_model = get_user_model()
        field = user_model._meta.get_field('username')
        expected = str(field.verbose_name)
        self.assertEqual(
            helpers.get_verbose_name(user_model, 'username'),
            expected,
        )

    def test_obj_does_not_exist_string_formatting(self):
        message = str(helpers.OBJ_DOESNT_EXIT_STR).format('Deal', '42')
        self.assertIn('Deal', message)
        self.assertIn('42', message)

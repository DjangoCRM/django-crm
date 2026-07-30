"""Unit tests for common.services.translations."""

from django.contrib.auth.models import Group
from django.test import TestCase

from common.services.translations import get_trans_for_lang
from common.services.translations import get_trans_for_user
from common.services.translations import get_user_language_code
from common.utils.helpers import USER_MODEL


class TranslationServiceTests(TestCase):
    def test_get_trans_for_lang_returns_string(self):
        translated = get_trans_for_lang('Hello', 'en')
        self.assertEqual(translated, 'Hello')

    def test_get_user_language_code_falls_back_to_settings(self):
        Group.objects.create(name='co-workers')
        user = USER_MODEL.objects.create_user('jane', 'jane@example.com', 'pass')
        self.assertTrue(get_user_language_code(user))

    def test_get_trans_for_user_uses_profile_language(self):
        Group.objects.create(name='co-workers')
        user = USER_MODEL.objects.create_user('jane', 'jane@example.com', 'pass')
        user.profile.language_code = 'en'
        user.profile.save(update_fields=['language_code'])
        self.assertEqual(get_trans_for_user('Hello', user), 'Hello')

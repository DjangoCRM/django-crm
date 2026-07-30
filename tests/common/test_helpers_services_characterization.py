"""Characterization tests for workflow services re-exported from helpers."""

from types import SimpleNamespace

from django.test import tag

from common.services import datetimes
from common.services import messaging
from common.services import notifications
from common.services import tokens
from common.services import translations
from common.utils import helpers
from tests.base_test_classes import BaseTestCase


@tag('TestCase')
class HelpersServicesCharacterizationTests(BaseTestCase):
    def test_compose_subject_matches_service(self):
        obj = SimpleNamespace(name='Deal', request_for='')
        user = SimpleNamespace(username='owner')
        self.assertEqual(
            helpers.compose_subject(obj, 'Notice', user=user),
            messaging.compose_subject(obj, 'Notice', user=user),
        )

    def test_datetime_helpers_match_service(self):
        self.assertEqual(helpers.get_today(), datetimes.get_today())
        self.assertEqual(helpers.get_delta_date(2), datetimes.get_delta_date(2))

    def test_translation_helpers_match_service(self):
        user = helpers.USER_MODEL.objects.get(username='Adam.Admin')
        text = 'Hello CRM'
        self.assertEqual(
            helpers.get_trans_for_lang(text, 'en'),
            translations.get_trans_for_lang(text, 'en'),
        )
        self.assertEqual(
            helpers.get_user_language_code(user),
            translations.get_user_language_code(user),
        )

    def test_token_default_matches_service(self):
        self.assertEqual(len(helpers.token_default()), len(tokens.token_default()))

    def test_send_crm_email_symbol_is_shared(self):
        self.assertIs(helpers.send_crm_email, notifications.send_crm_email)

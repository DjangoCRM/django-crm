"""Tests for the common.utils.helpers deprecation shim."""

import importlib
import sys
import warnings

from django.test import SimpleTestCase

import common.queries
import common.services.datetimes
import common.services.messaging
import common.services.notifications
import common.services.tokens
import common.services.translations
import sharedkernel.presentation


class HelpersShimTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self._reload_helpers()

    def tearDown(self):
        self._reload_helpers()
        super().tearDown()

    @staticmethod
    def _reload_helpers():
        module_name = 'common.utils.helpers'
        if module_name in sys.modules:
            del sys.modules[module_name]
        importlib.import_module(module_name)

    def test_importing_module_is_silent(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', DeprecationWarning)
            importlib.import_module('common.utils.helpers')
        self.assertEqual(
            [warning for warning in caught if issubclass(warning.category, DeprecationWarning)],
            [],
        )

    def test_accessing_moved_symbol_warns_once(self):
        helpers_module = importlib.import_module('common.utils.helpers')
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', DeprecationWarning)
            first = helpers_module.annotate_chat
            second = helpers_module.annotate_chat
        shim_warnings = [
            warning for warning in caught if issubclass(warning.category, DeprecationWarning)
        ]
        self.assertEqual(len(shim_warnings), 1)
        message = str(shim_warnings[0].message)
        self.assertIn('common.utils.helpers.annotate_chat', message)
        self.assertIn('common.queries.annotate_chat', message)
        self.assertIn('3.0.0', message)
        self.assertIs(first, second)
        self.assertIs(first, common.queries.annotate_chat)

    def test_moved_symbols_match_canonical_modules(self):
        cases = (
            ('annotate_chat', common.queries),
            ('get_formatted_short_date', sharedkernel.presentation),
            ('compose_subject', common.services.messaging),
            ('get_today', common.services.datetimes),
            ('send_crm_email', common.services.notifications),
            ('token_default', common.services.tokens),
            ('get_trans_for_lang', common.services.translations),
        )
        helpers_module = importlib.import_module('common.utils.helpers')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            for name, canonical_module in cases:
                with self.subTest(name=name):
                    self.assertIs(
                        getattr(helpers_module, name),
                        getattr(canonical_module, name),
                    )

    def test_unknown_name_raises_attribute_error_without_warning(self):
        helpers_module = importlib.import_module('common.utils.helpers')
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', DeprecationWarning)
            with self.assertRaises(AttributeError):
                getattr(helpers_module, 'not_a_legacy_helper')
        self.assertEqual(
            [warning for warning in caught if issubclass(warning.category, DeprecationWarning)],
            [],
        )

    def test_user_model_is_available_without_warning(self):
        helpers_module = importlib.import_module('common.utils.helpers')
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', DeprecationWarning)
            user_model = helpers_module.USER_MODEL
        from django.contrib.auth import get_user_model

        self.assertIs(user_model, get_user_model())
        self.assertEqual(
            [warning for warning in caught if issubclass(warning.category, DeprecationWarning)],
            [],
        )

    def test_star_import_resolves_legacy_names(self):
        namespace = {}
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            exec('from common.utils.helpers import *', namespace)
        self.assertIn('annotate_chat', namespace)
        self.assertIn('token_default', namespace)

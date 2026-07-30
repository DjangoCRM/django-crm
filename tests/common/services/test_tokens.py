"""Unit tests for common.services.tokens."""

from django.test import SimpleTestCase

from common.services.tokens import token_default
from common.utils import helpers


class TokenServiceTests(SimpleTestCase):
    def test_token_default_generates_urlsafe_string(self):
        token = token_default()
        self.assertEqual(len(token), 11)

    def test_helpers_reexport_matches_service(self):
        self.assertIs(helpers.token_default, token_default)

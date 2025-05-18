
from datetime import datetime as dt
from unittest.mock import patch, MagicMock
from django.conf import settings
from django.test import TestCase
from django.utils.module_loading import import_string
import requests
from requests.exceptions import JSONDecodeError, HTTPError, RequestException

# manage.py test tests.crm.backends.test_currency_rate_backend
MARKETING_CURRENCY = 'USD'


class TestCurrencyRateBackend(TestCase):

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)
        if not settings.LOAD_RATE_BACKEND:
            self.skipTest("LOAD_RATE_BACKEND is not set in settings.")
        try:
            self.be = import_string(settings.LOAD_RATE_BACKEND)
        except ImportError:
            self.fail(f"Failed to import backend: {settings.LOAD_RATE_BACKEND}")


    def test_currency_rate_backend(self):
        # NOTE: This test depends on settings.LOAD_EXCHANGE_RATE = True and a valid LOAD_RATE_BACKEND.
        # It might perform a live API call if not mocked.
        # Consider mocking if live calls are undesirable.
        if not settings.LOAD_EXCHANGE_RATE:
            self.skipTest("LOAD_EXCHANGE_RATE is False in settings. Skipping live test.")

        today = dt.now().date()
        state_currency = self.be.get_state_currency()

        warning_msg = "Warning: Live API call in test_currency_rate_backend failed: {}"
        currencies = (state_currency, MARKETING_CURRENCY)
        for currency in currencies:
            backend = self.be(currency, MARKETING_CURRENCY, today)
            rate_to_state_currency, rate_to_marketing_currency, error = backend.get_rates()

            if error:
                print(warning_msg.format(error))
                self.assertNotEqual('', error)
            else:
                if state_currency != MARKETING_CURRENCY:
                    if currency == state_currency:
                        self.assertEqual(rate_to_state_currency, 1)
                        self.assertIsInstance(rate_to_marketing_currency, (float, int))
                    else:
                        self.assertEqual(rate_to_marketing_currency, 1)
                        self.assertIsInstance(rate_to_state_currency, (float, int))
                else:
                    self.assertEqual(rate_to_state_currency, 1)
                    self.assertEqual(rate_to_marketing_currency, 1)

    @patch('crm.backends.bank_gov_ua_backend.requests.get')
    def test_currency_rate_backend_json_error(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = 'invalid json'
        mock_response.json.side_effect = JSONDecodeError("Expecting value", mock_response.text, 0)
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        backend = self.be('EUR', MARKETING_CURRENCY, dt.now().date())
        rate_to_state_currency, rate_to_marketing_currency, error = backend.get_rates()

        self.assertIn("Failed to decode JSON response from API", error)
        self.assertIn("Status: 200", error)
        self.assertIn("Response text: invalid json", error)
        self.assertEqual(rate_to_state_currency, 1)
        self.assertEqual(rate_to_marketing_currency, 1)

    @patch('crm.backends.bank_gov_ua_backend.requests.get')
    def test_currency_rate_backend_http_error(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        http_error = HTTPError("500 Server Error", response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        backend = self.be('EUR', MARKETING_CURRENCY, dt.now().date())
        rate_to_state_currency, rate_to_marketing_currency, error = backend.get_rates()

        self.assertIn("API request failed", error)
        self.assertIn("500 Server Error", error)
        self.assertEqual(rate_to_state_currency, 1)
        self.assertEqual(rate_to_marketing_currency, 1)

    @patch('crm.backends.bank_gov_ua_backend.requests.get')
    def test_currency_rate_backend_request_exception(self, mock_get):
        mock_get.side_effect = RequestException("Connection timed out")

        backend = self.be('EUR', MARKETING_CURRENCY, dt.now().date())
        rate_to_state_currency, rate_to_marketing_currency, error = backend.get_rates()

        self.assertIn("API request failed", error)
        self.assertIn("Connection timed out", error)
        self.assertEqual(rate_to_state_currency, 1)
        self.assertEqual(rate_to_marketing_currency, 1)

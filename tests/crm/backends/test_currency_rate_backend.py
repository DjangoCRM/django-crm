from datetime import datetime as dt
from django.conf import settings
from django.test import TestCase
from django.utils.module_loading import import_string


# manage.py test tests.crm.backends.test_currency_rate_backend
MARKETING_CURRENCY = 'USD'


class TestCurrencyRateBackend(TestCase):

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_currency_rate_backend(self):
        if not any((settings.LOAD_EXCHANGE_RATE, settings.LOAD_RATE_BACKEND)):
            print("Test `CurrencyRateBackend` skipped due to settings.")
            return
        be = import_string(settings.LOAD_RATE_BACKEND)
        today = dt.now().date()
        state_currency = be.get_state_currency()
        if state_currency != MARKETING_CURRENCY:
            backend = be(state_currency, MARKETING_CURRENCY, today)
            rate_to_state_currency, rate_to_marketing_currency, error = backend.get_rates()
            self.assertEqual('', error)
            self.assertEqual(rate_to_state_currency, 1)
            self.assertEqual(type(rate_to_marketing_currency), float)

            backend = be(MARKETING_CURRENCY, MARKETING_CURRENCY, today)
            rate_to_state_currency, rate_to_marketing_currency, error = backend.get_rates()
            self.assertEqual('', error)
            self.assertEqual(rate_to_marketing_currency, 1)
            self.assertEqual(type(rate_to_state_currency), float)

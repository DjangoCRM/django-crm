import requests
from requests.exceptions import JSONDecodeError
from typing import Union
from datetime import date
from django.utils.formats import date_format

from crm.backends.basebackend import BaseBackend

STATE_CURRENCY = 'UAH'


class BankGovUaBackend(BaseBackend):

    @classmethod
    def get_state_currency(cls):
        return STATE_CURRENCY

    def __init__(self, currency: str, marketing_currency: str = 'USD',
                 rate_date: Union[date, None] = None):
        self.url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchangenew"
        self.date_format = "Ymd"
        self.error = ''
        self.state_currency = self.get_state_currency()
        self.currency = currency
        self.marketing_currency = marketing_currency
        self.rate_date = rate_date if rate_date else date.today() # Ensure rate_date is set
        self.data = self.get_data(marketing_currency)
        self.marketing_currency_rate = self.get_marketing_currency_rate()

    def get_data(self, currency: str = 'USD') -> list:
        date_str = date_format(self.rate_date, format=self.date_format, use_l10n=False)
        params = {'date': date_str, 'valcode': currency, 'json': ''}
        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except JSONDecodeError:
            self.error = f"Failed to decode JSON response from API. Status: {response.status_code}. Response text: {response.text[:100]}"
            return []
        except requests.exceptions.RequestException as e: # Catch other request errors (timeout, connection error)
            self.error = f"API request failed: {e}"
            return []

    def _extract_rate(self, data: list, currency_code: str):
        """Private helper to extract rate from API data list."""
        if not data:
            # self.error should be set by get_data if data is empty
            return 1 # Return default rate
        try:
            return data[0]['rate']
        except (IndexError, KeyError, TypeError) as e:
            self.error = f"Error processing API data for {currency_code}: {e}. Data received: {data}"
            return 1

    def get_marketing_currency_rate(self):
        # Uses the initially fetched data (self.data)
        return self._extract_rate(self.data, self.marketing_currency)

    def get_rate_to_state_currency(self, currency: str = 'USD'):
        # If initial marketing currency fetch already had issues, return default
        if self.error and not self.data:
            return 1

        # If querying the same currency as marketing, use the already fetched data
        if currency == self.marketing_currency:
            return self._extract_rate(self.data, self.marketing_currency)

        # Fetch data for the specific currency if different from marketing
        # Note: this resets self.error if the specific fetch fails
        specific_data = self.get_data(currency)
        return self._extract_rate(specific_data, currency)
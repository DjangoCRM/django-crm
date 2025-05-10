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
        self.rate_date = rate_date if rate_date else date.today()
        self.data = self.get_data(marketing_currency)
        self.marketing_currency_rate = self.get_marketing_currency_rate()

    def get_data(self, currency: str = 'USD') -> list:
        date_str = date_format(self.rate_date, format=self.date_format, use_l10n=False)
        params = {'date': date_str, 'valcode': currency, 'json': ''}
        try:
            response = requests.get(self.url, params=params)
            response.raise_for_status()
            return response.json()
        except JSONDecodeError:
            self.error = f"Failed to decode JSON response from API. Status: {response.status_code}. Response text: {response.text[:100]}"
            return []
        except requests.exceptions.RequestException as e:
            self.error = f"API request failed: {e}"
            return []

    def extract_rate_from_data(self, data: list, currency_code: str):
        """Extracts rate from API data list, handles errors, returns 1 on failure."""
        if self.error:
            return 1
        try:
            return data[0]['rate']
        except (IndexError, KeyError, TypeError) as e:
            self.error = f"Error processing API data for {currency_code}: {e}. Data received: {data}"
            return 1

    def get_marketing_currency_rate(self):
        return self.extract_rate_from_data(self.data, self.marketing_currency)

    def get_rate_to_state_currency(self, currency: str = 'USD'):
        if self.error:
            return 1


        currency_data = self.get_data(currency)
        return self.extract_rate_from_data(currency_data, currency)

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

    def get_marketing_currency_rate(self):
        # Check if data fetching failed
        if not self.data: # Data is empty list [] if fetching failed in get_data
            # self.error is already set in get_data
           return 1 # Return default rate
        try:
            return self.data[0]['rate']
        except (IndexError, KeyError, TypeError) as e: # More specific potential errors accessing data
            self.error = f"Error processing API data: {e}. Data received: {self.data}"
            return 1

    def get_rate_to_state_currency(self, currency: str = 'USD'):
        # If marketing currency rate already had issues, don't try again
        if self.error:
           return 1

        # If querying the same currency as marketing, return the already fetched rate
        if currency == self.marketing_currency:
             if not self.data: # Check if initial fetch failed
                 return 1
             try:
                 return self.data[0]['rate']
             except (IndexError, KeyError, TypeError) as e:
                 self.error = f"Error processing API data for marketing currency: {e}. Data received: {self.data}"
                 return 1

        # Fetch data for the specific currency if different from marketing
        specific_data = self.get_data(currency)
        if not specific_data : # Check if fetching failed for this specific currency
            # self.error is set within the get_data call above
            return 1
        try:
            return specific_data[0]['rate']
        except (IndexError, KeyError, TypeError) as e:
            self.error = f"Error processing API data for {currency}: {e}. Data received: {specific_data}"
            return 1

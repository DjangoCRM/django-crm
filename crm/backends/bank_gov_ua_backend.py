import requests
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
        self.url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"
        self.date_format = "Ymd"
        self.error = ''
        self.state_currency = self.get_state_currency()
        self.currency = currency
        self.marketing_currency = marketing_currency
        self.rate_date = rate_date
        self.data = self.get_data(marketing_currency)
        self.marketing_currency_rate = self.get_marketing_currency_rate()

    def get_data(self, currency: str = 'USD') -> list:
        date_str = date_format(self.rate_date, format=self.date_format, use_l10n=False)
        params = {'date': date_str, 'valcode': currency, 'json': ''}
        response = requests.get(self.url, params=params)
        return response.json()

    def get_marketing_currency_rate(self):
        try:
            return self.data[0]['rate']
        except Exception as e:
            self.error = e
            return 1

    def get_rate_to_state_currency(self, currency: str = 'USD'):
        if self.error:
            return 1
        try:
            return self.get_data(currency)[0]['rate']
        except Exception as e:
            self.error = e
            return 1

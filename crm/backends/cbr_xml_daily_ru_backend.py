import requests
from datetime import date
from django.utils.formats import date_format
from crm.backends.basebackend import BaseBackend

STATE_CURRENCY = 'RUB'


class CbrXmlDailyRuBackend(BaseBackend):
    
    @classmethod
    def get_state_currency(cls):
        return STATE_CURRENCY     

    def __init__(self, currency: str, marketing_currency: str = 'USD', 
                 rate_date: date = None):
        self.url = "https://www.cbr-xml-daily.ru/daily_json.js"
        self.date_format = "d/m/Y"
        self.error = ''
        self.state_currency = self.get_state_currency()
        self.currency = currency
        self.marketing_currency = marketing_currency
        self.rate_date = rate_date
        self.data = self.get_data(rate_date)
        self.marketing_currency_rate = self.get_marketing_currency_rate()

    def get_data(self, rate_date: date = None) -> dict:
        if rate_date:
            date_str = date_format(rate_date, format=self.date_format, use_l10n=False)
            params = {'date_req': date_str}
            response = requests.get(self.url, params=params)
        else:
            response = requests.get(self.url)
        return response.json()
    
    def get_marketing_currency_rate(self):
        try:
            return self.data['Valute'][self.marketing_currency]['Value'] / \
                self.data['Valute'][self.marketing_currency]['Nominal']
        except Exception as e:
            self.error = e
            return    

    def get_rate_to_state_currency(self, currency: str = 'USD'):
        if self.error:
            return 1
        try:
            return self.data['Valute'][currency]['Value'] / \
                self.data['Valute'][currency]['Nominal']
        except Exception as e:
            self.error = e
            return 1


"""
data = {
    'Date': '2021-05-22T11:30:00+03:00',
    'PreviousDate': '2021-05-21T11:30:00+03:00',
    'PreviousURL': '//www.cbr-xml-daily.ru/archive/2021/05/21/daily_json.js',
    'Timestamp': '2021-05-23T17:00:00+03:00', 
    'Valute': {
        'USD': {
            'ID': 'R01235',
            'NumCode': '840',
            'CharCode': 'USD',
            'Nominal': 1,
            'Name': 'Доллар США',
            'Value': 73.5803,
            'Previous': 73.6007
        }, 
        'EUR': {
            'ID': 'R01239', 'NumCode': '978', 'CharCode': 'EUR', 
            'Nominal': 1, 'Name': 'Евро', 'Value': 89.9446, 'Previous': 89.7708
        }, 
    }
}
"""

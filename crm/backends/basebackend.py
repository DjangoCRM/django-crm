from abc import ABC, abstractmethod
from datetime import date
from typing import Tuple
from django.core.mail import mail_admins

STATE_CURRENCY = 'EUR'


class BaseBackend(ABC):
    
    @classmethod
    def get_state_currency(cls):
        return STATE_CURRENCY
    
    @abstractmethod
    def __init__(self, currency: str, marketing_currency: str = 'USD', rate_date: date = None):
        self.url = "https://bank.gov.example/api/v1/statdirectory/exchange"
        self.date_format = "Y/m/d"
        self.error = ''
        self.state_currency = self.get_state_currency()
        self.currency = currency
        self.marketing_currency = marketing_currency
        self.rate_date = rate_date
        self.data = self.get_data()
        self.marketing_currency_rate = self.data['marketing_currency']

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def get_marketing_currency_rate(self):
        """Get marketing currency rate to state currency."""
        pass

    @abstractmethod
    def get_rate_to_state_currency(self, currency: str = 'USD'):
        pass

    def get_rates(self) -> Tuple[float, float, str]:
        if not self.error:
            if self.currency == self.state_currency:
                rate_to_state_currency = 1
                rate_to_marketing_currency_rate = 1 / self.marketing_currency_rate
            elif self.currency == self.marketing_currency:
                rate_to_state_currency = self.marketing_currency_rate
                rate_to_marketing_currency_rate = 1
            else:
                rate_to_state_currency = self.get_rate_to_state_currency(self.currency)
                rate_to_marketing_currency_rate = rate_to_state_currency / self.marketing_currency_rate
            if not self.error:
                return rate_to_state_currency, rate_to_marketing_currency_rate, self.error

        mail_admins(
            "Error getting currency rates",
            f"self.currency {self.currency}. Error: {self.error}",
            fail_silently=False,
        )
        return 1, 1, self.error

import time
import threading
from datetime import timedelta
from tendo.singleton import SingleInstance
from django.conf import settings
from django.core.mail import mail_admins
from django.db import connection
from django.db.models import Exists
from django.db.models import OuterRef
from django.utils import timezone
from django.utils.module_loading import import_string

from crm.models import Currency
from crm.models import Payment
from crm.models import Rate


BACKEND = ""
if settings.LOAD_RATE_BACKEND:
    BACKEND = import_string(settings.LOAD_RATE_BACKEND)


class RatesLoader(threading.Thread, SingleInstance):
    
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        if settings.TESTING:
            SingleInstance.__init__(self, flavor_id='RatesLoader_test')
        else:
            SingleInstance.__init__(self, flavor_id='RatesLoader')

    def run(self):
        if settings.DEBUG or not settings.LOAD_EXCHANGE_RATE:
            return
        # To prevent hit the db until the apps.ready() is completed.
        time.sleep(1)

        marketing_currency = Currency.objects.filter(
                is_marketing_currency=True
        ).first()
        if not marketing_currency:
            mail_admins(
                "Error getting currency rates from the Internet",
                "\nPlease specify the marketing currency."
                "\nOr disable automatic retrieval of exchange rates."
                "\ncrm.settings.LOAD_EXCHANGE_RATE = False",
                fail_silently=True,
            )
            connection.close()
            return

        while True:
            now = timezone.localtime(timezone.now())
            hour_str, minute_str = settings.LOADING_EXCHANGE_RATE_TIME.split(':')
            appointment = now.replace(hour=int(hour_str), minute=int(minute_str))
            if now < appointment:
                secs = (appointment - now).total_seconds()
            else:
                secs = (timedelta(hours=24) + appointment - now).total_seconds()
            connection.close()
            if not settings.TESTING:
                time.sleep(secs)
            get_rates(marketing_currency)

            if settings.TESTING:
                break


def get_rates(marketing_currency: Currency, backend=BACKEND) -> None:
    now = timezone.localtime(timezone.now())
    # update currencies
    for currency in Currency.objects.all():
        be = backend(
            currency.name,
            marketing_currency.name,
            now.date() - timedelta(days=1)
        )
        rate_to_state_currency, rate_to_marketing_currency, error = be.get_rates()
        if not error:
            currency.rate_to_state_currency = rate_to_state_currency
            currency.rate_to_marketing_currency = rate_to_marketing_currency
            currency.save()
        time.sleep(0.5)

    rates = Rate.objects.filter(
        currency=OuterRef('currency'),
        payment_date=OuterRef('payment_date'),
        rate_type=Rate.OFFICIAL
    )
    while True:
        payment = Payment.objects.filter(
            payment_date__lt=now.date(),
            status=Payment.RECEIVED
        ).annotate(
            rate=Exists(rates)
        ).filter(rate=False).first()
        if not payment:
            break
        currency = payment.currency
        payment_date = payment.payment_date
        be = backend(
            currency.name,
            marketing_currency.name,
            payment_date
        )
        rate_to_state_currency, rate_to_marketing_currency, error = be.get_rates()
        if error:
            break
        try:
            r = Rate.objects.get(
                currency=currency,
                payment_date=payment_date,
            )
        except Rate.DoesNotExist:
            r = Rate(
                currency=currency,
                payment_date=payment_date,
            )
        r.rate_to_state_currency = rate_to_state_currency
        r.rate_to_marketing_currency = rate_to_marketing_currency
        r.rate_type = Rate.OFFICIAL
        r.save()

        time.sleep(0.5)

from datetime import datetime as dt
from datetime import timedelta
from django.conf import settings
from django.test import tag
from django.test import TransactionTestCase

from crm.models import Country
from crm.models import Currency
from crm.models import Deal
from crm.models import Rate
from crm.models import Payment
from common.utils.helpers import get_delta_date
from common.utils.helpers import get_department_id
from crm.utils.rates_loader import RatesLoader
from tests.utils.helpers import get_user

# test tests.crm.utils.test_rates_loader --noinput
# test tests.crm.utils.test_rates_loader --keepdb


@tag('TransactionTestCase')
class TestGetRates(TransactionTestCase):
    """Test getting currency rates from the Internet"""
    # Inherit TransactionTestCase since creating and saving objects
    # happens in a separate thread.
    fixtures = ('groups.json',)

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_get_rates(self):
        if not settings.LOAD_EXCHANGE_RATE:
            print("Currency exchange rate download test skipped due to settings.")
            return
        Currency.objects.bulk_create([
            Currency(
                pk=1, name="USD",
                rate_to_state_currency="0.83",
                rate_to_marketing_currency="1.0",
                is_state_currency=False,
                is_marketing_currency=True
            ),
            Currency(
                pk=2, name="EUR",
                rate_to_state_currency="1.0",
                rate_to_marketing_currency="1.2",
                is_state_currency=True,
                is_marketing_currency=False
            )
        ])
        Country.objects.create(id=190, name="United States")
        # owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        owner = get_user()
        date = dt.now().date()
        usd_currency = Currency.objects.get(name="USD")
        eur_currency = Currency.objects.get(name="EUR")
        marketing_currency = Currency.objects.filter(
            is_marketing_currency=True
        ).first()
        self.assertIsNotNone(marketing_currency)
        deal = Deal.objects.create(
            name="Test deal",
            department_id=get_department_id(owner),
            ticket="abc123",
            description="description",
            next_step=settings.FIRST_STEP,
            next_step_date=get_delta_date(1),
            stage=None,
            owner=owner,
        )
        currencies = Currency.objects.all()
        currencies.update(
            rate_to_state_currency=0,
            rate_to_marketing_currency=0
        )
        self.assertEqual(0, currencies.first().rate_to_state_currency)
        self.assertFalse(Rate.objects.exists())

        Payment.objects.create(
            deal=deal,
            amount=100.0,
            currency=usd_currency,
            payment_date=date,
            status=Payment.RECEIVED,
        )
        # rate must be created
        rate1 = Rate.objects.filter(
            currency=usd_currency,
            payment_date=date,
            rate_type=Rate.APPROXIMATE,
        ).first()
        self.assertTrue(rate1)
        self.assertEqual(0, rate1.rate_to_state_currency)
        self.assertEqual(0, rate1.rate_to_marketing_currency)

        Payment.objects.create(
            deal=deal,
            amount=200.0,
            currency=usd_currency,
            payment_date=date - timedelta(days=7),
            status=Payment.RECEIVED,
        )
        rate2 = Rate.objects.create(
            currency=usd_currency,
            payment_date=date - timedelta(days=7),
            rate_to_state_currency=0,
            rate_to_marketing_currency=0,
            rate_type=Rate.OFFICIAL,
        )
        Payment.objects.create(
            deal=deal,
            amount=300.0,
            currency=eur_currency,
            payment_date=date - timedelta(days=14),
            status=Payment.RECEIVED,
        )
        rate3 = Rate.objects.filter(
            currency=eur_currency,
            payment_date=date - timedelta(days=14),
            rate_type=Rate.APPROXIMATE,
        ).first()
        self.assertTrue(rate3)
        self.assertEqual(0, rate3.rate_to_state_currency)
        self.assertEqual(0, rate3.rate_to_marketing_currency)

        # the rate4 does not match any payment
        rate4 = Rate.objects.create(
            currency=usd_currency,
            payment_date=date - timedelta(days=14),
            rate_to_state_currency=0,
            rate_to_marketing_currency=0,
            rate_type=Rate.APPROXIMATE,
        )

        # get_rates(marketing_currency)
        # with self.settings(TESTING=True):
        rl = RatesLoader()
        rl.run()

        # all currencies must be updated
        for c in currencies:
            self.assertNotEqual(0, c.rate_to_state_currency)
            self.assertNotEqual(0, c.rate_to_marketing_currency)

        # rate1 should not be updated since payment_date is today
        rate1.refresh_from_db()
        self.assertEqual(usd_currency, rate1.currency)
        self.assertEqual(date, rate1.payment_date)
        self.assertEqual(Rate.APPROXIMATE, rate1.rate_type)
        self.assertEqual(0.0, rate1.rate_to_state_currency)
        self.assertEqual(0.0, rate1.rate_to_marketing_currency)

        # rate2 should not be updated since rate_type is OFFICIAL
        rate2.refresh_from_db()
        self.assertEqual(usd_currency, rate2.currency)
        self.assertEqual(date - timedelta(days=7), rate2.payment_date)
        self.assertEqual(Rate.OFFICIAL, rate2.rate_type)
        self.assertEqual(0.0, rate2.rate_to_state_currency)
        self.assertEqual(0.0, rate2.rate_to_marketing_currency)

        # rate3 should  be updated
        rate3.refresh_from_db()
        self.assertEqual(eur_currency, rate3.currency)
        self.assertEqual(date - timedelta(days=14), rate3.payment_date)
        self.assertEqual(Rate.OFFICIAL, rate3.rate_type)
        self.assertNotEqual(0.0, rate3.rate_to_state_currency)
        self.assertNotEqual(0.0, rate3.rate_to_marketing_currency)

        # rate4 should not be updated since does not match any payment
        rate4.refresh_from_db()
        self.assertEqual(usd_currency, rate4.currency)
        self.assertEqual(date - timedelta(days=14), rate4.payment_date)
        self.assertEqual(Rate.APPROXIMATE, rate4.rate_type)
        self.assertEqual(0.0, rate4.rate_to_state_currency)
        self.assertEqual(0.0, rate4.rate_to_marketing_currency)

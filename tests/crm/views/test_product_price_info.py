from decimal import Decimal

from django.test import tag
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from crm.models import ClientType
from crm.models import Currency
from crm.models import Product
from crm.models import ProductPriceTier
from tests.base_test_classes import BaseTestCase

# python manage.py test tests.crm.views.test_product_price_info --keepdb

EUR = 2     # state currency in the fixture, rate 1.0
USD = 1     # rate_to_state_currency 0.83
GLOBAL_SALES = 9    # department with default_currency USD
BOOKKEEPING = 11    # department with no default currency


@tag('TestCase')
class TestProductPriceInfo(BaseTestCase):
    """The amount the Deal's product inline asks for (#526).

    The admin JS sends the product, quantity, the deal's price tier and
    currency, and the deal's discount, and writes the returned `amount`
    into the inline. Each test states the arithmetic it expects, so a change
    to the calculation shows up as a named number rather than a diff.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('product_price_info')
        cls.user = USER_MODEL.objects.get(username="Adam.Admin")
        cls.tier = ClientType.objects.get(pk=4)     # end customer
        cls.eur_product = cls._product("EUR widget", currency_id=EUR)
        cls.usd_product = cls._product("USD widget", currency_id=USD)
        cls.dept_product = cls._product(
            "Department-priced widget", department_id=GLOBAL_SALES)
        cls.bare_product = cls._product(
            "Unpriced-currency widget", department_id=BOOKKEEPING)
        for product in (cls.eur_product, cls.usd_product,
                        cls.dept_product, cls.bare_product):
            ProductPriceTier.objects.create(
                product=product, tier_name=cls.tier, price=Decimal("100.00"))

    @classmethod
    def _product(cls, name, **fields):
        fields.setdefault('department_id', GLOBAL_SALES)
        return Product.objects.create(
            name=name, price=Decimal("100.00"), **fields)

    def setUp(self):
        self.client.force_login(self.user)

    def get(self, **params):
        query = {
            'tier_name': self.tier.id,
            'deal_currency': EUR,
            'quantity': '1',
            **params,
        }
        response = self.client.get(self.url, query)
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def assertAmount(self, expected, **params):
        body = self.get(**params)
        self.assertEqual(body, {'ok': True, 'amount': expected})

    def assertError(self, error, **params):
        body = self.get(**params)
        self.assertEqual(body, {'ok': False, 'error': error})

    # -- the calculation -------------------------------------------------

    def test_same_currency_is_price_times_quantity(self):
        self.assertAmount('300.00', product=self.eur_product.id, quantity='3')

    def test_product_currency_is_converted_into_the_deal_currency(self):
        # 100 USD * 0.83 (USD -> state) / 1.0 (EUR -> state) = 83 EUR a unit
        self.assertAmount('166.00', product=self.usd_product.id, quantity='2')

    def test_conversion_the_other_way_is_rounded_to_cents(self):
        # 100 EUR * 1.0 / 0.83 = 120.4819... USD
        self.assertAmount(
            '120.48', product=self.eur_product.id, deal_currency=USD)

    def test_without_a_product_currency_the_department_default_is_used(self):
        # Global sales defaults to USD, so this prices like the USD product.
        self.assertAmount('83.00', product=self.dept_product.id)

    def test_without_any_currency_the_price_is_taken_as_the_deals(self):
        self.assertAmount('100.00', product=self.bare_product.id)

    def test_a_fractional_quantity_is_honoured(self):
        self.assertAmount('150.00', product=self.eur_product.id, quantity='1.5')

    def test_an_empty_quantity_is_zero(self):
        self.assertAmount('0.00', product=self.eur_product.id, quantity='')

    # -- discounts -------------------------------------------------------

    def test_percentage_discount(self):
        self.assertAmount(
            '180.00', product=self.eur_product.id, quantity='2',
            discount_type='D', discount_value='10')

    def test_percentage_discount_applies_after_conversion(self):
        # 83 EUR a unit, less 10% = 74.70, times 2
        self.assertAmount(
            '149.40', product=self.usd_product.id, quantity='2',
            discount_type='D', discount_value='10')

    def test_fixed_discount_is_subtracted_per_unit(self):
        # Current behaviour: 'F' takes the value off each unit's price,
        # (100 - 15) * 2. The Deal model labels 'F' "Fixed Price" and the
        # view's docstring calls the value a "fixed unit price", which would
        # make this 30.00 instead; see the pull request.
        self.assertAmount(
            '170.00', product=self.eur_product.id, quantity='2',
            discount_type='F', discount_value='15')

    def test_discount_type_is_percentage_when_not_sent(self):
        self.assertAmount(
            '90.00', product=self.eur_product.id, discount_value='10')

    def test_an_empty_discount_type_applies_no_discount(self):
        self.assertAmount(
            '100.00', product=self.eur_product.id,
            discount_type='', discount_value='10')

    def test_a_zero_or_empty_discount_changes_nothing(self):
        for value in ('0', ''):
            with self.subTest(discount_value=value):
                self.assertAmount(
                    '100.00', product=self.eur_product.id,
                    discount_type='D', discount_value=value)

    # -- refusals --------------------------------------------------------

    def test_missing_parameters(self):
        for missing in ('product', 'tier_name', 'deal_currency'):
            with self.subTest(missing=missing):
                query = {
                    'product': self.eur_product.id,
                    'tier_name': self.tier.id,
                    'deal_currency': EUR,
                }
                del query[missing]
                response = self.client.get(self.url, query)
                self.assertEqual(
                    response.json(), {'ok': False, 'error': 'missing_params'})

    def test_unknown_product(self):
        self.assertError('product_not_found', product=2147483647)

    def test_a_product_id_that_is_not_a_number_is_refused_not_a_500(self):
        self.assertError('product_not_found', product='abc')

    def test_bad_quantity(self):
        self.assertError(
            'bad_quantity', product=self.eur_product.id, quantity='two')

    def test_a_quantity_that_is_not_finite_is_refused(self):
        # Decimal() parses these, so without a check NaN came back as the
        # amount "NaN" and Infinity was a 500 on a product with no currency.
        for product in (self.eur_product, self.bare_product):
            for value in ('NaN', 'Infinity', '-Infinity'):
                with self.subTest(product=product.name, quantity=value):
                    self.assertError(
                        'bad_quantity', product=product.id, quantity=value)

    def test_a_discount_that_is_not_finite_is_refused(self):
        for product in (self.eur_product, self.bare_product):
            for value in ('NaN', 'Infinity'):
                with self.subTest(product=product.name, discount_value=value):
                    self.assertError(
                        'bad_discount_value', product=product.id,
                        discount_type='D', discount_value=value)

    def test_bad_discount_value(self):
        self.assertError(
            'bad_discount_value', product=self.eur_product.id,
            discount_value='ten')

    def test_bad_discount_type(self):
        self.assertError(
            'bad_discount_type', product=self.eur_product.id,
            discount_type='X', discount_value='10')

    def test_no_price_for_that_tier(self):
        other_tier = ClientType.objects.get(pk=1)
        self.assertError(
            'no_price_tier', product=self.eur_product.id,
            tier_name=other_tier.id)

    def test_a_tier_id_that_is_not_a_number_has_no_price(self):
        self.assertError(
            'no_price_tier', product=self.eur_product.id, tier_name='abc')

    def test_unknown_deal_currency(self):
        self.assertError(
            'deal_currency_not_found', product=self.eur_product.id,
            deal_currency=2147483647)

    def test_a_deal_currency_id_that_is_not_a_number_is_refused_not_a_500(self):
        self.assertError(
            'deal_currency_not_found', product=self.eur_product.id,
            deal_currency='abc')

    def test_a_deal_currency_with_a_zero_rate(self):
        zero = Currency.objects.create(
            name="ZZZ", rate_to_state_currency=0, rate_to_marketing_currency=1)
        self.assertError(
            'zero_deal_rate', product=self.eur_product.id,
            deal_currency=zero.id)

    # -- access ----------------------------------------------------------

    def test_requires_a_staff_login(self):
        self.client.logout()
        response = self.client.get(self.url, {
            'product': self.eur_product.id,
            'tier_name': self.tier.id,
            'deal_currency': EUR,
        })
        self.assertEqual(response.status_code, 302)

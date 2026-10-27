from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.test import TestCase
from django.test import tag

from crm.models import Country
from crm.site.countryadmin import CountryAdmin


@tag('TestCase')
class TestCountrySearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.north = Country.objects.create(
            name='Northland', alternative_names='Northern Isles',
            iso_code='nl', phone_code='34', url_name='northland'
        )
        cls.south = Country.objects.create(
            name='Southland', iso_code='sl', phone_code='345',
            url_name='southland'
        )
        cls.middle = Country.objects.create(
            name='Midland', iso_code='ml', phone_code='234',
            url_name='midland'
        )
        cls.numeric_name = Country.objects.create(
            name='34 Islands', iso_code='ii', phone_code='99',
            url_name='34-islands'
        )

    def setUp(self):
        self.model_admin = CountryAdmin(Country, AdminSite())
        self.request = RequestFactory().get('/')

    def test_digits_match_the_beginning_of_phone_codes_only(self):
        results, duplicates = self.model_admin.get_search_results(
            self.request, Country.objects.all(), '34'
        )
        self.assertCountEqual(results, [self.north, self.south])
        self.assertFalse(duplicates)

    def test_complete_phone_code_matches(self):
        results, duplicates = self.model_admin.get_search_results(
            self.request, Country.objects.all(), '345'
        )
        self.assertCountEqual(results, [self.south])
        self.assertFalse(duplicates)

    def test_unmatched_digits_return_no_countries(self):
        results, duplicates = self.model_admin.get_search_results(
            self.request, Country.objects.all(), '777'
        )
        self.assertFalse(results.exists())
        self.assertFalse(duplicates)

    def test_digit_search_preserves_the_supplied_queryset(self):
        results, duplicates = self.model_admin.get_search_results(
            self.request, Country.objects.filter(pk=self.south.pk), '34'
        )
        self.assertCountEqual(results, [self.south])
        self.assertFalse(duplicates)

    def test_empty_search_preserves_the_supplied_queryset(self):
        queryset = Country.objects.filter(pk=self.north.pk)
        results, duplicates = self.model_admin.get_search_results(
            self.request, queryset, ''
        )
        self.assertCountEqual(results, [self.north])
        self.assertFalse(duplicates)

    def test_text_search_still_matches_name_alternative_name_and_iso_code(self):
        for term in ('Northland', 'Northern', 'nl'):
            with self.subTest(term=term):
                results, duplicates = self.model_admin.get_search_results(
                    self.request, Country.objects.all(), term
                )
                self.assertCountEqual(results, [self.north])
                self.assertFalse(duplicates)

    def test_other_input_keeps_djangos_existing_search_behavior(self):
        for term in (' 34', '+34', '34 Islands'):
            with self.subTest(term=term):
                queryset = Country.objects.all()
                expected, expected_duplicates = ModelAdmin.get_search_results(
                    self.model_admin, self.request, queryset, term
                )
                results, duplicates = self.model_admin.get_search_results(
                    self.request, queryset, term
                )
                self.assertCountEqual(results, expected)
                self.assertEqual(duplicates, expected_duplicates)

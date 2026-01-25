from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from django.test import tag
from django.urls import reverse

from crm.models import City
from crm.models import Country
from crm.site.cityadmin import CityAdmin
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials


# python manage.py test tests.crm.test_city --keepdb


@tag('TestCase')
class TestCity(BaseTestCase):
    """Test City Model and CityAdmin"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_url = reverse("site:crm_city_add")
        cls.changelist_url = reverse("site:crm_city_changelist")
        cls.user = User.objects.get(username="Darian.Manager.Co-worker.Head.Global")
        cls.country = Country.objects.create(
            name='France',
            url_name='france'
        )
        cls.country2 = Country.objects.create(
            name='Germany',
            url_name='germany'
        )

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.user)

    # -- City Model Tests -- #

    def test_create_city_with_name_only(self):
        """Test creating a city with only name and country."""
        city = City.objects.create(
            name='Paris',
            country=self.country
        )
        self.assertEqual(city.name, 'Paris')
        self.assertEqual(city.country, self.country)
        self.assertEqual(city.alternative_names, '')
        self.assertEqual(str(city), 'Paris')

    def test_create_city_with_alternative_names(self):
        """Test creating a city with alternative names."""
        city = City.objects.create(
            name='Munich',
            alternative_names='München, Muenchen',
            country=self.country2
        )
        self.assertEqual(city.name, 'Munich')
        self.assertEqual(city.alternative_names, 'München, Muenchen')
        self.assertEqual(city.country, self.country2)

    def test_validate_name_prevents_duplicate_exact_name(self):
        """Test that validate_name prevents duplicate city names."""
        City.objects.create(
            name='Lyon',
            country=self.country
        )
        duplicate_city = City(
            name='Lyon',
            country=self.country
        )
        with self.assertRaises(ValidationError) as context:
            duplicate_city.clean()
        self.assertIn('name', context.exception.message_dict)

    def test_validate_name_prevents_duplicate_case_insensitive(self):
        """Test that validate_name is case insensitive."""
        City.objects.create(
            name='Marseille',
            country=self.country
        )
        duplicate_city = City(
            name='MARSEILLE',
            country=self.country
        )
        with self.assertRaises(ValidationError) as context:
            duplicate_city.clean()
        self.assertIn('name', context.exception.message_dict)

    def test_validate_name_prevents_duplicate_in_alternative_names(self):
        """Test that a new city name cannot match existing alternative names."""
        City.objects.create(
            name='Nice',
            alternative_names='Nizza, Nissa',
            country=self.country
        )
        duplicate_city = City(
            name='Nizza',
            country=self.country
        )
        with self.assertRaises(ValidationError) as context:
            duplicate_city.clean()
        self.assertIn('name', context.exception.message_dict)

    def test_validate_alternative_names_prevents_duplicate(self):
        """Test that alternative names cannot duplicate existing city names."""
        City.objects.create(
            name='Bordeaux',
            country=self.country
        )
        duplicate_city = City(
            name='Burdigala',
            alternative_names='Bordeaux, Bordèu',
            country=self.country
        )
        with self.assertRaises(ValidationError) as context:
            duplicate_city.clean()
        self.assertIn('alternative_names', context.exception.message_dict)

    def test_validate_alternative_names_multiple_duplicates(self):
        """Test validation with multiple alternative names where one is duplicate."""
        City.objects.create(
            name='Toulouse',
            country=self.country
        )
        duplicate_city = City(
            name='Pink City',
            alternative_names='Tolosa, Toulouse, La Ville Rose',
            country=self.country
        )
        with self.assertRaises(ValidationError) as context:
            duplicate_city.clean()
        self.assertIn('alternative_names', context.exception.message_dict)

    def test_validate_name_allows_same_name_different_country(self):
        """Test that same city name is allowed in different countries."""
        City.objects.create(
            name='Berlin',
            country=self.country2
        )
        # Create city with same name but different country
        city = City(
            name='Berlin',
            country=self.country
        )
        # Should not raise ValidationError
        try:
            city.clean()
        except ValidationError:
            self.fail("ValidationError raised for same city name in different country")

    def test_edit_city_name_no_self_validation_error(self):
        """Test editing a city's own data doesn't trigger validation error."""
        city = City.objects.create(
            name='Strasbourg',
            alternative_names='Strassburg',
            country=self.country
        )
        # Edit the same city
        city.name = 'Strasbourg'
        city.alternative_names = 'Strassburg, Argentoratum'
        try:
            city.clean()
        except ValidationError:
            self.fail("ValidationError raised when editing city's own data")

    def test_edit_city_alternative_names_prevents_duplicates(self):
        """Test editing alternative names to add existing city name fails."""
        City.objects.create(
            name='Lille',
            country=self.country
        )
        city = City.objects.create(
            name='Rijsel',
            country=self.country
        )
        # Try to add 'Lille' to alternative names
        city.alternative_names = 'Lille, Ryssel'
        with self.assertRaises(ValidationError) as context:
            city.clean()
        self.assertIn('alternative_names', context.exception.message_dict)

    def test_validate_name_with_empty_alternative_names(self):
        """Test validation works correctly with empty alternative names."""
        City.objects.create(
            name='Nantes',
            alternative_names='',
            country=self.country
        )
        city = City(
            name='Naoned',
            alternative_names='',
            country=self.country
        )
        try:
            city.clean()
        except ValidationError:
            self.fail("ValidationError raised with empty alternative names")

    # -- CityAdmin Tests -- #

    def test_cityadmin_list_display(self):
        """Test CityAdmin list_display configuration."""
        model_admin = CityAdmin(City, AdminSite())
        self.assertEqual(model_admin.list_display, ('name', 'country'))

    def test_cityadmin_list_filter(self):
        """Test CityAdmin list_filter configuration."""
        from crm.utils.admfilters import ByCountryFilter
        model_admin = CityAdmin(City, AdminSite())
        self.assertEqual(len(model_admin.list_filter), 1)
        self.assertEqual(model_admin.list_filter[0], ByCountryFilter)

    def test_cityadmin_ordering(self):
        """Test CityAdmin ordering configuration."""
        model_admin = CityAdmin(City, AdminSite())
        self.assertEqual(model_admin.ordering, ('name', 'country'))

    def test_cityadmin_search_fields(self):
        """Test CityAdmin search_fields configuration."""
        model_admin = CityAdmin(City, AdminSite())
        self.assertEqual(model_admin.search_fields, ('name', 'alternative_names'))

    def test_cityadmin_change_view_includes_delete_duplicate_url(self):
        """Test that change_view adds delete duplicate URL to context."""
        city = City.objects.create(
            name='Montpellier',
            country=self.country
        )
        model_admin = CityAdmin(City, AdminSite())
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user

        response = model_admin.change_view(request, str(city.id))

        # Check that del_dup_url is in extra_context
        self.assertIn('del_dup_url', response.context_data)
        self.assertIn('delete-duplicate', response.context_data['del_dup_url'])

    # -- Integration Tests with Admin Interface -- #

    def test_add_city_via_admin(self):
        """Test adding a city through admin interface."""
        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        data = get_adminform_initials(response)
        data['name'] = 'Cannes'
        data['alternative_names'] = 'Canas'
        data['country'] = self.country.id

        response = self.client.post(self.add_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)

        # Verify city was created
        self.assertTrue(City.objects.filter(name='Cannes').exists())
        city = City.objects.get(name='Cannes')
        self.assertEqual(city.alternative_names, 'Canas')
        self.assertEqual(city.country, self.country)

    def test_change_city_via_admin(self):
        """Test changing a city through admin interface."""
        city = City.objects.create(
            name='Rennes',
            alternative_names='Roazhon',
            country=self.country
        )

        change_url = reverse("site:crm_city_change", args=(city.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain, [])

        data = get_adminform_initials(response)
        data['alternative_names'] = 'Roazhon, Resnn'

        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)

        # Verify changes were saved
        city.refresh_from_db()
        self.assertEqual(city.alternative_names, 'Roazhon, Resnn')

    def test_add_duplicate_city_via_admin_fails(self):
        """Test that adding a duplicate city through admin fails."""
        City.objects.create(
            name='Grenoble',
            country=self.country
        )

        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        data = get_adminform_initials(response)
        data['name'] = 'grenoble'  # Different case
        data['country'] = self.country.id

        response = self.client.post(self.add_url, data, follow=True)
        # Should have form errors due to duplicate
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        # Check that we're still on add page (not redirected)
        self.assertEqual(response.redirect_chain, [])

    def test_city_changelist_access(self):
        """Test accessing city changelist."""
        City.objects.create(name='Avignon', country=self.country)
        City.objects.create(name='Dijon', country=self.country)

        response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        # Check that cities appear in the list
        content = response.content.decode()
        self.assertIn('Avignon', content)
        self.assertIn('Dijon', content)

    def test_city_search_by_name(self):
        """Test searching cities by name in admin."""
        City.objects.create(name='Annecy', country=self.country)
        City.objects.create(name='Aix-en-Provence', country=self.country)
        City.objects.create(name='Brest', country=self.country)

        response = self.client.get(
            self.changelist_url,
            {'q': 'Annecy'},
            follow=True
        )
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        content = response.content.decode()
        self.assertIn('Annecy', content)
        self.assertNotIn('Brest', content)

    def test_city_search_by_alternative_names(self):
        """Test searching cities by alternative names in admin."""
        City.objects.create(
            name='Dunkirk',
            alternative_names='Dunkerque, Duinkerke',
            country=self.country
        )
        City.objects.create(name='Calais', country=self.country)

        response = self.client.get(
            self.changelist_url,
            {'q': 'Dunkerque'},
            follow=True
        )
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        content = response.content.decode()
        self.assertIn('Dunkirk', content)
        self.assertNotIn('Calais', content)

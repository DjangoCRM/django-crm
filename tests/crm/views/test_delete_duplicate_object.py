from django.contrib.auth.models import User
from django.test import tag, RequestFactory
from django.urls import reverse

from crm.models.country import City
from crm.models.country import Country
from crm.site.crmadminsite import crm_site
from crm.site.crmmodeladmin import CrmModelAdmin
from tests.base_test_classes import BaseTestCase


@tag('TestCase')
class TestDeleteDuplicateObject(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.get(username="Andrew.Manager.Global")
        cls.country = Country.objects.get(name="United States")
        cls.factory = RequestFactory()
        cls.original_city = City.objects.create(
            name="Original City",
            country=cls.country,
            alternative_names="OldName, london"
        )

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)
        self.client.force_login(self.user)
        self.model_admin = CrmModelAdmin(model=City, admin_site=crm_site)

    def test_delete_duplicate_city_adds_alternative_name(self):
        """Test that deleting a duplicate city adds its name to alternative names."""
        duplicate_city = City.objects.create(
            name="Duplicate City",
            country=self.country
        )
        url = reverse('site:crm_city_change', args=(duplicate_city.id,))
        factory = RequestFactory()
        test_request = factory.get(url)

        # Use helper to get the correct URL
        del_dup_url = self.model_admin.del_dup_url(
            test_request, duplicate_city.id)

        # Post to the view
        data = {'city': self.original_city.id}
        response = self.client.post(del_dup_url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.original_city.refresh_from_db()

        # This assertion is expected to FAIL currently
        self.assertIn("Duplicate City", self.original_city.alternative_names)

    def test_delete_duplicate_city_case_insensitive_check(self):
        """Test that we don't add duplicate if it exists with different case."""
        duplicate_city = City.objects.create(
            name="London",
            country=self.country
        )
        # Create a dummy request to pass to del_dup_url
        dummy_url = reverse('site:crm_city_change', args=(duplicate_city.id,))
        test_request = self.factory.get(dummy_url)
        del_dup_url = self.model_admin.del_dup_url(test_request, duplicate_city.id)

        data = {'city': self.original_city.id}
        response = self.client.post(del_dup_url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.original_city.refresh_from_db()
        # Should NOT have added "big smoke" again
        self.assertNotIn(self.original_city.alternative_names, "London")

    def test_delete_duplicate_city_handle_empty_alternative_names(self):
        """Test that we handle None/empty alternative names correctly."""
        original_city = City.objects.create(
            name="Kyoto",
            country=self.country,
        )
        duplicate_city = City.objects.create(
            name="Heian-kyo",
            country=self.country
        )
        dummy_url = reverse('site:crm_city_change', args=(duplicate_city.id,))
        test_request = self.factory.get(dummy_url)
        del_dup_url = self.model_admin.del_dup_url(
            test_request, duplicate_city.id)

        data = {'city': original_city.id}
        response = self.client.post(del_dup_url, data, follow=True)
        self.assertEqual(response.status_code, 200)

        original_city.refresh_from_db()
        self.assertEqual(original_city.alternative_names, "Heian-kyo")

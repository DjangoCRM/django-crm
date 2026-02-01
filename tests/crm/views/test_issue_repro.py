from django.test import tag, RequestFactory
from django.urls import reverse
from crm.models.country import Country, City
from crm.site.crmadminsite import crm_site
from crm.site.cityadmin import CityAdmin
from tests.base_test_classes import BaseTestCase
from common.utils.helpers import USER_MODEL

@tag('TestCase')
class TestIssueRepro(BaseTestCase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")

    def setUp(self):
        self.client.force_login(self.owner)
        self.country = Country.objects.create(name="Test Country", url_name="test-country")

    def test_delete_duplicate_city_adds_alternative_name(self):
        original_city = City.objects.create(
            name="Original City",
            country=self.country,
            alternative_names="OldName"
        )
        duplicate_city = City.objects.create(
            name="Duplicate City",
            country=self.country
        )
        
        url = reverse('site:crm_city_change', args=(duplicate_city.id,))
        from crm.site.crmmodeladmin import CrmModelAdmin
        model_admin = CrmModelAdmin(model=City, admin_site=crm_site)
        factory = RequestFactory()
        test_request = factory.get(url)
        
        # Use helper to get the correct URL
        del_dup_url = model_admin.del_dup_url(test_request, duplicate_city.id)
        
        # Post to the view
        data = {'city': original_city.id}
        response = self.client.post(del_dup_url, data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        
        original_city.refresh_from_db()
        
        # This assertion is expected to FAIL currently
        self.assertIn("Duplicate City", original_city.alternative_names)

    def test_delete_duplicate_city_case_insensitive_check(self):
        """Test that we don't add duplicate if it exists with different case."""
        original_city = City.objects.create(
            name="London",
            country=self.country,
            alternative_names="london"
        )
        duplicate_city = City.objects.create(
            name="London", # Same name, technically this scenario might be blocked by other validation but used for logic check
            country=self.country
        )
         # Actually let's use a name that is in alternative names but different case
        original_city.alternative_names = "Big Smoke"
        original_city.save()
        
        duplicate_city.name = "big smoke" # different case
        duplicate_city.save()

        # Fix URL retrieval
        from crm.site.crmmodeladmin import CrmModelAdmin
        model_admin = CrmModelAdmin(model=City, admin_site=crm_site)
        factory = RequestFactory()
        # Create a dummy request to pass to del_dup_url
        dummy_url = reverse('site:crm_city_change', args=(duplicate_city.id,))
        test_request = factory.get(dummy_url)
        del_dup_url = model_admin.del_dup_url(test_request, duplicate_city.id)
        
        data = {'city': original_city.id}
        response = self.client.post(del_dup_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        original_city.refresh_from_db()
        # Should NOT have added "big smoke" again
        self.assertEqual(original_city.alternative_names, "Big Smoke")

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

        from crm.site.crmmodeladmin import CrmModelAdmin
        model_admin = CrmModelAdmin(model=City, admin_site=crm_site)
        factory = RequestFactory()
        dummy_url = reverse('site:crm_city_change', args=(duplicate_city.id,))
        test_request = factory.get(dummy_url)
        del_dup_url = model_admin.del_dup_url(test_request, duplicate_city.id)
        
        data = {'city': original_city.id}
        response = self.client.post(del_dup_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        original_city.refresh_from_db()
        self.assertEqual(original_city.alternative_names, "Heian-kyo")

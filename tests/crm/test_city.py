from django.test import TestCase
from django.core.exceptions import ValidationError
from crm.models.country import City, Country

class CityModelTest(TestCase):
    def setUp(self):
        # Setting up Country object because City has a ForeignKey to it
        self.country = Country.objects.create(name="Testland")

    def test_duplicate_alternative_names_internal(self):
        """
        Test that providing duplicate names in the alternative_names 
        string field (comma-separated) raises a ValidationError.
        """
        city = City(
            name="London",
            alternative_names="London, London, Paris", # "London" is repeated
            country=self.country
        )
        # This should fail validation because of the duplicate "London"
        with self.assertRaises(ValidationError):
            city.clean()

    def test_alternative_name_unique_success(self):
        """Test that unique alternative names work fine"""
        city = City(
            name="London",
            alternative_names="The Big Smoke, L-Town",
            country=self.country
        )
        try:
            city.clean()
        except ValidationError:
            self.fail("city.clean() raised ValidationError unexpectedly!")
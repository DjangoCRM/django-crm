from django.test import TestCase
from django.core.exceptions import ValidationError
from crm.models.country import City, Country

class CityModelTest(TestCase):
    def setUp(self):
        # Setting up Country object because City has a ForeignKey to it
        self.country = Country.objects.create(name="Italy", url_name="italy")

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


    # Additional tests can be added here to cover more scenarios to avoid lower case duplicates, etc.

    def test_cannot_add_city_if_name_exists_as_alternative_elsewhere(self):
        """
        Confirms the inability to add 'Rome' if 'Roma' 
        already has 'Rome' as an alternative name.
        """
        # Create the initial record
        City.objects.create(
            name="Roma",
            alternative_names="Rom, Rome, Róm",
            country=self.country
        )

        # Attempt to create a new record with the name "Rome"
        duplicate_city = City(
            name="Rome", 
            country=self.country
        )

        # Debug: Check if Roma actually exists in the DB right now
        print(f"DEBUG: Cities in DB: {City.objects.filter(country=self.country).all()}")

        with self.assertRaises(ValidationError) as cm:
            duplicate_city.clean()
        
        # Check if the error message correctly identifies the conflict
        self.assertIn("Rome", str(cm.exception))
        self.assertIn("Roma", str(cm.exception))

    def test_alternative_names_cannot_conflict_with_existing_city_names(self):
        """
        Ensures that if 'Paris' exists as a primary name, you can't add 
        'Paris' as an alternative name to 'London'.
        """
        City.objects.create(name="Paris", country=self.country)
        
        city = City(
            name="London",
            alternative_names="Paris, Londinium",
            country=self.country
        )
        
        with self.assertRaises(ValidationError):
            city.clean()

    def test_case_insensitivity_and_spacing(self):
        """
        Tests that 'rome ' (with space/lowercase) still triggers 
        the duplicate check against 'Rome'.
        """
        City.objects.create(name="Roma", alternative_names="Rome", country=self.country)
        
        city = City(name="rome ", country=self.country) # lowercase and extra space
        
        with self.assertRaises(ValidationError):
            city.clean()

    def test_partial_match_is_allowed(self):
        """
        Ensure that 'Ro' is NOT blocked by 'Rome'. 
        Validation should only block exact matches in the list.
        """
        City.objects.create(name="Roma", alternative_names="Rome", country=self.country)
        
        city = City(name="Ro", country=self.country)
        try:
            city.clean()
        except ValidationError:
            self.fail("Validation failed on a partial name match (Ro vs Rome)!")
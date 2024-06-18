from django.test import tag

from crm.forms.contact_form import ContactForm
from crm.models import Country
from crm.models import City
from crm.models import Request
from crm.utils.check_city import check_city
from tests.base_test_classes import BaseTestCase

# manage.py test tests.crm.utils.test_check_city --keepdb


@tag('TestCase')
class TesttestCheckCity(BaseTestCase):

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_check_city(self):
        country = Country.objects.create(
            name='Ukraine',
            url_name='Ukraine'
        )
        city = City.objects.create(
            name='Kyiv',
            alternative_names='Kiev, Київ',
            country=country
        )
        request = Request(
            request_for="City Test request",
            first_name="John",
            country=country,
            city_name='Kiev'
        )
        form = ContactForm()
        check_city(request, form)
        self.assertEqual(request.city, city)
        self.assertFalse(
            City.objects.filter(name='Kiev').exists(),
            "A duplicate city instance has been created."
        )

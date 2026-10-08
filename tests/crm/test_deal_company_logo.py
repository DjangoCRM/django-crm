import io
import shutil
import tempfile

from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.test import tag
from django.urls import reverse
from PIL import Image

from common.utils.helpers import get_department_id
from tests.base_test_classes import BaseTestCase
from tests.crm.test_deal import get_contact_request
from tests.crm.test_deal import get_test_deal
from tests.crm.test_request_methods import populate_db

MEDIA_ROOT = tempfile.mkdtemp()


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new('RGB', (64, 32), (200, 30, 30)).save(buf, format='PNG')
    return buf.getvalue()


# python manage.py test tests.crm.test_deal_company_logo --keepdb


@tag('TestCase')
@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestDealCompanyLogo(BaseTestCase):
    """The deal page shows the company's logo in Contact info (#544)."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        populate_db(cls)
        cls.contact_request = get_contact_request()
        cls.co_owner = None
        cls.department = Group.objects.get(id=get_department_id(cls.owner))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.deal = get_test_deal(self)
        self.url = reverse('site:crm_deal_change', args=(self.deal.id,))
        self.client.force_login(self.owner)

    def test_deal_page_shows_the_company_logo(self):
        company = self.deal.company
        company.logo = SimpleUploadedFile('acme.png', _png(), content_type='image/png')
        company.save()

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'src="{company.logo.url}"')
        self.assertContains(response, company.full_name)

    def test_deal_page_without_a_logo_shows_no_image(self):
        company = self.deal.company
        self.assertFalse(company.logo)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, company.full_name)
        self.assertNotContains(response, 'company_logos/')

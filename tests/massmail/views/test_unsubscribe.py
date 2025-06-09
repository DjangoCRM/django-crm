from django.contrib.contenttypes.models import ContentType
from django.test import tag
from django.urls import reverse

from crm.models.company import Company
from crm.models.contact import Contact
from massmail.models.mass_contact import MassContact
from tests.base_test_classes import BaseTestCase
from settings.models import MassmailSettings

# manage.py test tests.massmail.views.test_unsubscribe --keepdb


@tag('TestCase')
class TestUnsubscribe(BaseTestCase):

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_unsubscribe(self):
        company = Company.objects.create()
        contact = Contact.objects.create(company_id=company.id)
        content_type = ContentType.objects.get(app_label='crm', model='contact')
        mc = MassContact.objects.create(
            content_type=content_type, object_id=contact.id)
        url = reverse('unsubscribe', args=(mc.uuid,))
        home_url = reverse('site:index')
        massmail_settings = MassmailSettings.objects.get(id=1)
        unsubscribe_url = massmail_settings.unsubscribe_url
        massmail_settings.unsubscribe_url = home_url
        massmail_settings.save(update_fields=['unsubscribe_url'])

        response = self.client.get(url, follow=True)

        massmail_settings.unsubscribe_url = unsubscribe_url
        massmail_settings.save(update_fields=['unsubscribe_url'])
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(
            response.redirect_chain[0][0],
            home_url
        )
        mc.refresh_from_db()
        self.assertEqual(mc.massmail, False)
        contact.refresh_from_db()
        self.assertEqual(contact.massmail, False)

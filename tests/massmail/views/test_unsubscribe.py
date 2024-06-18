from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import tag
from django.urls import reverse

from massmail.models.mass_contact import MassContact
from tests.base_test_classes import BaseTestCase

# manage.py test tests.massmail.views.test_unsubscribe --keepdb


@tag('TestCase')
class TestUnsubscribe(BaseTestCase):

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_unsubscribe(self):
        content_type = ContentType.objects.get(app_label='crm', model='contact')
        mc = MassContact.objects.create(content_type=content_type, object_id=1)
        url = reverse('unsubscribe', args=(mc.uuid,))
        home_url = reverse('site:index')
        with self.settings(UNSUBSCRIBE_URL=home_url):
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200, response.reason_phrase)
            self.assertEqual(
                response.redirect_chain[0][0],
                settings.UNSUBSCRIBE_URL
            )
        mc.refresh_from_db()
        self.assertEqual(mc.massmail, False)

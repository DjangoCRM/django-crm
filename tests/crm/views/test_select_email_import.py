from django.test import tag
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from massmail.models.email_account import EmailAccount
from tests.base_test_classes import BaseTestCase

# manage.py test tests.crm.views.test_select_email_import.py --keepdb


@tag('TestCase')
class SelectEmailsImportView(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = USER_MODEL.objects.get(username="Eve.Superoperator.Co-worker")
        ea_data = dict(
            name="Compay Global Email Account",
            email_host="smtp.example.com",
            email_port=587, owner=cls.owner,
            email_host_user="Global@example.com",
            email_host_password='password',
            from_email="Global@example.com",
            main=True, do_import=True,
            email_use_tls=True, email_use_ssl=False,
        )
        cls.ea1 = EmailAccount.objects.create(**ea_data)
        ea_data['name'] = "Compay Local Email Account"
        ea_data['email_host_user'] = "Local@example.com"
        cls.ea2 = EmailAccount.objects.create(**ea_data)

    def test_select_email_import(self):
        # with self.settings(TESTING=True):
        self.client.force_login(self.owner)
        next_url = reverse("site:crm_request_changelist")
        select_emails_url = reverse("select_emails_import_request") + f"?next={next_url}"
        response = self.client.get(select_emails_url, follow=True)
        self.assertContains(response, self.ea1.name, status_code=200)
        self.assertContains(response, self.ea2.name, status_code=200)

        # submit form
        select_account_url = response.redirect_chain[0][0]
        data = {'choice': self.ea1.id}
        response = self.client.post(select_account_url, data, follow=True)
        self.assertContains(response, self.ea1.email_host_user, status_code=200)
        select_emails_url = response.redirect_chain[0][0]
        data = {'action': 'import', '15198': 'False', '15193': 'False',
                'ea_id': self.ea1.id, 'url': next_url}
        response = self.client.post(select_emails_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data['action'] = 'seen'
        response = self.client.post(select_emails_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

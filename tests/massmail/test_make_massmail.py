from django.test import tag
from django.urls import reverse

from crm.models import Company
from crm.models import Contact
from crm.models import Country
from crm.models import ClientType
from crm.models import Industry
from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from massmail.models import MailingOut, EmlMessage
from massmail.models.email_account import EmailAccount
from massmail.site.mailingoutadmin import no_redirect_url_str, vip_recipients_only_str, no_massmal_account_str
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials


# manage.py test tests.massmail.test_make_massmail --keepdb


@tag('TestCase')
class TestMakeMassmail(BaseTestCase):
    """Test create massmail for companies and contact using form"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        username_list = ("Andrew.Manager.Global",
                         "Darian.Manager.Co-worker.Head.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.user2 = users.get(username="Andrew.Manager.Global")
        cls.user = users.get(
            username="Darian.Manager.Co-worker.Head.Global")
        cls.user.is_superoperator = None
        department_id = get_department_id(cls.user)
        cls.user.department_id = department_id
        cls.country = Country.objects.first()
        cls.industry = Industry.objects.create(name='metallurgy', department_id=department_id)
        cls.industry.save()
        cls.client_type = ClientType.objects.create(
            name='manufacturer', department_id=department_id)
        cls.company1 = Company.objects.create(
            full_name="Test company 1",
            email="office@company1.com",
            owner=cls.user,
            department_id=department_id,
            country=cls.country,
            type=cls.client_type
        )
        cls.company1.industry.add(cls.industry)
        cls.company2 = Company.objects.create(
            full_name="Test company 2",
            email="office@company2.com",
            owner=cls.user,
            department_id=department_id,
            country=cls.country,
            type=cls.client_type
        )
        cls.company2.industry.add(cls.industry)
        cls.contact1 = Contact.objects.create(
            first_name='Name1',
            last_name='Last_name1',
            email="Name1@company1.com",
            company=cls.company1,
            owner=cls.user,
            department_id=department_id,
            country=cls.country,
        )
        cls.contact2 = Contact.objects.create(
            first_name='Name2',
            last_name='Last_name2',
            email="Name1@company2.com",
            company=cls.company2,
            owner=cls.user,
            department_id=department_id,
            country=cls.country,
        )
        cls.company_make_massmail_url = reverse("site:company_make_massmail")
        cls.ea = EmailAccount.objects.create(
            name='Email Account',
            email_host='smtp.example.com',
            email_host_user='andrew@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            owner=cls.user,
            main=True,
        )

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_no_account_for_massmail(self):
        """Getting warning - no email account for massmail."""
        self.client.force_login(self.user2)
        response = self.client.get(self.company_make_massmail_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(
            reverse('site:app_list', args=('crm',)),
            response.redirect_chain[-1][0]
        )

    def test_make_company_massmail(self):
        """Make massmail for companies using form."""
        self.client.force_login(self.user)
        response = self.client.get(self.company_make_massmail_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = self.get_form_data(response)
        response = self.client.post(
            self.company_make_massmail_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        try:
            mailing_out = MailingOut.objects.get(
                recipient_ids=f'{self.company1.id},{self.company2.id}'
            )
        except MailingOut.DoesNotExist:
            self.fail("The MailingOut instance DoesNotExist")

        # Testing the tips when saving the mailing_out
        change_url = reverse('site:massmail_mailingout_change', args=(mailing_out.id,))
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        eml_msg = EmlMessage.objects.create(
            subject='Test Subject',
            content='Test Content',
            owner=self.user,
        )
        data = get_adminform_initials(response)
        data['status'] = MailingOut.ACTIVE
        data['message'] = str(eml_msg.id)
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        messages = list(response.context['messages'])
        self.assertNoFormErrors(response)
        self.assertEqual(messages[0].message, vip_recipients_only_str)
        self.assertEqual(messages[1].message, no_redirect_url_str)
        self.ea.owner = self.user2
        self.ea.save(update_fields=['owner'])
        mailing_out.status = MailingOut.PAUSED
        mailing_out.save(update_fields=['status'])
        response = self.client.post(change_url, data, follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(messages[0].message, no_massmal_account_str)




    def test_make_contact_massmail(self):
        """Make massmail for contacts using form."""
        self.client.force_login(self.user)
        make_massmail_url = reverse("site:contact_make_massmail")
        response = self.client.get(make_massmail_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = self.get_form_data(response)
        response = self.client.post(make_massmail_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertTrue(
            MailingOut.objects.filter(
                recipient_ids=f'{self.contact1.id},{self.contact2.id}'
            ).exists(),
            "The Obj DoesNotExist"
        )

    def get_form_data(self, response):
        form = response.context['form']
        return {
            'before': form.base_fields['before'].initial,
            'after': form.base_fields['after'].initial,
            'industries': [str(self.industry.id)],
            'countries': [str(self.country.id)],
            'types': [str(self.client_type.id)],
        }

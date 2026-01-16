from django.contrib.contenttypes.models import ContentType
from django.test import tag
from crm.models import Contact, Company
from crm.utils.admfilters import ByVIPStatus
from massmail.models import EmailAccount, MassContact
from tests.base_test_classes import BaseTestCase



@tag('vip')
class TestCheckVipStatus(BaseTestCase):

    def setUp(self):
        self.vip_account = EmailAccount.objects.create(
            name='gmail',
            main=True,
            email_host='smtp.gmail.com',
            email_host_user='test@gmail.com',
            email_host_password='123456',
            from_email='test@gmail.com',
        )

        self.regular_account = EmailAccount.objects.create(
            name='hotmail',
            main=False,
            email_host='smtp.hotmail.com',
            email_host_user ='test@hotmail.com',
            email_host_password='password',
            from_email='test@hotmail.com',
        )
        self.company = Company.objects.create(full_name='TEST')

        self.vip_contact = Contact.objects.create(
            first_name='VIP',
            last_name='User',
            company=self.company)
        self.regular_contact = Contact.objects.create(
            first_name='Regular',
            last_name='User',
            company=self.company)

        content_type = ContentType.objects.get_for_model(Contact)


        MassContact.objects.create(
            content_type=content_type,
            object_id = self.vip_contact.id,
            email_account = self.vip_account,
        )

        MassContact.objects.create(
            content_type=content_type,
            object_id = self.regular_contact.id,
            email_account = self.regular_account,
        )

    def apply_filter(self, value):
        filter = ByVIPStatus(
            request = None,
            params={},
            model=Contact,
            model_admin=None,
        )

        filter.used_parameters = {'vip_status': value}
        return filter.queryset(None, Contact.objects.all())

    def test_vip_filter_returns_only_vip_contacts(self):

        result = self.apply_filter('yes')

        self.assertIn(self.vip_contact, result)
        self.assertNotIn(self.regular_contact, result)

    def test_non_vip_filter_returns_only_non_vip_contacts(self):

        result = self.apply_filter('no')
        self.assertIn(self.regular_contact, result)
        self.assertNotIn(self.vip_contact, result)





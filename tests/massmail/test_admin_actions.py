from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage import default_storage
from django.test import RequestFactory
from django.test import tag
from django.urls import reverse
from django.utils.translation import gettext as _

from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from crm.models import Lead
from massmail.admin_actions import make_mailing_out
from massmail.admin_actions import merge_mailing_outs
from massmail.admin_actions import specify_vip_recipients
from massmail.models.email_account import EmailAccount
from massmail.models.mass_contact import MassContact
from massmail.models.mailing_out import MailingOut
from tests.base_test_classes import BaseTestCase

# manage.py test tests.massmail.test_admin_actions --keepdb


@tag('TestCase')
class TesttestAdminActions(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        username_list = ("Andrew.Manager.Global",
                         "Darian.Manager.Co-worker.Head.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.owner = users.get(username="Andrew.Manager.Global")
        cls.owner2 = users.get(
            username="Darian.Manager.Co-worker.Head.Global")
        cls.ea = EmailAccount.objects.create(
            name='Email Account',
            email_host='smtp.example.com',
            email_port=587,
            email_host_user='andrew@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            main=True,
            massmail=True,
            owner=cls.owner,
        )
        cls.ea2 = EmailAccount.objects.create(
            name='Email Account 2',
            email_host='smtp.example.com',
            email_port=587,
            email_host_user='andrew2@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            main=False,
            massmail=True,
            owner=cls.owner,
        )
        cls.lead1 = Lead.objects.create(
            first_name='Bruno',
            email='Bruno@company.com',
            phone='+0182345678',
            company_name='Bruno Company LLC',
            owner=cls.owner
        )
        cls.lead2 = Lead.objects.create(
            first_name='Michael',
            email='Michael@testcompany.com',
            phone='+0182345678',
            owner=cls.owner
        )
        cls.lead3 = Lead.objects.create(
            first_name='Michael',
            email='Michael@testcompany.com',
            phone='+0182345678',
            owner=cls.owner
        )
        cls.lead_content_type = ContentType.objects.get_for_model(Lead)
        cls.mc = MassContact.objects.create(
            content_type=cls.lead_content_type,
            object_id=cls.lead1.id,
            email_account=cls.ea,
            massmail=True
        )
        cls.factory = RequestFactory()

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.owner)

    def test_specify_vip_recipients(self):
        lead_ids = (self.lead1.id, self.lead2.id, self.lead3.id)
        queryset = Lead.objects.filter(
            id__in=lead_ids
        )
        data = {ACTION_CHECKBOX_NAME: [str(i) for i in lead_ids]}
        with self.settings(
                MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'
        ):
            self.request = self.factory.post(
                reverse('site:massmail_mailingout_changelist'), data
            )
            self.request.user = self.owner
            self.request.user.department_id = get_department_id(self.owner)
            self.request._messages = default_storage(self.request)
            response = specify_vip_recipients(None, self.request, queryset)
            self.assertEqual(response.status_code, 302, response.reason_phrase)
            mc_num = MassContact.objects.filter(
                object_id__in=(self.lead1.id, self.lead2.id, self.lead3.id),
                content_type=self.lead_content_type,
                email_account=self.ea
            ).count()
            self.assertEqual(3, mc_num)

    def test_merge_mailing_outs(self):
        mo, mo1 = self.create_mailing_outs()
        queryset = MailingOut.objects.filter(id__in=(mo.id, mo1.id))
        with self.settings(
                MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'
        ):
            self.request = self.factory.get(
                reverse('site:massmail_mailingout_changelist'))
            self.request.user = self.owner
            self.request.user.department_id = get_department_id(self.owner)
            self.request._messages = default_storage(self.request)
            response = merge_mailing_outs(None, self.request, queryset)
            self.assertEqual(response.status_code, 302, response.reason_phrase)
            self.assertTrue(
                MailingOut.objects.filter(
                    name="Test MO" + f' ({_("united")})',
                    recipient_ids='1,2,3,4',
                    recipients_number=4
                ).exists(),
                "Mailing out not created"
            )
            self.assertFalse(
                MailingOut.objects.filter(
                    id__in=(mo.id, mo1.id)
                ).exists(),
                "Mailing outs not deleted"
            )

    def test_make_mailing_out(self):
        lead4 = Lead.objects.create(
            first_name='Michael',
            email='Michael@testcompany.com',
            phone='+0182345678',
            owner=self.owner
        )
        mc = MassContact.objects.create(
            content_type=self.lead_content_type,
            object_id=lead4.id,
            email_account=self.ea,
            massmail=False
        )
        queryset = Lead.objects.all()
        with self.settings(
                MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'
        ):
            self.request = self.factory.get(
                reverse('site:crm_lead_changelist'))
            self.request.user = self.owner
            self.request.user.department_id = get_department_id(self.owner)
            self.request._messages = default_storage(self.request)
            response = make_mailing_out(None, self.request, queryset)
            self.assertEqual(response.status_code, 302, response.reason_phrase)
            corrected_qs = queryset.exclude(id=lead4.id)
            recipient_ids = ",".join([str(x.id) for x in corrected_qs])
            try:
                mailing_out = MailingOut.objects.get(
                    recipient_ids=recipient_ids,
                    recipients_number=corrected_qs.count()
                )
            except MailingOut.DoesNotExist:
                self.fail("Mailing out not created")
            change_url = reverse(
                'site:massmail_mailingout_change', args=(mailing_out.id,)
            )
            self.assertEqual(change_url, response.url)

    def test_merge_with_multiple_content_types(self):
        mo, mo1 = self.create_mailing_outs()
        mo.content_type_id = 2
        mo.save(update_fields=['content_type_id'])
        queryset = MailingOut.objects.filter(id__in=(mo.id, mo1.id))
        with self.settings(
            MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'
        ):
            self.request = self.factory.get(
                reverse('site:massmail_mailingout_changelist'))
            self.request.user = self.owner
            self.request.user.department_id = get_department_id(self.owner)
            self.request._messages = default_storage(self.request)
            response = merge_mailing_outs(None, self.request, queryset)
            self.assertEqual(response.status_code, 302, response.reason_phrase)
            queryset_num = MailingOut.objects.filter(
                id__in=(mo.id, mo1.id)
            ).count()
            self.assertEqual(2, queryset_num, "Mailing outs deleted")

    def test_multiple_owners(self):
        lead4 = Lead.objects.create(
            first_name='Michael',
            email='Michael@testcompany.com',
            phone='+0182345678',
            owner=self.owner2
        )
        queryset = Lead.objects.all()
        with self.settings(
                MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'
        ):
            self.request = self.factory.get(
                reverse('site:crm_lead_changelist'))
            self.request.user = self.owner
            self.request.user.department_id = get_department_id(self.owner)
            self.request._messages = default_storage(self.request)
            response = make_mailing_out(None, self.request, queryset)
            self.assertEqual(response.status_code, 302, response.reason_phrase)

    def create_mailing_outs(self):
        department_id = get_department_id(self.owner)
        mo = MailingOut.objects.create(
            name="Test MO",
            recipient_ids='1,2',
            recipients_number=2,
            content_type_id=1,
            owner=self.owner,
            department_id=department_id
        )
        mo1 = MailingOut.objects.create(
            name="Test MO2",
            recipient_ids='3,4',
            recipients_number=2,
            content_type_id=1,
            owner=self.owner,
            department_id=department_id
        )
        return mo, mo1

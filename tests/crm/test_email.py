from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage import default_storage
from django.core import mail
from django.test import override_settings
from django.test import RequestFactory
from django.test import tag
from django.urls import reverse

from common.models import TheFile
from common.templatetags.util import FILE_ERROR_SUBJ
from common.utils.helpers import get_delta_date
from common.utils.helpers import USER_MODEL
from common.utils.helpers import get_department_id
from crm.models import Deal
from crm.models import CrmEmail
from crm.site.crmemailadmin import CrmEmailAdmin
from crm.site.crmadminsite import crm_site
from crm.utils.ticketproc import get_ticket_str
from crm.utils.ticketproc import new_ticket
from massmail.models.email_account import EmailAccount
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_content_file
from tests.utils.helpers import get_adminform_initials

# manage.py test tests.crm.test_email --keepdb


email_admin = CrmEmailAdmin(model=CrmEmail, admin_site=crm_site)


@tag('TestCase')
class TestEmail(BaseTestCase):
    """Emil sending test"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.ea = EmailAccount.objects.create(
            name='CRM Email Account',
            email_host='smtp.example.com',
            email_port=587,
            email_host_user='andrew@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            main=True,
            email_use_tls=True,
            email_use_ssl=False,
            owner=cls.owner,
        )

        cls.department_id = get_department_id(cls.owner)
        cls.factory = RequestFactory()
        # create and save test email to reply it
        cls.eml = CrmEmail.objects.create(**{
            'from_field': '"Michael" <Michael@testcompany.com>',
            'to': "Andrew <andrew@example.com>",
            'subject': 'Product inquiry',
            'content': 'Hello!',
            'owner': cls.owner,
            'department_id': cls.department_id,
            'ticket': new_ticket()
        })
        cls.add_url = reverse("site:crm_crmemail_add")
        cls.content_type = ContentType.objects.get_for_model(cls.eml)

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.add_request = self.factory.get(self.add_url)
        self.add_request.user = self.owner
        self.add_request.user.is_superoperator = False
        self.add_request.user.department_id = self.department_id
        self.client.force_login(self.owner)
        
    def test_view_non_existent_email(self):
        obj_id = 9223372036854775807
        self.assertFalse(
            CrmEmail.objects.filter(id=obj_id).exists(),
            "Email exists"
        )
        url = reverse("site:crm_crmemail_change", args=(obj_id,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        url = response.redirect_chain[-1][0]
        self.assertEqual(reverse("site:crm_crmemail_changelist"), url)

    def test_form_not_enough_data(self):
        """Test for clearing a form with insufficient data."""
        self.form = email_admin.get_form(self.add_request)
        form = self.form({'to': '"Michael" <Michael@testcompany.com>'})
        self.assertEqual(form.is_valid(), False)
        self.assertTrue(form['content'].errors)

    @override_settings(
        MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage',
    )
    def test_form_save(self):
        """Test for saving a completed form."""
        self.form = email_admin.get_form(self.add_request)
        form = self.form({
            'to': '"Michael" <Michael@testcompany.com>',
            'subject': 'Product inquiry ',
            'content': 'Hello!',
        })
        self.assertEqual(form.is_valid(), True)
        form.save()
        self.assertTrue(
            CrmEmail.objects.filter(
                to='"Michael" <Michael@testcompany.com>'
            ).exists(),
            "The Email object has not been saved."
        )

    def test_save_new_email(self):
        response = self.client.get(self.add_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['owner'] = str(self.owner.id)
        data['to'] = "'Michael' <Michael@testcompany.com>"
        data['subject'] = "Product inquiry"
        data['content'] = 'Hello!'

        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        self.assertTrue(
            CrmEmail.objects.filter(
                to="'Michael' <Michael@testcompany.com>"
            ).exists(),
            "Email object not saved"
        )

    def test_attach_email_file_to_deal(self):
        deal = Deal.objects.create(
            name="Test deal",
            next_step=settings.FIRST_STEP,
            next_step_date=get_delta_date(1),
            owner=self.owner,
            department_id=self.department_id
        )
        eml = CrmEmail.objects.create(**{
            'to': '"Michael" <Michael@testcompany.com>',
            'from_field': "Andrew <andrew@example.com>",
            'subject': 'File',
            'content': 'File in attachment!',
            'owner': self.owner,
            'department_id': self.department_id,
            'ticket': new_ticket(),
            'deal': deal
        })

        file_name, content_file = get_content_file(self._testMethodName)
        file = TheFile.objects.create(
            file=content_file,
            content_type=self.content_type,
            object_id=eml.id
        )
        content_file.file.close()
        # open test email in change view
        url = reverse("site:crm_crmemail_change", args=(eml.id,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['common-thefile-content_type-object_id-0-attached_to_deal'] = True
        # submit 'save' button
        response = self.client.post(url, data, follow=True)
        data['common-thefile-content_type-object_id-0-file'].file.close()
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        deal_file = deal.files.first()
        if deal_file is None:
            self.fail('There is no attached file.')
        else:
            self.assertIn(file_name.split('.')[0], deal_file.file.name)

        # detach the file from a deal
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        del data['common-thefile-content_type-object_id-0-attached_to_deal']
        # `RequestFactory` is used instead of `self.client` to avoid "PermissionError: [WinError 32]
        # The process cannot access the file because it is being used by another process"
        request = self.factory.post(url, data)
        request.user = self.owner
        request.user.department_id = self.department_id
        request.user.is_superoperator = False
        request.user.is_chief = False
        request.user.is_manager = True
        request.user.is_operator = False
        context = response.context or response.context_data
        request.COOKIES[settings.CSRF_COOKIE_NAME] = str(context['csrf_token'])
        request.META[settings.CSRF_HEADER_NAME] = str(context['csrf_token'])
        data['common-thefile-content_type-object_id-0-file'].file.close()

        with self.settings(
                MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'
        ):
            request._messages = default_storage(request)
            response = email_admin.change_view(request, str(eml.id))
        self.assertEqual(response.status_code, 302, response.reason_phrase)
        self.assertFalse(deal.files.exists(), 'The file is attached to deal.')
        file.file.delete()

        # test email with missing file
        url = reverse("site:crm_deal_change", args=(deal.id,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(FILE_ERROR_SUBJ.format(file.id), mail.outbox[0].subject)
        mail.outbox = []

    def test_reply_email(self):
        """Email reply test."""
        # open test email in change view
        url = reverse("site:crm_crmemail_change", args=(self.eml.id,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # submit 'reply' button
        data['_reply'] = ''
        response = self.client.post(url, data, follow=True)
        msg = 'http status code is not 200 ok'
        self.assertEqual(response.status_code, 200, msg)
        self.assertEqual(
            response.context['adminform'].form.initial['subject'],
            'Re: ' + self.eml.subject + get_ticket_str(self.eml.ticket)
        )
        data = get_adminform_initials(response)
        data['content'] = "Dear Michael."
        # submit 'send' button
        data['_send'] = ''
        url = response.redirect_chain[-1][0]
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200, msg)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, data['subject'].strip())
        mail.outbox = []

    @override_settings(LANGUAGE_CODE='en')
    def test_forward_email(self):
        """Email forward test."""
        # open test email in change view
        url = reverse("site:crm_crmemail_change", args=(self.eml.id,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # submit 'forward' button
        data['_forward'] = ''
        response = self.client.post(url, data, follow=True)
        msg = 'http status code is not 200 ok'
        self.assertEqual(response.status_code, 200, msg)
        self.assertEqual(
            response.context['adminform'].form.initial['subject'],
            'Fwd: ' + self.eml.subject + get_ticket_str(self.eml.ticket)
        )

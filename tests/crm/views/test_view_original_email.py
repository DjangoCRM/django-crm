from django.test import RequestFactory
from django.test import tag

from common.utils.helpers import USER_MODEL
from common.utils.helpers import get_department_id
from crm.models import CrmEmail
from crm.views.view_original_email import _get_ea_eml_uid
from massmail.models import EmailAccount
from tests.base_test_classes import BaseTestCase


@tag('TestCase')
class TestGetOriginalEmailAccess(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.other_user = USER_MODEL.objects.get(
            username="Marina.Co-worker.Global"
        )
        cls.email_account = EmailAccount.objects.create(
            name='CRM Email Account',
            email_host='smtp.example.com',
            email_host_user='andrew@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            owner=cls.owner,
            department_id=get_department_id(cls.owner),
        )
        cls.email = CrmEmail.objects.create(
            subject='Original email access test',
            content='Test content',
            to='andrew@example.com',
            email_host_user=cls.email_account.email_host_user,
            owner=cls.owner,
            department_id=get_department_id(cls.owner),
        )

    def setUp(self):
        self.request = RequestFactory().get('/')

    def test_visible_email_and_account_are_returned(self):
        self.request.user = self.owner
        self.request.user.department_id = get_department_id(self.owner)

        ea, eml, uid, err = _get_ea_eml_uid(
            self.request, self.email.id, None, None
        )

        self.assertFalse(err)
        self.assertEqual(self.email_account, ea)
        self.assertEqual(self.email, eml)
        self.assertEqual(self.email.uid, uid)

    def test_inaccessible_crm_email_is_reported_as_missing(self):
        self.request.user = self.other_user
        self.request.user.department_id = get_department_id(self.other_user)

        _, _, _, err = _get_ea_eml_uid(
            self.request, self.email.id, None, None
        )

        self.assertIn(str(self.email.id), str(err))
        self.assertIn(str(CrmEmail._meta.verbose_name), str(err))

    def test_inaccessible_email_account_is_reported_as_missing(self):
        self.request.user = self.owner
        self.request.user.department_id = get_department_id(self.owner)
        inaccessible_account = EmailAccount.objects.create(
            name='Other Email Account',
            email_host='smtp.other.example.com',
            email_host_user='other@example.com',
            email_host_password='password',
            from_email='other@example.com',
            owner=self.other_user,
        )

        _, _, _, err = _get_ea_eml_uid(
            self.request, None, inaccessible_account.id, None
        )

        self.assertIn(str(inaccessible_account.id), str(err))
        self.assertIn(str(EmailAccount._meta.verbose_name), str(err))

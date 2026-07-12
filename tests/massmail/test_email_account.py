from django.contrib.auth.models import Permission
from django.test import tag
from django.urls import reverse

from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from massmail.models import EmailAccount
from tests.base_test_classes import BaseTestCase


# python manage.py test tests.massmail.test_email_account --keepdb


@tag('TestCase')
class TestEmailAccountCopy(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        users = USER_MODEL.objects.filter(
            username__in=(
                "Andrew.Manager.Global",
                "Darian.Manager.Co-worker.Head.Global",
            )
        )
        cls.owner = users.get(username="Andrew.Manager.Global")
        cls.other_user = users.get(
            username="Darian.Manager.Co-worker.Head.Global"
        )
        cls.owner.user_permissions.add(
            Permission.objects.get(
                codename='add_emailaccount',
                content_type__app_label='massmail',
            )
        )
        cls.account = EmailAccount.objects.create(
            name='Primary account',
            main=True,
            massmail=True,
            do_import=True,
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_host_user='andrew@example.com',
            email_host_password='password',
            email_app_password='app-password',
            email_port=587,
            from_email='sales@example.com',
            email_use_tls=True,
            email_imail_ssl_certfile='/certs/account.pem',
            email_imail_ssl_keyfile='/certs/account.key',
            refresh_token='refresh-token',
            owner=cls.owner,
            co_owner=cls.other_user,
            department_id=get_department_id(cls.owner),
            report='runtime report',
            today_count=17,
            start_incoming_uid=42,
        )
        cls.add_url = reverse("site:massmail_emailaccount_add")
        cls.changelist_url = reverse(
            "site:massmail_emailaccount_changelist"
        )

    def setUp(self):
        self.client.force_login(self.owner)

    def test_changelist_contains_copy_link(self):
        response = self.client.get(self.changelist_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'{self.add_url}?copy_email_account={self.account.id}',
        )

    def test_changelist_hides_copy_link_without_add_permission(self):
        account = EmailAccount.objects.create(
            name='Read-only account',
            email_host='smtp.readonly.example.com',
            email_host_user='readonly@example.com',
            email_host_password='password',
            from_email='readonly@example.com',
            owner=self.other_user,
            department_id=get_department_id(self.other_user),
        )
        self.client.force_login(self.other_user)

        response = self.client.get(self.changelist_url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            f'{self.add_url}?copy_email_account={account.id}',
        )

    def test_copy_prefills_configuration_without_runtime_state(self):
        response = self.client.get(
            self.add_url,
            {'copy_email_account': self.account.id},
        )

        self.assertEqual(response.status_code, 200)
        initial = response.context['adminform'].form.initial
        self.assertEqual(initial['name'], self.account.name)
        self.assertIs(initial['main'], False)
        self.assertIs(initial['massmail'], True)
        self.assertIs(initial['do_import'], True)
        self.assertEqual(initial['email_host'], self.account.email_host)
        self.assertEqual(initial['imap_host'], self.account.imap_host)
        self.assertEqual(
            initial['email_host_user'], self.account.email_host_user
        )
        self.assertEqual(
            initial['email_host_password'],
            self.account.email_host_password,
        )
        self.assertEqual(
            initial['email_app_password'], self.account.email_app_password
        )
        self.assertEqual(initial['email_port'], self.account.email_port)
        self.assertEqual(initial['from_email'], self.account.from_email)
        self.assertIs(initial['email_use_tls'], True)
        self.assertIs(initial['email_use_ssl'], False)
        self.assertEqual(
            initial['email_imail_ssl_certfile'],
            self.account.email_imail_ssl_certfile,
        )
        self.assertEqual(
            initial['email_imail_ssl_keyfile'],
            self.account.email_imail_ssl_keyfile,
        )
        self.assertEqual(initial['refresh_token'], self.account.refresh_token)
        self.assertEqual(initial['owner'], self.account.owner)
        self.assertEqual(initial['co_owner'], self.account.co_owner)
        self.assertEqual(initial['department'], self.account.department)
        self.assertNotIn('report', initial)
        self.assertNotIn('today_count', initial)
        self.assertNotIn('start_incoming_uid', initial)

    def test_copy_does_not_read_another_users_account(self):
        inaccessible_account = EmailAccount.objects.create(
            name='Other account',
            email_host='smtp.other.example.com',
            email_host_user='other@example.com',
            email_host_password='password',
            from_email='other@example.com',
            owner=self.other_user,
            department_id=get_department_id(self.other_user),
        )

        response = self.client.get(
            self.add_url,
            {'copy_email_account': inaccessible_account.id},
        )

        self.assertEqual(response.status_code, 200)
        initial = response.context['adminform'].form.initial
        self.assertNotIn('name', initial)
        self.assertEqual(initial['owner'], self.owner.id)

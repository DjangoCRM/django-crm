from django.forms import PasswordInput
from django.test import SimpleTestCase

from massmail.forms.email_account_form import EmailAccountAdminForm
from massmail.models import EmailAccount
from sharedkernel.credentials import SECRET_FIELD_NAMES
from tests.fixtures.email_account_credentials import app_password_account


class EmailAccountAdminFormTests(SimpleTestCase):
    def test_secret_fields_use_write_only_password_widgets(self):
        form = EmailAccountAdminForm()
        for field_name in SECRET_FIELD_NAMES:
            widget = form.fields[field_name].widget
            self.assertIsInstance(widget, PasswordInput)
            self.assertFalse(widget.render_value)

    def test_blank_secret_preserves_existing_instance_value(self):
        account = app_password_account()
        instance = EmailAccount(
            pk=account.pk,
            email_host_password=account.email_host_password,
            email_app_password=account.email_app_password,
        )
        form = EmailAccountAdminForm(instance=instance)
        form.cleaned_data = {'email_host_password': '', 'email_app_password': ''}

        self.assertEqual(form.clean_email_host_password(), 'host-secret')
        self.assertEqual(form.clean_email_app_password(), 'app-secret')

    def test_new_instance_requires_secret_values(self):
        form = EmailAccountAdminForm(
            data={
                'name': 'New account',
                'email_host': 'smtp.example.com',
                'imap_host': 'imap.example.com',
                'email_host_user': 'new@example.com',
                'email_host_password': '',
                'email_app_password': '',
                'refresh_token': '',
                'email_imail_ssl_keyfile': '',
                'email_port': 587,
                'from_email': 'new@example.com',
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn('email_host_password', form.errors)

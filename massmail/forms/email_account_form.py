from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from massmail.models import EmailAccount
from sharedkernel.credentials import SECRET_FIELD_NAMES

SECRET_REQUIRED_MSG = _(
    'Enter a value for this credential before saving a new account.'
)


class EmailAccountAdminForm(forms.ModelForm):
    class Meta:
        model = EmailAccount
        fields = '__all__'
        widgets = {
            field_name: forms.PasswordInput(render_value=False)
            for field_name in SECRET_FIELD_NAMES
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in SECRET_FIELD_NAMES:
            if field_name not in self.fields:
                continue
            self.fields[field_name].widget = forms.PasswordInput(render_value=False)
            self.fields[field_name].required = False

    def clean_email_host_password(self):
        return self._clean_secret_field('email_host_password')

    def clean_email_app_password(self):
        return self._clean_secret_field('email_app_password')

    def clean_refresh_token(self):
        return self._clean_secret_field('refresh_token')

    def clean_email_imail_ssl_keyfile(self):
        return self._clean_secret_field('email_imail_ssl_keyfile')

    def _clean_secret_field(self, field_name: str) -> str:
        value = self.cleaned_data.get(field_name, '')
        if value:
            return value
        if self.instance.pk:
            return getattr(self.instance, field_name)
        raise ValidationError(SECRET_REQUIRED_MSG)

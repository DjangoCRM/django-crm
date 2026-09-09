import requests
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from common.utils.helpers import send_crm_email
from crm.models import LeadSource
from crm.models.request import ATTRIBUTION_FIELDS
from crm.models.request import ATTRIBUTION_MAX_LENGTH


def get_attribution_data(query_params):
    attribution = {}
    for field in ATTRIBUTION_FIELDS:
        value = (query_params.get(field, '') or '').strip()
        if value and len(value) <= ATTRIBUTION_MAX_LENGTH:
            attribution[field] = value
    return attribution


class ContactForm(forms.Form):

    name = forms.CharField(
        label=_("Your name"),
        max_length=200
    )
    email = forms.EmailField(
        label=_("Your E-mail")
    )
    subject = forms.CharField(
        label=_("Subject"),
        max_length=200
    )
    phone = forms.CharField(
        label=_("Phone number (with country code)"),
        max_length=200
    )
    company = forms.CharField(
        label=_("Company name"),
        max_length=200
    )
    message = forms.CharField(
        label=_("Message"),
        required=False,
        widget=forms.Textarea
    )
    country = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.HiddenInput
    )
    city = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.HiddenInput
    )
    leadsource_token = forms.UUIDField(
        widget=forms.HiddenInput
    )
    utm_source = forms.CharField(
        max_length=ATTRIBUTION_MAX_LENGTH,
        required=False,
        widget=forms.HiddenInput,
    )
    utm_medium = forms.CharField(
        max_length=ATTRIBUTION_MAX_LENGTH,
        required=False,
        widget=forms.HiddenInput,
    )
    utm_campaign = forms.CharField(
        max_length=ATTRIBUTION_MAX_LENGTH,
        required=False,
        widget=forms.HiddenInput,
    )
    utm_term = forms.CharField(
        max_length=ATTRIBUTION_MAX_LENGTH,
        required=False,
        widget=forms.HiddenInput,
    )
    utm_content = forms.CharField(
        max_length=ATTRIBUTION_MAX_LENGTH,
        required=False,
        widget=forms.HiddenInput,
    )
    gclid = forms.CharField(
        max_length=ATTRIBUTION_MAX_LENGTH,
        required=False,
        widget=forms.HiddenInput,
    )
    fbclid = forms.CharField(
        max_length=ATTRIBUTION_MAX_LENGTH,
        required=False,
        widget=forms.HiddenInput,
    )

    def clean(self):
        super().clean()
        recaptcha_response = self.data.get("g-recaptcha-response")

        if recaptcha_response:
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            if "error-codes" in result and settings.ADMINS:
                leadsource_token = self.cleaned_data['leadsource_token']
                leadsource = LeadSource.objects.filter(uuid=leadsource_token).first()
                send_crm_email(
                    "reCaptcha error",
                    f"error-codes: {result['error-codes']}<br><br>"
                    f"LeadSource token: {leadsource_token}<br><br>"
                    f"LeadSource: {leadsource}",
                    [adr[1] for adr in settings.ADMINS]
                )
            if not result['success'] or "error-codes" in result:
                msg = _("Sorry, invalid reCAPTCHA. Please try again or send an email.")
                raise forms.ValidationError(msg)

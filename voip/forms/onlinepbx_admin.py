from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _


class OnlinePBXJSONForm(forms.Form):
    payload = forms.CharField(
        label=_('Payload (JSON or form-like key=value&k2=v2)'),
        required=False,
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        help_text=_('Provide JSON body for JSON endpoints or form-encoded string for x-www-form-urlencoded. Leave empty if not required.'),
    )
    use_json = forms.BooleanField(
        label=_('Send as JSON body'),
        initial=False,
        required=False,
        help_text=_('If checked, the payload will be sent as JSON; otherwise as application/x-www-form-urlencoded'),
    )

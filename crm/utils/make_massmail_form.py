from typing import Optional
from typing import Type
from typing import Union
from datetime import date
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext_lazy as _

from common.utils.helpers import get_today
from crm.models import ClientType
from crm.models import Company
from crm.models import Contact
from crm.models import Country
from crm.models import Industry


class MassmailFormBase(forms.Form):

    def clean(self):
        cleaned_data = super().clean()
        before = cleaned_data.get("before")
        after = cleaned_data.get("after")

        if after > before:
            raise forms.ValidationError(
                _("""Error: The date you set as 'Created before' has to be later 
                than the date of 'Created after'.""")
            )


def get_massmail_form(request: WSGIRequest, model: Union[Company, Contact],
                      min_date: Optional[date] = None) -> Type[MassmailFormBase]:
    form = MassmailFormBase

    form.base_fields['industries'] = forms.ModelMultipleChoiceField(
        queryset=Industry.objects.filter(
            **{f'{Company._meta.model_name}__owner': request.user}
            ).distinct().order_by('name'),
        required=False,
        widget=FilteredSelectMultiple(_("Industries"), False, )
    )
    form.base_fields['countries'] = forms.ModelMultipleChoiceField(
        queryset=Country.objects.filter(
            **{f'{model._meta.model_name}__owner': request.user}    # NOQA
        ).distinct().order_by('name'),
        required=False,
        widget=FilteredSelectMultiple(_("Countries"), False, )
    )
    form.base_fields['types'] = forms.ModelMultipleChoiceField(
        queryset=ClientType.objects.filter(
            **{f'{Company._meta.model_name}__owner': request.user}
        ).distinct().order_by('name'),
        required=False,
        widget=FilteredSelectMultiple(_("Types"), False, )
    )
    form.base_fields['before'] = forms.DateField(
        widget=AdminDateWidget(),
        initial=get_today(),
        label=_('Created before')
    )
    form.base_fields['after'] = forms.DateField(
        widget=AdminDateWidget(),
        initial=min_date,
        label=_('Created after')
    )
    return form

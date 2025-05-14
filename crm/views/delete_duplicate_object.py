import re
from django import forms
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.views import View

from common.models import TheFile
from crm.models import Contact
from crm.models import Company
from crm.models import Deal
from crm.models import Lead
from crm.models import Request
from crm.models import CrmEmail
from crm.models.country import City
from crm.site.crmadminsite import crm_site
from massmail.models import MailingOut
from massmail.models import MassContact


class DeleteDuplicateObject(View):
    template_name = 'crm/select_original_obj.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.form_class_data = {
            Contact: (Request, 'contact'),
            Company: (Contact, 'company'),
            Lead: (Request, 'lead'),
            City: (Company, 'city')
        }
        self.form_class = None
        self.content_type = None
        self.model = None
        self.form_model = None
        self.field = None
        self.success_url = ''
        self.duplicate_id = None
        self.original_id = None
        self.original = None
        self.duplicate = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.content_type = ContentType.objects.get(id=kwargs['content_type_id'])
        self.model = self.content_type.model_class()
        self.form_model, self.field = self.form_class_data[self.model]
        self.form_class = self.get_form_class()
        self.duplicate_id = kwargs['object_id']

    def get(self, request, *args, **kwargs):
        context = dict(
            crm_site.each_context(request),
            opts=Request._meta,
        )
        context['form'] = self.form_class()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            self. original_id = request.POST.get(self.field)
            self.original = self.model.objects.get(id=self.original_id)
            self.duplicate = self.model.objects.get(id=self.duplicate_id)
            self.relate_to()
            self.update_fields()

            self.duplicate.delete()
            MassContact.objects.filter(
                content_type=self.content_type,
                object_id=self.duplicate_id,
            ).delete()
            messages.success(
                request,
                _('The duplicate object has been correctly deleted.')
            )
            try:
                url = reverse(f"site:crm_{self.model._meta.model_name}_changelist")  # NOQA
            except NoReverseMatch:
                url = reverse(f"admin:crm_{self.model._meta.model_name}_changelist")  # NOQA
            return HttpResponseRedirect(url)

    def relate_to(self) -> None:
        field, models = self.get_data(self.model)
        for model in models:
            kwarg1 = {field: self.duplicate_id}
            kwarg2 = {field: self.original_id}
            objects = model.objects.filter(**kwarg1)
            objects.update(**kwarg2)

        # re_str string must be acceptable for MySQL and PostgreSQL
        re_str = fr"^{self.duplicate_id},|,{self.duplicate_id},|,{self.duplicate_id}$"
        mailing_outs = MailingOut.objects.filter(recipient_ids__regex=re_str)
        for mo in mailing_outs:
            ids = mo.recipient_ids
            ids = re.sub(fr"^{self.duplicate_id},", f"{self.original_id},", ids)
            ids = re.sub(fr",{self.duplicate_id},", f",{self.original_id},", ids)
            ids = re.sub(fr",{self.duplicate_id}$", f",{self.original_id}", ids)
            mo.recipient_ids = ids
            mo.save()

        TheFile.objects.filter(
            content_type=self.content_type,
            object_id=self.duplicate_id
        ).update(object_id=self.original_id)

    @staticmethod
    def get_data(model):
        data = {
            Company: {
                'field': 'company',
                'models': (Deal, Contact, CrmEmail, Request)
            },
            Contact: {
                'field': 'contact',
                'models': (Deal, Request, CrmEmail)
            },
            Lead: {
                'field': 'lead',
                'models': (Deal, CrmEmail, Request)
            },
            City: {
                'field': 'city',
                'models': (Company, Request, Lead)
            },
        }
        return data[model]['field'], data[model]['models']

    def get_form_class(self):
        class SelectObjForm(forms.ModelForm):
            class Meta:
                model = self.form_model
                fields = [self.field]
                widgets = {
                    self.field: ForeignKeyRawIdWidget(
                        self.form_model._meta.get_field(self.field).remote_field, crm_site)  # NOQA
                }
        return SelectObjForm

    def update_fields(self) -> None:
        data = {
            Company: {
                'fields': [
                    'address',
                    'city_name',
                    'city',
                    'country',
                    'description',
                    'email',
                    'full_name',
                    'lead_source',
                    'phone',
                    'registration_number',
                    'type',
                    'was_in_touch',
                    'website',
                ],
                'm2m_fields': ['industry', 'tags']
            },
            Contact: {
                'fields': [
                    'address',
                    'birth_date',
                    'city_name',
                    'city',
                    'company',
                    'country',
                    'description',
                    'email',
                    'first_name',
                    'last_name',
                    'lead_source',
                    'middle_name',
                    'mobile',
                    'other_phone',
                    'phone',
                    'secondary_email',
                    'sex',
                    'title',
                    'token',
                    'was_in_touch',
                ],
                'm2m_fields': ['tags']
            },
            Lead: {
                'fields': [
                    'address',
                    'birth_date',
                    'city_name',
                    'city',
                    'company_address',
                    'company_email',
                    'company_name',
                    'company_phone',
                    'country',
                    'description',
                    'email',
                    'first_name',
                    'last_name',
                    'lead_source',
                    'middle_name',
                    'mobile',
                    'other_phone',
                    'phone',
                    'secondary_email',
                    'sex',
                    'title',
                    'type',
                    'was_in_touch',
                    'website'
                ],
                'm2m_fields': ['industry', 'tags']
            },
            City: {
                'fields': [
                    'name',
                    'alternative_names',
                    'country'
                ],
                'm2m_fields': []
            },
        }
        for f in data[self.model]['fields']:
            if not getattr(self.original, f) and getattr(self.duplicate, f):
                setattr(self.original, f, getattr(self.duplicate, f))
        self.original.save()
        for f in data[self.model]['m2m_fields']:
            objects = getattr(self.duplicate, f).all()
            if objects:
                getattr(self.original, f).add(*objects)

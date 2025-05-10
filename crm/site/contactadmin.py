from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.urls import path

from common.utils.parse_full_name import parse_contacts_name
from crm.forms.admin_forms import ContactForm
from crm.models.contact import Contact
from crm.models.company import Company
from crm.models.deal import Deal
from crm.site.crmmodeladmin import CrmModelAdmin
from crm.utils.admfilters import ByOwnerFilter
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter
from massmail.admin_actions import make_mailing_out
from massmail.admin_actions import specify_vip_recipients


class ContactAdmin(CrmModelAdmin):
    actions = [
        make_mailing_out,
        specify_vip_recipients,
        'export_selected'
    ]
    form = ContactForm
    list_display = [
        'the_full_name',
        'the_email',
        'the_phone',
        'contact_company',
        'newsletters_subscriptions',
        'created',
        'person',
    ]
    list_filter = (
        ByOwnerFilter,
        ('company__industry', ScrollRelatedOnlyFieldListFilter),
        ('company__type', admin.RelatedOnlyFieldListFilter),
    )
    radio_fields = {"sex": admin.HORIZONTAL}
    raw_id_fields = ('city', 'company')
    readonly_fields = [
        'owner',
        'modified_by',
        'creation_date',
        'update_date',
        'tag_list',
        'the_full_name',
        'the_email',
        'contact_company',
        'connections_to_phone',
        'connections_to_other_phone',
        'connections_to_mobile',
        'create_email',
        'unsubscribed'
    ]
    save_on_top = True
    search_fields = [
        'first_name', 'last_name',
        'email', 'secondary_email',
        'description', 'phone',
        'other_phone', 'mobile',
        'city_name',
        'address', 'company__full_name',
        'company__website',
        'company__city_name',
        'company__address',
        'company__email',
        'company__description',
    ]

    # -- ModelAdmin methods -- #

    def change_view(self, request, object_id,
                    form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['emails'] = self.get_latest_emails(
            'contact_id', object_id)
        extra_context['deal_num'] = Deal.objects.filter(
            contact_id=object_id).count()
        extra_context['del_dup_url'] = self.del_dup_url(object_id)
        self.add_remainder_context(
            request, extra_context, object_id,
            ContentType.objects.get_for_model(Contact)
        )
        return super().change_view(
            request, object_id, form_url,
            extra_context=extra_context,
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "company":
            initial = dict(request.GET.items())
            if initial.get('company', None):
                kwargs["queryset"] = Company.objects.filter(
                    id=int(initial['company'])
                )
        return super().formfield_for_foreignkey(
            db_field, request, **kwargs)

    def get_fieldsets(self, request, obj=None):
        return (
            [None if not obj else f'{obj}', {
                'fields': (
                    ('first_name', 'middle_name', 'last_name'),
                    ('title', 'sex'),
                    ('birth_date', 'was_in_touch'),
                    'description',
                    ('disqualified', self.massmail_field_name(obj))
                )
            }],
            *self.get_tag_fieldsets(obj),
            ('Contact details', {
                'fields': (
                    'email',
                    'create_email',
                    'secondary_email',
                    'phone',
                    'connections_to_phone',
                    'other_phone',
                    'connections_to_other_phone',
                    'mobile',
                    'connections_to_mobile',
                    ('lead_source', 'company'),
                    ('city', 'country'),
                    'address'
                )
            }),
            (_('Additional information'), {
                'classes': ('collapse',) if request.user.department_id else (),
                'fields': (
                    ('owner', 'department'),
                    'modified_by',
                    ('creation_date', 'update_date'),
                )
            }),
        )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if request.user.is_superuser:
            if readonly_fields.count('owner'):
                readonly_fields.remove('owner')
        return readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        initial = dict(request.GET.items())
        if initial.get('company', None):
            form.base_fields['company'].initial = Company.objects.get(
                id=int(initial['company'])
            )
        return form

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('make_massmail/',
                 admin.views.decorators.staff_member_required(
                    self.admin_site.admin_view(self.make_massmail)),
                 name='contact_make_massmail'
                 ),
        ]
        return my_urls + urls

    def save_model(self, request, obj, form, change):
        parse_contacts_name(obj)
        obj.owner = obj.company.owner
        obj.department_id = obj.company.department_id
        super().save_model(request, obj, form, change)

    # -- ModelAdmin callables -- #

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">business</i>'
        ),
        ordering='company'
    )
    def contact_company(self, obj):
        return obj.company

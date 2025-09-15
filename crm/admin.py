from django.conf import settings
from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.db.models import F
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from common.models import Department
from common.utils.for_translation import check_for_translation
from common.utils.helpers import LEADERS
from crm.models import Company
from crm.models import City
from crm.models import Contact
from crm.models import ClientType
from crm.models import Country
from crm.models import CrmEmail
from crm.models import Currency
from crm.models import Deal
from crm.models import Industry
from crm.models import Lead
from crm.models import LeadSource
from crm.models import Payment
from crm.models.product import Product
from crm.models.product import ProductCategory
from crm.models import Rate
from crm.models import ClosingReason
from crm.models import Request
from crm.models import Tag
from crm.models import Shipment
from crm.models import Stage
from crm.site import companyadmin
from crm.site import dealadmin
from crm.site import contactadmin
from crm.site import crmemailadmin
from crm.site import leadadmin
from crm.site import requestadmin
from crm.site import productadmin
from crm.site import tagadmin
from crm.site import cityadmin
from crm.site.currencyadmin import CurrencyAdmin
from crm.site.paymentadmin import PaymentAdmin
from crm.site.shipmentadmin import ShipmentAdmin
from crm.site.crmadminsite import crm_site
from crm.utils.admfilters import ByDepartmentFilter

admin.site.empty_value_display = '(None)'


class MyModelAdmin(admin.ModelAdmin):
    list_filter = (ByDepartmentFilter,)

    # -- ModelAdmin methods -- #

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'department':
            kwargs["queryset"] = Group.objects.filter(
                department__isnull=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TranslateNameModelAdmin(MyModelAdmin):

    # -- ModelAdmin methods -- #

    def save_model(self, request, obj, form, change):
        if 'index_number' in form.changed_data:
            # arrange indexes
            objects = self.model.objects.filter(
                index_number__gte=obj.index_number,
                department=obj.department
            )
            objects.update(index_number=F('index_number') + 1)
        super().save_model(request, obj, form, change)
        check_for_translation(request, obj, form)


class CompanyAdmin(companyadmin.CompanyAdmin):
    inlines = []
    raw_id_fields = ('city',)

    # -- ModelAdmin methods -- #

    def get_fieldsets(self, request, obj=None):
        return (
            (None, {
                'fields': (
                    ('full_name', 'disqualified'),
                    ('alternative_names', 'massmail'),
                    ('type', 'lead_source'),
                    'registration_number',
                    'was_in_touch',
                    'description',
                    'industry',
                )
            }),
            (None, {
                'fields': ('tag_list',)
            }),
            (_('Add tags'), {
                'classes': ('collapse',),
                'fields': ('tags',)
            }),
            (_('Contact details'), {
                'fields': (
                    ('email', 'phone'),
                    'website',
                    'city_name',
                    ('city', 'country'),
                    'region', 'district',
                    'address',
                )
            }),
            (_('Additional information'), {
                'classes': ('collapse',),
                'fields': (
                    ('owner', 'modified_by'),
                    'department',
                    'warning',
                    ('creation_date', 'update_date',)
                )
            }),
        )

    # -- ModelAdmin callables -- #

    @admin.display(description=_("Name"), ordering='name')
    def city_name(self, instance):
        if not instance.name:
            instance.name = settings.NO_NAME_STR
        return instance.name


class DealAdmin(dealadmin.DealAdmin):
    list_display = [
        'dynamic_name', 'next_step_name',
        'next_step_date', 'stage', 'owner',
        'relevant', 'active',
        'counterparty', 'creation_date'
    ]
    raw_id_fields = (
        'lead', 'contact', 'company',
        'partner_contact', 'request'
    )

    # -- ModelAdmin methods -- #

    def get_fieldsets(self, request, obj=None):
        return (
            (None, {
                'fields': (
                    'name', ('creation_date', 'closing_date'),
                    ('inquiry', 'translation'),
                    ('relevant', 'active', 'important', 'closing_reason'),
                )
            }),
            (_('Contact info'), {
                # 'classes': ('collapse',),
                'fields': (
                    'contact_person',
                    'company',
                )
            }),
            (' ', {
                'fields': (
                    'stage', ('amount', 'currency'),
                    'next_step', 'next_step_date', 'workflow', 'description',
                    'stages_dates',
                )
            }),
            (None, {
                'fields': ('tag_list',)
            }),
            (_('Add tags'), {
                'classes': ('collapse',),
                'fields': ('tags',)
            }),
            (_('Relations'), {
                'classes': ('collapse',),
                'fields': (
                    'contact', 'company', 'lead',
                    'partner_contact', 'request'
                )
            }),
            (_('Additional information'), {
                'classes': ('collapse',),
                'fields': (
                    ('owner', 'co_owner'),
                    'department', 'update_date',
                    'modified_by',
                    'ticket'
                )
            }),
        )

    def get_readonly_fields(self, request, obj=None):
        return (
            'inquiry', 'company', 'tag_list',
            'deal_messengers', 'translation',
            'contact_person', 'update_date', 'creation_date',
            'dynamic_name', 'counterparty'
        )


class ContactAdmin(contactadmin.ContactAdmin):
    readonly_fields = ['creation_date', 'update_date']

    # -- ModelAdmin methods -- #

    def get_fieldsets(self, request, obj=None):
        return (
            [None, {
                'fields': (
                    ('first_name', 'middle_name', 'last_name'),
                    ('title', 'sex'),
                    ('birth_date', 'was_in_touch'),
                    ('disqualified', 'massmail')
                )
            }],
            (_('Add tags'), {
                'fields': ('tags',)
            }),
            ('Contact details', {
                'fields': (
                    ('email', 'secondary_email'),
                    'phone',
                    ('other_phone', 'mobile'),
                    ('lead_source', 'company'),
                    'region',
                    'district',
                    'address', 'country'
                )
            }),
            (_('Additional information'), {
                'fields': (
                    ('owner', 'department'),
                    'modified_by',
                    ('creation_date', 'update_date'),
                )
            }),
        )


class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class LeadAdmin(leadadmin.LeadAdmin):

    # -- ModelAdmin methods -- #

    def get_fieldsets(self, request, obj=None):
        return (
            (None, {
                'fields': [
                    ('lead_source', 'disqualified', 'massmail'),
                    ('contact', 'company')
                ],
            }),
            (None, {
                'fields': [
                    ('first_name', 'middle_name', 'last_name'),
                    ('title', 'sex'),
                    ('birth_date', 'was_in_touch'),
                    'description'
                ],
            }),
            (None, {
                'fields': ('tag_list',)
            }),
            (_('Add tags'), {
                'classes': ('collapse',),
                'fields': ('tags',)
            }),
            (_('Contact details'), {

                'fields': (
                    ('email', 'secondary_email'),
                    ('phone', 'other_phone'),
                    ('company_name', 'website'),
                    ('company_email', 'country'),
                    'region', 'district',
                    'address',
                )
            }),
            (_('Additional information'), {
                'classes': ('collapse',),
                'fields': (
                    ('owner', 'modified_by'),
                    'department',
                    ('creation_date', 'update_date'),
                )
            }),
        )


class CrmEmailAdmin(admin.ModelAdmin):
    empty_value_display = LEADERS
    raw_id_fields = (
        'deal',
        'contact',
        'company',
        'request',
        'lead'
    )
    save_on_top = True


class RequestAdmin(requestadmin.RequestAdmin):
    raw_id_fields = (
        'lead',
        'contact',
        'deal',
        'company'
    )
    readonly_fields = tuple()

    def get_fieldsets(self, request, obj=None):
        return (
            (None, {
                'fields': [
                    'request_for',
                    'duplicate',
                    'case',
                    'pending',
                    'subsequent',
                    ('lead_source', 'receipt_date'),
                    ('department', 'owner', 'co_owner'),
                    ('first_name', 'middle_name', 'last_name'),
                    ('email', 'phone'),
                    'website',
                    'company_name',
                    ('country', 'city_name'),
                    ('description', 'translation'),
                    'remark',
                    'products'
                ]
            }),
            (_('Relations'), {
                'fields': [
                    'verification_required',
                    'contact',
                    'company',
                    'lead',
                    'deal',
                ]
            }),
            (_('Additional information'), {
                'classes': ('collapse',),
                'fields': [
                    'subsequent',
                    ('modified_by', 'ticket')
                ]
            }),
        )


class StageAdmin(TranslateNameModelAdmin):
    list_display = (
        'name', 'default',
        'second_default',
        'success_stage',
        'conditional_success_stage',
        'goods_shipped', 'department',
        'index_number', 'id'
    )
    list_filter = (
        ByDepartmentFilter,
        'default',
        'success_stage',
        'conditional_success_stage',
        'goods_shipped',
    )
    readonly_fields = ('id',)


class ClientTypeAdmin(TranslateNameModelAdmin):
    list_display = ('name', 'id', 'department')


class IndustryAdmin(TranslateNameModelAdmin):
    list_display = ('name', 'id', 'department')


class ProductAdmin(productadmin.ProductAdmin):
    list_display = ('name', 'price', 'currency', 'department')

    # -- ModelAdmin methods -- #

    def get_fieldsets(self, request, obj=None):
        fieldsets = self.fieldsets
        fls = fieldsets[1][1]['fields']
        if not fls.count('department'):
            fls.extend(['department'])
        return fieldsets


class ProductCategoryAdmin(TranslateNameModelAdmin):
    fieldsets = (
        (None, {
            'fields': [
                'name',
                'department',
                'description',
                'creation_date'
            ]
        }),
    )
    list_display = ('name', 'id', 'department')
    readonly_fields = ('creation_date',)


class ClosingReasonAdmin(TranslateNameModelAdmin):
    list_display = ('name', 'id', 'department',
                    'index_number', 'success_reason')


class LeadSourceAdmin(TranslateNameModelAdmin):
    list_display = ('name', 'website_email',
                    'department', 'id')
    raw_id_fields = ('department',)
    readonly_fields = ('website_email',)
    search_fields = ('name', 'email', 'uuid')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'department':
            kwargs["queryset"] = Department.objects.all()
        return BaseModelAdmin.formfield_for_foreignkey(self, db_field, request, **kwargs)

    # -- ModelAdmin Callables -- #

    @admin.display(
        description="Email on website",
        ordering='email'
    )
    def website_email(self, obj):
        return obj.email


class RateAdmin(admin.ModelAdmin):
    list_display = (
        'currency', 'payment_date',
        'rate_to_state_currency',
        'rate_to_marketing_currency',
        'rate_type'
    )
    readonly_fields = ('payment_date',)


admin.site.register(City, cityadmin.CityAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(ClientType, ClientTypeAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(CrmEmail, CrmEmailAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Deal, DealAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(LeadSource, LeadSourceAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ClosingReason, ClosingReasonAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(Shipment, ShipmentAdmin)
admin.site.register(Stage, StageAdmin)
admin.site.register(Tag, tagadmin.TagAdmin)

crm_site.register(City, cityadmin.CityAdmin)
crm_site.register(Company, companyadmin.CompanyAdmin)
crm_site.register(Contact, contactadmin.ContactAdmin)
crm_site.register(CrmEmail, crmemailadmin.CrmEmailAdmin)
crm_site.register(Currency, CurrencyAdmin)
crm_site.register(Deal, dealadmin.DealAdmin)
crm_site.register(Lead, leadadmin.LeadAdmin)
crm_site.register(Payment, PaymentAdmin)
crm_site.register(Product, productadmin.ProductAdmin)
crm_site.register(Request, requestadmin.RequestAdmin)
crm_site.register(Shipment, ShipmentAdmin)
crm_site.register(Tag, tagadmin.TagAdmin)

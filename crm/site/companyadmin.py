from django.contrib import admin
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import path
from django.urls import reverse

from crm.forms.admin_forms import CompanyForm
from crm.models import Company
from crm.models import Contact
from crm.models import Deal
from crm.utils.change_massconts import change_massconts
from crm.utils.check_city import check_city
from crm.site.crmmodeladmin import CrmModelAdmin
from crm.site.crmstackedinline import CrmStackedInline
from crm.utils.admfilters import ByOwnerFilter
from crm.utils.admfilters import HasContactsFilter
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter
from massmail.admin_actions import make_mailing_out
from massmail.admin_actions import remove_vip_status
from massmail.admin_actions import specify_vip_recipients
from common.admin import FileInline

you_can_view_warning = _(
    'Attention! You can only view companies associated with your department.')


class ContactInline(CrmStackedInline):
    fieldsets = [
        (None, {
            'fields': (
                ('first_name', 'last_name'),
                ('title', 'phone'),
                ('email', 'secondary_email'),
                ('country', 'lead_source'),
            )
        }),
    ]
    model = Contact
    show_change_link = True
    view_on_site = False


class CompanyAdmin(CrmModelAdmin):
    form = CompanyForm
    list_display = [
        'company',
        'type',
        'created',
        'person',
        'newsletters_subscriptions',
        'id',
        'registration_number'
    ]
    list_filter = [
        HasContactsFilter,
        ByOwnerFilter,
        'update_date',
        ('industry', ScrollRelatedOnlyFieldListFilter),
        ('type', admin.RelatedOnlyFieldListFilter),
    ]    
    readonly_fields = (
        'modified_by',
        'creation_date',
        'update_date',
        'view_website_button',
        'warning',
        'tag_list',
        'company',
        'connections_to_phone'
    )
    actions = [
        make_mailing_out,
        specify_vip_recipients,
        remove_vip_status,
        'export_selected',
        'change_owner'
    ]
    search_fields = [
        'full_name', 'website',
        'phone', 'city_name',
        'address', 'email',
        'description',
        'registration_number',
        'alternative_names'
    ]
    filter_horizontal = ('industry',)
    inlines = [FileInline, ContactInline]
    raw_id_fields = ('city',)

    # -- ModelAdmin Methods -- #

    def change_view(self, request, object_id,
                    form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['contact_num'] = Contact.objects.filter(
            company_id=object_id).count()
        extra_context['deal_num'] = Deal.objects.filter(
            company_id=object_id).count()
        extra_context['emails'] = self.get_latest_emails(
            'company_id', object_id)
        extra_context['del_dup_url'] = self.del_dup_url(request, object_id)
        self.add_remainder_context(
            request, extra_context, object_id,
            ContentType.objects.get_for_model(Company)
        )
        return super().change_view(
            request, object_id, form_url,
            extra_context=extra_context,
        )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'change_owner' in actions:
                del actions['change_owner']
        return actions

    def get_fieldsets(self, request, obj=None):
        return [
            (None, {
                'fields': (
                    ('full_name', 'disqualified'),
                    ('alternative_names', 
                     self.massmail_field_name(obj)),
                    ('type', 'lead_source'),
                    'registration_number',
                    'was_in_touch',
                    'description',
                    'industry',
                )
            }),
            *self.get_tag_fieldsets(obj),
            (_('Contact details'), {
                'fields': (
                    'email', 'phone',
                    'connections_to_phone',
                    'website', 'view_website_button',
                    ('city', 'country'),
                    'region', 'district',
                    'address',
                )
            }),
            (_('Additional information'), {
                'classes': ('collapse',) if request.user.department_id else (),
                'fields': (
                    ('owner', 'department'),
                    'warning', 'modified_by',
                    ('creation_date', 'update_date',)
                )
            }),
        ]

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = self.model.objects.all()
            if any((request.user.is_manager, request.user.is_operator)):
                messages.warning(
                    request,
                    you_can_view_warning
                )
        return super().get_search_results(
            request, queryset, search_term
        )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if instance.__class__ == Contact:
                instance.owner = instance.company.owner
                instance.department_id = instance.company.department_id
            instance.save()

    def save_model(self, request, obj, form, change):
        if change:
            if 'owner' in form.changed_data:
                obj.contacts.update(
                    owner=obj.owner,
                    department=obj.department
                )
                change_massconts(obj)
            if 'department' in form.changed_data and 'owner' not in form.changed_data:
                obj.contacts.update(department=obj.department)        
        check_city(obj, form)

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        if 'country' in form.changed_data:
            obj.deals.update(country=obj.country)
            obj.requests.update(country=obj.country)
        if 'city' in form.changed_data:
            obj.deals.update(city=obj.city)
            obj.requests.update(city=obj.city)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('make_massmail/',
                 admin.views.decorators.staff_member_required(
                     self.admin_site.admin_view(self.make_massmail)),
                 name='company_make_massmail'
                 ),
        ]
        return my_urls + urls

    # -- ModelAdmin callables -- #

    @admin.display(description=_('Warning:'))
    def warning(self, obj):        # NOQA
        txt = _('Owner will also be changed for contact persons.')
        return mark_safe(f'<span style="color: var(--green-fg)">{txt}</span>')

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">business</i>'
        ),
        ordering='full_name'
    )
    def company(self, obj):
        return obj.full_name

    # -- ModelAdmin actions -- #

    @admin.display(description=_("Change owner of selected Companies"))
    def change_owner(self, request, queryset):
        selected = queryset.values_list('pk', flat=True)
        url = request.get_full_path()
        ids = ','.join(str(pk) for pk in selected)
        return HttpResponseRedirect(
            reverse('change_owner_companies') + f'?next={url}&ids={ids}'
        )

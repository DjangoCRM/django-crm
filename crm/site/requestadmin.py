import threading
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.forms.widgets import HiddenInput
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse

from common.admin import FileInline
from common.models import Department
from common.utils.copy_files import copy_files
from common.utils.helpers import CONTENT_COPY_ICON
from common.utils.helpers import CONTENT_COPY_LINK
from common.utils.helpers import COPY_STR
from common.utils.helpers import get_delta_date
from common.utils.helpers import LEADERS
from common.utils.helpers import get_formatted_short_date
from common.utils.helpers import get_department_id
from common.utils.notify_user import notify_user
from common.utils.parse_full_name import parse_contacts_name
from crm.forms.admin_forms import RequestForm
from crm.models import Currency
from crm.models import CrmEmail
from crm.models import Deal
from crm.models import Output
from crm.models import Request
from crm.models import Stage
from crm.settings import FIRST_STEP
from crm.site.crmmodeladmin import CrmModelAdmin
from crm.site.dealadmin import add_shopping_cart_icon
from crm.utils.check_city import check_city
from crm.utils.admfilters import ByOwnerFilter
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter
from crm.utils.helpers import get_counterparty_header

ATTR_LIST = (
    'lead',
    'deal',
)
COPIED_FIELDS = (
    'request_for',
    'first_name',
    'middle_name',
    'last_name',
    'email',
    'phone',
    'website',
    'lead_source',
    'company_name',
    'lead',
    'contact',
    'company',
    'country',
    'city',
    'city_name',
    'description',
    'translation',
    'remark',
    'subsequent',
    'department',
    'owner',
    'co_owner',
    'verification_required'
)
client_loyalty_title = _("Client Loyalty")
CONTACT_ATTR_LIST = (
    'first_name',
    'last_name',
    'email',
    'phone'
)
country_not_specified = _("Country not specified in request")
DEAL_OWNER_NOTICE = _("You received the deal")
DEAL_CO_OWNER_NOTICE = _("You are the co-owner of the deal")
LEAD_ATTR_LIST = CONTACT_ATTR_LIST + ('country', 'company_name')
table_loyalty_icon = '<i title="{}" class="material-icons" ' \
                     'style="color: var(--body-quiet-color)">loyalty</i>'.format(
                         client_loyalty_title)
loyalty_icon = '<i title="{}" class="material-icons" style="font-size: 17px;color: var(--green-fg)">loyalty</i>'
primary_icon = '<i title="{}" class="material-icons" style="font-size: 17px;color: #ECBA82">local_offer</i>'
primary_title = _("Primary request")
REQUEST_CO_OWNER_NOTICE = _("You are the co-owner of the request")
REQUEST_OWNER_NOTICE = _("You received the request")
pending_str = _('pending')
processed_str = _('processed')
status_str = _('Status')
subject_safe_icon = mark_safe(
    '<i class="material-icons" style="color: var(--body-quiet-color)">subject</i>'
)
subsequent_title = _("Subsequent request")
today_safe_icon = mark_safe(
    '<i class="material-icons" style="color: var(--body-quiet-color)">today</i>'
)

_thread_local = threading.local()


class RequestAdmin(CrmModelAdmin):
    empty_value_display = ''
    fieldsets = [
        (None, {
            'fields': [
                'request_for',
                'duplicate',
                'case',
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
    ]
    filter_horizontal = ('products',)
    form = RequestForm
    inlines = [FileInline]
    list_filter = [
        'pending', ByOwnerFilter, 'receipt_date',
        ('products', ScrollRelatedOnlyFieldListFilter),
        'subsequent'
    ]
    list_per_page = 30
    raw_id_fields = ('lead', 'contact', 'company', 'deal')
    readonly_fields = (
        'subsequent', 'ticket',
        'modified_by', 'person',
        'request_subject', 'the_full_name',
        'the_receipt_date', 'counterparty',
        'the_city', 'loyalty', 'request_counter',
        'content_copy', 'mark_no_products'
    )
    search_fields = [
        'request_for', 'first_name',
        'last_name', 'email',
        'company_name', 'description',
        'translation', 'phone', 'ticket'
    ]

    # -- ModelAdmin Methods -- #

    def change_view(self, request, object_id,
                    form_url='', extra_context=None):
        url = self.get_url_if_no_object(request, object_id)
        if url:
            return HttpResponseRedirect(url)

        extra_context = extra_context or {}
        extra_context['emails'] = self.get_latest_emails(
            'request_id', object_id
        )
        extra_context['has_change_deal_perm'] = request.user.has_perm(
            'crm.change_deal'
        )
        url = reverse("site:crm_request_add") + f"?copy_request={object_id}"
        extra_context['content_copy_link'] = mark_safe(
            CONTENT_COPY_LINK.format(url, COPY_STR, CONTENT_COPY_ICON))
        check_for_counterparty_assignment(request, object_id)
        return super().change_view(
            request, object_id, form_url,
            extra_context=extra_context,
        )

    def changelist_view(self, request, extra_context=None):
        self.add_request_url = reverse("site:crm_request_add")
        return super().changelist_view(
            request, extra_context=extra_context,
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if obj and getattr(obj, "deal", None):
            if "duplicate" in form.base_fields:
                form.base_fields["duplicate"].widget = HiddenInput()
            if "case" in form.base_fields:
                form.base_fields["case"].widget = HiddenInput()

        if request.method == "POST" and '_create-deal' in request.POST:
            department_id = request.user.department_id
            works_globally = Department.objects.get(
                id=department_id
            ).works_globally
            if works_globally:
                form.country_must_be_specified = True

        return form

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        request_id = request.GET.get('copy_request')
        if request_id:
            inquiry = Request.objects.get(id=request_id)
            for f in COPIED_FIELDS:
                initial[f] = getattr(inquiry, f)
            initial['products'] = inquiry.products.all()
        return initial

    def get_list_display(self, request):
        list_display = [
            'request_subject',
            'loyalty',
            'mark_no_products',
            'counterparty',
        ]
        if not any(('company' in request.GET, 'lead' in request.GET)):
            list_display.append('request_counter')
        list_display.extend(('the_full_name', 'the_receipt_date'))
        if not (request.user.is_manager and 'owner' not in request.GET) \
                or request.user.is_chief:
            list_display.append('person')
        list_display.append('status')
        list_display.append('content_copy')
        self.list_display = list_display
        return super().get_list_display(request)

    def response_post_save_change(self, request, obj):
        if '_view_print_version' in request.POST:
            return HttpResponseRedirect(
                reverse('print_request', args=(obj.pk,))
            )
        return super().response_post_save_change(request, obj)

    def save_model(self, request, obj, form, change):
        company = None
        parse_contacts_name(obj)
        if not change:
            self.set_owner(request, obj)
            if request.user.is_manager:
                obj.subsequent = True

        if any((
            '_create-deal' in request.POST or 'duplicate' in form.changed_data and obj.duplicate,
            '_close-case' in request.POST)):
            obj.pending = False
        elif '_activate-case' in request.POST:
            obj.pending = True
        if not obj.pending:
            if not obj.owner:
                obj.owner = request.user
            if not any((obj.contact, obj.lead)):
                obj.get_or_create_contact_or_lead()
            if obj.company:
                company = obj.company
            else:
                if obj.contact:
                    company = obj.contact.company
                    obj.company = company

            if company:
                if not obj.company_name:
                    obj.company_name = company.full_name
                if not obj.country:
                    obj.country = company.country
                if not obj.city:
                    obj.city = company.city
        else:
            if not any((obj.contact, obj.lead)):
                obj.find_contact_or_lead()
            if obj.contact:
                obj.company_id = obj.contact.company_id
            if not obj.company:
                obj.find_company()

        if 'owner' in form.changed_data and obj.deal:
            _notify_deal_owners(request, obj)
        if 'contact' in form.changed_data and obj.contact:
            copy_attrs(obj, 'contact', CONTACT_ATTR_LIST)
            if obj.contact.company:
                if not obj.company_name:
                    obj.company_name = obj.contact.company.full_name
                if not obj.country:
                    obj.country = obj.contact.company.country
                if not obj.website:
                    obj.website = obj.contact.company.website
        elif 'lead' in form.changed_data and obj.lead:
            copy_attrs(obj, 'lead', LEAD_ATTR_LIST)

        check_city(obj, form)

        super().save_model(request, obj, form, change)

        if not obj.products.exists():
            messages.warning(request, _("Specify products"))

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        if not change and request.user.is_manager \
                or obj.pending and 'owner' in form.changed_data:
            notify_request_owners(obj)

        if not obj.pending:
            _update_request_email(obj)

            if not obj.country and obj.department.department.works_globally:
                link = f'<a href="{obj.get_absolute_url()}">{obj.request_for}.</a>'
                messages.warning(
                    request, mark_safe(f'{country_not_specified}: "{link}"')
                )
        attrs = []
        if 'department' in form.changed_data:
            attrs.append('department')
        if 'owner' in form.changed_data:
            if 'managers' in obj.owner.groups.values_list('name', flat=True):
                attrs.append('owner')
        if attrs:
            _change_related_objs_attrs(obj, attrs)

        if '_create-deal' in request.POST:
            if not any((obj.pending, obj.deal, obj.duplicate, obj.case)):
                update_fields = ['deal']
                d = _get_or_create_deal(obj, request)
                obj.deal = d
                if obj.contact and not obj.company:
                    obj.company = obj.contact.company
                    update_fields.append('company')
                obj.save(update_fields=update_fields)
                CrmEmail.objects.filter(
                    ticket=obj.ticket, deal__isnull=True
                ).update(deal=d)
                if obj.deal:
                    _notify_deal_owners(request, obj)

        if 'contact' in form.changed_data and obj.contact and obj.deal:
            _update_deal_attr(obj, 'contact')
        if 'lead' in form.changed_data and obj.lead and obj.deal:
            _update_deal_attr(obj, 'lead')
        if 'company' in form.changed_data and obj.company and obj.deal:
            _update_deal_attr(obj, 'company')

    # -- ModelAdmin callables -- #

    @admin.display(description='')
    def content_copy(self, obj):
        url = self.add_request_url + f"?copy_request={obj.id}"
        return mark_safe(
            CONTENT_COPY_LINK.format(url, COPY_STR, CONTENT_COPY_ICON)
        )

    @admin.display(description=get_counterparty_header())
    def counterparty(self, obj):
        counterparty = obj.lead if obj.lead else obj.company
        if counterparty:
            url = counterparty.get_crm_url()
            return mark_safe(
                f'<a href="{url}">{counterparty.full_name}</a>'
            )
        return obj.company_name

    @staticmethod
    @admin.display(description=mark_safe(
        table_loyalty_icon))
    def loyalty(obj):
        if obj.subsequent:
            return mark_safe(
                loyalty_icon.format(subsequent_title)
            )
        return mark_safe(
            primary_icon.format(primary_title)
        )

    @staticmethod
    @admin.display(description='')
    def mark_no_products(obj):
        if not obj.products.exists():
            return mark_safe(add_shopping_cart_icon)
        return ''

    @staticmethod
    @admin.display(description='')
    def request_counter(obj):
        counter = counterparty = None
        if obj.company:
            counterparty = obj.company
            counter = Request.objects.filter(company=obj.company).count()
        elif obj.lead:
            counterparty = obj.lead
            counter = Request.objects.filter(lead=obj.lead).count()
        if counter:
            obj_plural_name = obj._meta.verbose_name_plural     # NOQA
            if counter > 1:
                if hasattr(_thread_local, 'request_changelist_url'):
                    url = _thread_local.request_changelist_url
                else:
                    url = reverse("site:crm_request_changelist")
                    _thread_local.request_changelist_url = url
                url += f"?{counterparty._meta.model_name}={counterparty.id}"  # NOQA
                link = f'<a href="{url}" title="{obj_plural_name}">({counter})</a>'
                return mark_safe(link)
            elif counter == 1:
                return mark_safe(f'<span title="{obj_plural_name}">(1)</span>')
        # to avoid showing dashes if there is no counter
        return mark_safe('&nbsp;')

    @admin.display(
        description=subject_safe_icon,
        ordering='request_for'
    )
    def request_subject(self, obj):
        if not obj.request_for:
            obj.request_for = LEADERS
        if obj.duplicate:
            duplicate = obj._meta.get_field('duplicate').verbose_name  # NOQA
            return mark_safe(
                f'<span style="color: var(--body-quiet-color)">({duplicate}) {obj.request_for}</span>'
            )
        if obj.case:
            case = obj._meta.get_field('case').verbose_name
            if obj.pending:
                return mark_safe(
                    f'<span style="color: var(--green-fg)">({case}) {obj.request_for}</span>'
                )
            else:
                return mark_safe(
                    f'<span style="color: var(--body-quiet-color)">({case}) {obj.request_for}</span>'
                )
        return obj.request_for

    @admin.display(description=status_str)
    def status(self, obj):
        if obj.pending:
            return mark_safe(
                f'<i class="material-icons" title="{status_str}: {pending_str}"'
                ' style="font-size: 17px; color: var(--error-fg)">assignment_late</i>'
            )
        else:
            return mark_safe(
                f'<i class="material-icons" title="{status_str}: {processed_str}"'
                ' style="font-size: 17px; color: var(--green-fg)">assignment_turned_in</i>'
            )

    @admin.display(
        description=today_safe_icon,
        ordering='receipt_date'
    )
    def the_receipt_date(self, instance):
        return instance.receipt_date


# -- Custom methods -- #

def check_for_counterparty_assignment(request: WSGIRequest, object_id: int) -> None:
    """
    Check if a counterparty is assigned to a request object and add a warning message
    in case counterparty and request owners are different
    or add an information message if a request owner is not assigned yet
    """
    if object_id:
        data = Request.objects.values_list(
            "owner",
            "contact__owner",
            "company__owner",
            "lead__owner",
        ).get(id=object_id)
        owner_id = data[0]
        counterparty_assigned_to = data[1] or data[2] or data[3]
        if counterparty_assigned_to:
            tag = None
            if not owner_id:
                tag = messages.INFO
            elif owner_id != counterparty_assigned_to:
                tag = messages.WARNING
            if tag:
                username = get_user_model().objects.get(id=counterparty_assigned_to).username
                msg = _("Found the counterparty assigned to")
                messages.add_message(
                    request,
                    tag,
                    f"{msg} {username}"
                )


def copy_attrs(obj: Request, attr: str, attr_list) -> None:
    for a in attr_list:
        if not getattr(obj, a, None):
            setattr(
                obj, a, getattr(getattr(obj, attr), a, None)
            )


def _change_related_objs_attrs(obj: Request, attrs: list) -> None:
    for field in ('lead', 'deal', 'contact'):
        fk_obj = getattr(obj, field)
        if fk_obj:
            for attr in attrs:
                setattr(fk_obj, attr, getattr(obj, attr))
            fk_obj.save(update_fields=[*attrs])
            if field == 'contact':
                company = fk_obj.company
                for attr in attrs:
                    setattr(company, attr, getattr(obj, attr))
                company.save(update_fields=[*attrs])
    emails = CrmEmail.objects.filter(
        request=obj,
        incoming=True,
        inquiry=True
    )
    pairs = [(attr, getattr(obj, attr)) for attr in attrs]
    kwargs = dict(pairs)
    emails.update(**kwargs)


def _get_or_create_deal(obj: Request, request: WSGIRequest) -> Deal:
    try:
        deal = Deal.objects.get(
            request=obj,
            ticket=obj.ticket
        )
    except Deal.DoesNotExist:
        date = get_formatted_short_date()
        msg = _('Request')
        department_id = get_department_id(obj.owner)
        stage = Stage.objects.filter(
            department_id=department_id,
            default=True
        ).first()
        deal = Deal(
            name=obj.request_for,
            request=obj,
            department_id=department_id,
            ticket=obj.ticket,
            description=obj.remark,
            next_step=FIRST_STEP,
            next_step_date=get_delta_date(1),
            stage=stage,
            owner=obj.owner,
            co_owner=obj.co_owner,
            stages_dates=f'{date} - {stage}\n',
            workflow=f'{date} - {msg}\n'
        )
        if request.user.department_id:  # NOQA
            deal.currency_id = Department.objects.get(
                id=request.user.department_id  # NOQA
            ).default_currency_id
        else:
            deal.currency_id = Currency.objects.get(
                is_state_currency=True
            ).id
        if obj.contact:
            deal.contact = obj.contact
            deal.company = obj.contact.company
            if deal.company:
                deal.country = deal.company.country
                deal.city = deal.company.city
        else:
            deal.lead = obj.lead
            if deal.lead:
                deal.country = deal.lead.country
                deal.city = deal.lead.city
        deal.save()
        copy_files(obj, deal)
        for product in obj.products.all():
            Output.objects.create(
                deal=deal,
                product=product,
                quantity=1
            )

        deal_url = deal.get_absolute_url()
        msg_dict = {
            "name": deal._meta.verbose_name,
            "obj": format_html('<a href="{}">{}</a>', deal_url, deal),
        }
        msg = _("The {name} “{obj}” was added successfully.")
        messages.success(
            request, format_html(msg, **msg_dict)
        )
    return deal


def _notify_deal_owners(request: WSGIRequest, obj: Request) -> None:
    deal = obj.deal
    if request.user != deal.owner:
        notify_user(deal, deal.owner, DEAL_OWNER_NOTICE,
                    DEAL_OWNER_NOTICE, request=request)
    if deal.co_owner and request.user != deal.co_owner:
        notify_user(deal, deal.co_owner, DEAL_CO_OWNER_NOTICE,
                    DEAL_CO_OWNER_NOTICE, request=request)


def notify_request_owners(obj: Request) -> None:
    notify_user(obj, obj.owner, REQUEST_OWNER_NOTICE)
    if obj.co_owner:
        notify_user(obj, obj.co_owner, REQUEST_CO_OWNER_NOTICE)


def _update_deal_attr(obj: Request, attr: str) -> None:
    setattr(obj.deal, attr, getattr(obj, attr))
    obj.deal.save(update_fields=[attr])


def _update_request_email(obj: Request) -> None:
    try:
        save_request_email = False
        request_email = CrmEmail.objects.get(
            request=obj,
            incoming=True,
            trash=False,
            inquiry=True
        )
        if request_email.owner != obj.owner:
            request_email.owner = obj.owner
            save_request_email = True
        if not request_email.deal:
            request_email.contact = obj.contact
            request_email.deal = obj.deal
            request_email.lead = obj.lead
            save_request_email = True
        if save_request_email:
            request_email.save(
                update_fields=['owner', 'deal', 'lead']
            )
    except CrmEmail.DoesNotExist:
        pass

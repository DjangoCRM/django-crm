import threading
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models import Sum
from django.db.models import Exists
from django.db.models import F
from django.http import HttpResponseRedirect
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.urls import reverse

from chat.models import ChatMessage
from common.admin import FileInline
from common.models import Department
from common.utils.helpers import add_chat_context
from common.utils.helpers import get_now
from common.utils.helpers import LEADERS
from common.utils.helpers import get_today
from common.utils.helpers import popup_window
from common.utils.remind_me import remind_me
from crm.forms.admin_forms import DealForm
from crm.models import ClosingReason
from crm.models import CrmEmail
from crm.models import Deal
from crm.models import Output
from crm.models import Payment
from crm.models import Stage
from crm.site.crmmodeladmin import CrmModelAdmin
from crm.site.outputinline import OutputInline
from crm.site.paymentadmin import set_currency_initial
from crm.site.paymentinline import PaymentInline
from crm.utils.admfilters import ByChangedByChiefs
from crm.utils.admfilters import ByOwnerFilter
from crm.utils.admfilters import ByProductFilter
from crm.utils.admfilters import ByPartnerFilter
from crm.utils.admfilters import ImportantFilter
from crm.utils.admfilters import IsActiveFilter
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter
from crm.utils.clarify_permission import clarify_permission
from crm.utils.helpers import get_counterparty_header
from tasks.models import Memo

closing_date_str = _("Closing date")
closing_date_safe_icon = mark_safe(
    f'<i class="material-icons" title="{closing_date_str}" '
    f'style="color: var(--body-quiet-color)">event_busy</i>'
)
icon_str = '<i class="material-icons" style="color: var(--body-quiet-color)">{}</i>'
contact_tip = _("View Contact in new tab")
company_tip = _("View Company in new tab")
company_safe_icon = mark_safe(icon_str.format('domain'))
deal_counter_icon = '<span title="{}">({})</span>'
deal_counter_title = _("Deal counter")
lead_tip = _("View Lead in new tab")
unanswered_email_str = _('Unanswered email')
mail_outline_small_icon = f'<i class="material-icons" title="{unanswered_email_str}" ' \
                          f'style="font-size:small;color: var(--body-quiet-color)">mail_outline</i>'
mail_outline_safe_icon = mark_safe(icon_str.format('mail_outline'))
unread_chat_message_str = _('Unread chat message')
message_icon = f'<i class="material-icons" title="{unread_chat_message_str}" ' \
               f'style="font-size:small;color: var(--error-fg)">message</i>'
payment_received_str = _('Payment received')
payment_received_icon = f'<i class="material-icons" title="{payment_received_str}" ' \
                        f'style="font-size:small;color:green">payments</i>'
specify_shipment_str = _('Specify the date of shipment')
local_shipping_icon = f'<i class="material-icons" title="{specify_shipment_str}" ' \
                      f'style="font-size:small;color: var(--body-quiet-color)">local_shipping</i>'
specify_products_str = _('Specify products')
add_shopping_cart_icon = f'<i class="material-icons" title="{specify_products_str}" ' \
                         f'style="font-size:small;color: var(--error-fg)">add_shopping_cart</i>'
expired_shipment_date_str = _('Expired shipment date')
expired_local_shipping_icon = f'<i class="material-icons" title="{expired_shipment_date_str}" ' \
                              f'style="font-size:small;color: var(--error-fg)">local_shipping</i>'
perm_phone_msg_safe_icon = mark_safe(icon_str.format('perm_phone_msg'))
person_outline_safe_icon = mark_safe(icon_str.format('person_outline'))
textarea_tag = '<textarea name="description" cols="80" rows="5" class="vLargeTextField">{}</textarea>'
subject_icon = '<i title="{}" class="material-icons" style="color: var(--body-quiet-color)">subject</i>'
relevant_deal_str = _('Relevant deal')

_thread_local = threading.local()


class DealAdmin(CrmModelAdmin):
    actions = ['export_selected']
    form = DealForm
    inlines = [OutputInline, PaymentInline, FileInline]
    list_filter = (
        ImportantFilter,
        IsActiveFilter, ByOwnerFilter,
        # TagFilter,
        ByProductFilter,
        ByPartnerFilter,
        ByChangedByChiefs,
        'relevant', 'creation_date',
        ('stage', ScrollRelatedOnlyFieldListFilter),
        ('closing_reason', ScrollRelatedOnlyFieldListFilter),
        ('company__industry', ScrollRelatedOnlyFieldListFilter),
        # 'update_date'
    )
    list_per_page = 50
    raw_id_fields = (
        'lead',
        'contact',
        'company',
        'partner_contact',
        'request'
    )
    search_fields = [
        'name', 'next_step', 'description',
        'ticket', 'contact__first_name',
        'contact__last_name', 'contact__email',
        'contact__address', 'contact__description',
        'company__full_name', 'company__website',
        'company__city_name', 'company__country__name',
        'company__address', 'company__email',
        'company__description',
        'partner_contact__company__full_name',
        'lead__first_name', 'lead__last_name', 'lead__address',
        'lead__description', 'lead__company_name', 'lead__website',
        'lead__company_address',
        'lead__company_email',
    ]

    # -- ModelAdmin methods -- #

    def _create_formsets(self, request, obj, change):
        formsets, inline_instances = super()._create_formsets(request, obj, change)
        p = Payment.objects.filter(deal=obj).last()
        if p:
            # change initial data for an empty inline form of payment
            d = formsets[1].empty_form.base_fields
            d['amount'].initial = p.amount
            d['contract_number'].initial = p.contract_number
            d['invoice_number'].initial = p.invoice_number
            d['order_number'].initial = p.order_number
            if settings.MARK_PAYMENTS_THROUGH_REP:
                d['through_representation'].initial = p.through_representation
        return formsets, inline_instances

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['emails'] = self.get_latest_emails('deal_id', object_id)
        try:
            obj = Deal.objects.get(id=object_id)
        except Deal.DoesNotExist:
            messages.error(
                request,
                _(
                    "Deal with ID '{}' does not exist. Perhaps it was deleted?"
                ).format(object_id)
            )
            return HttpResponseRedirect(reverse("site:crm_deal_changelist"))
        extra_context['deal_num'] = Deal.objects.filter(
            company_id=obj.company_id
        ).count()
        extra_context['memo_num'] = Memo.objects.filter(
            deal_id=object_id
        ).count()
        content_type = ContentType.objects.get_for_model(Deal)
        add_chat_context(
            request, extra_context, object_id, content_type
        )
        self.add_remainder_context(
            request, extra_context, object_id, content_type
        )
        if settings.USE_I18N:
            for inline in self.inlines:
                inline.verbose_name_plural = mark_safe(
                    f'{inline.icon} {inline.model._meta.verbose_name_plural}'  # NOQA
                )
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        next_url = request.get_full_path()
        url = reverse("toggle_default_sorting")
        extra_context['toggle_sorting_url'] = f"{url}?model=Deal&next_url={next_url}"
        url = reverse("site:crm_request_add")
        extra_context['request_add_url'] = url
        has_add_permission = request.user.has_perm('crm.add_request')
        extra_context['has_add_request_permission'] = has_add_permission

        func = getattr(self.__class__, 'dynamic_name')
        title = gettext(
            self.model._meta.get_field("name").help_text._args[0]  # NOQA
        )
        func.short_description = mark_safe(
            f'<i title="{title}" class="material-icons" style="color: var(--body-quiet-color)">subject</i>'
        )
        _thread_local.department_id = {}
        return super().changelist_view(request, extra_context)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "stage":
            kwargs["empty_label"] = None
            if db_field.name == 'currency':
                set_currency_initial(request, kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_fieldsets(self, request, obj=None):
        inquiry = None
        contact_fields = []
        if obj:
            if obj.request:
                inquiry = obj.request
                inquiry_url = reverse(
                    'site:crm_request_change',
                    args=(obj.request.id,)
                )
                title = _('View the Request')
                func = getattr(self.__class__, 'inquiry')
                func.short_description = mark_safe(
                    f'<ul class="object-tools" style="margin-left: -40px;margin-top: 0px;">'
                    f'<li><a title="{title}" href="{inquiry_url}" target="_blank">'
                    f'{_("Request")}'
                    f' </a></li></ul>'
                )
            person = obj.contact or obj.lead
            for attr in ('phone', 'other_phone', 'mobile'):
                if getattr(person, attr, None):
                    contact_fields.append('connections_to_' + attr)

        fields = ['name']
        if inquiry:
            if inquiry.translation:
                fields.append(('inquiry', 'translation'))
            else:
                fields.append('inquiry')
        fields.extend([
            ('relevant', 'important', 'created'),
            ('closing_reason', 'closed')
        ])

        return (
            (None, {'fields': fields}),
            (_('Contact info'), {
                'fields': (
                    'contact_person', 'create_email',
                    *contact_fields, 'deal_messengers',
                    'view_website_button', 'view_company',
                )
            }),
            (' ', {
                'fields': (
                    'stage',
                    ('amount', 'currency'),
                    ('paid', 'expected'),
                    'next_step', ('next_step_date', 'remind_me'),
                    'workflow_area', 'description',
                    'stages_dates',
                )
            }),
            (' ', {
                'fields': ('tag_list',)
            }),
            (_('Add tags'), {
                'classes': ('collapse',),
                'fields': ('tags',)
            }),
            (_('Relations'), {
                'classes': ('collapse',),
                'fields': (
                    'contact', 'company',
                    'lead', 'partner_contact',
                    'request'
                )
            }),
            (_('Additional information'), {
                'classes': ('collapse',),
                'fields': (
                    ('owner', 'co_owner'),
                    ('modified_by', 'update_date'),
                    'ticket'
                )
            }),
        )

    def get_list_display(self, request):
        list_display = [
            'dynamic_name', 'attachment', 'marks',
            'next_step_name', 'coloured_next_step_date',
            'stage', 'counterparty']
        if not any(('company' in request.GET, 'lead' in request.GET)):
            list_display.append('deal_counter')
        if not (request.user.is_manager and 'owner' not in request.GET):
            list_display.append('person')
        list_display.extend(['act', 'rel', 'created', 'id'])
        return list_display

    def get_ordering(self, request):
        if hasattr(request, 'session') and \
                "deal_step_date_sorting" in request.session:
            return 'next_step_date',
        return '-id',

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        newest = CrmEmail.objects.filter(
            deal=OuterRef('pk'),
            trash=False
        ).order_by('-creation_date')
        unread = ChatMessage.objects.filter(
            content_type=ContentType.objects.get_for_model(Deal),
            object_id=OuterRef('pk'),
            recipients=request.user
        ).values('id')
        received_payments = Payment.objects.filter(
            deal=OuterRef('pk'),
            status=Payment.RECEIVED,
        ).values('id')
        product = Output.objects.filter(
            deal=OuterRef('pk')
        ).values('id')
        kwargs = {
            'is_unanswered_email': Subquery(
                newest.values('incoming')[:1]
            ),
            'is_unanswered_inquiry': Subquery(
                newest.values('inquiry')[:1]
            ),
            'is_unread_chat': Exists(unread),
            'is_received_payment': Exists(received_payments),
            'is_no_product': ~Exists(product),
        }
        if settings.SHIPMENT_DATE_CHECK:
            today = get_today()
            expired_shipment_date = Output.objects.filter(
                deal=OuterRef('pk'),
                shipping_date__lt=today
            ).values('id')
            empty_date = Output.objects.filter(
                deal=OuterRef('pk'),
                shipping_date__isnull=True
            ).values('id')
            kwargs['is_empty_shipping_date'] = Exists(empty_date)
            kwargs['is_expired_shipment_date'] = Exists(
                expired_shipment_date
            )
            kwargs['is_goods_shipped'] = F('stage__goods_shipped')
        qs = qs.annotate(**kwargs)
        return qs

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            'creation_date', 'update_date',
            'created', 'inquiry', 'workflow',
            'ticket', 'modified_by', 'stages_dates',
            'closing_date', 'translation',
            'coloured_next_step_date', 'rel',
            'act', 'person', 'contact_person',
            'deal_messengers', 'view_website_button',
            'view_company', 'tag_list', 'dynamic_name',
            'counterparty', 'workflow_area', 'marks',
            'create_email', 'connections_to_phone',
            'connections_to_other_phone',
            'connections_to_mobile', 'closed',
            'paid', 'expected', 'attachment', 'deal_counter'
        ]
        if request.user.is_chief:
            readonly_fields.extend((
                'name', 'relevant', 'active',
                'closing_reason', 'stage',
                'amount', 'currency', 'description',
                'products', 'tags', 'contact',
                'request', 'lead', 'company',
                'partner_contact', 'owner'
            ))
        return readonly_fields

    def has_change_permission(self, request, obj=None):
        value = super().has_change_permission(request, obj)
        if not value or not obj:
            return value
        return clarify_permission(request, obj)

    def response_post_save_change(self, request, obj):
        """This method is called by `self.changeform_view()` when the form
        was submitted successfully and should return an HttpResponse.
        """
        if '_create_email_to_partner' in request.POST:
            url = reverse(
                'create_email', args=(obj.pk,)
            ) + '?object=deal&recipient=partner_contact'
            return HttpResponseRedirect(url)
        return super().response_post_save_change(request, obj)

    def save_model(self, request, obj, form, change):
        now = get_now()
        today = get_today()
        if not obj.stage:
            obj.stage = Stage.objects.get(
                default=True,
                department=obj.department
            )
        if 'next_step' in form.changed_data:
            if request.user != obj.owner:
                next_step = obj.next_step + f' ({request.user})'
                next_step_len = len(next_step)
                delta = next_step_len - 250
                if delta > 0:
                    obj.next_step = truncatechars(
                        obj.next_step, len(obj.next_step) - delta
                    )
                obj.next_step += f' ({request.user})'
            obj.add_to_workflow(obj.next_step)
        if 'closing_reason' in form.changed_data:
            obj.active = not bool(obj.closing_reason)
            if obj.closing_reason:
                obj.closing_date = today
                if obj.closing_reason == ClosingReason.objects.get(
                        success_reason=True,
                        department=obj.department
                ):
                    obj.stage = Stage.objects.get(
                        success_stage=True,
                        department=obj.department
                    )
                    obj.change_stage_data(today)
                    obj.win_closing_date = now
            else:
                obj.closing_date = None
        if 'stage' in form.changed_data:
            obj.change_stage_data(today)
            if obj.stage:
                success_stages = Stage.objects.filter(
                    Q(success_stage=True) |
                    Q(conditional_success_stage=True),
                    department=obj.department
                )
                if obj.stage in success_stages:
                    obj.win_closing_date = now
        if 'active' in form.changed_data:
            if obj.active:
                obj.relevant = True
            else:
                obj.closing_date = today
        if 'relevant' in form.changed_data and not obj.relevant:
            obj.active = False
            obj.closing_date = today
        if 'owner' in form.changed_data:
            if obj.lead:
                obj.lead.owner = obj.owner
                obj.lead.save()
        if change:
            if obj.stage and obj.stage == Stage.objects.get(
                    default=True,
                    department=obj.department
            ):
                second_default_stage = Stage.objects.filter(
                    second_default=True,
                    department=obj.department
                ).first()
                if second_default_stage:
                    obj.stage = second_default_stage
        if obj.is_new and obj.owner == request.user:
            obj.is_new = False
        self.set_owner(request, obj)
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        remind_me(request, form, change)
        # If the deal is closed as unsuccessful, delete unreceived payments
        obj = form.instance
        if 'closing_reason' in form.changed_data and not obj.active:
            if not obj.closing_reason.success_reason:
                Payment.objects.filter(deal=obj).exclude(
                    status=Payment.RECEIVED,
                ).delete()

    # -- ModelAdmin Callables -- #

    @admin.display(description=person_outline_safe_icon)
    def contact_person(self, obj):
        if obj.contact:
            url = reverse(
                'site:crm_contact_change', args=(obj.contact_id,)
            )
            name = obj.contact.full_name
        else:
            url = reverse(
                'site:crm_lead_change', args=(obj.lead_id,)
            )
            name = obj.lead.full_name
        return mark_safe(
            f'{name} <ul class="object-tools" style="margin-left: 0px;margin-top: 0px;">\
            <li><a title="{contact_tip}" href="#" onClick="{popup_window(url)}">'
            f'<i class="material-icons" style="font-size: 17px;vertical-align: middle;">visibility</i> '
            f'<i class="material-icons" style="font-size: 17px;vertical-align: middle;">edit</i>'
            f'</a></li></ul>'
        )

    @admin.display(description=get_counterparty_header())
    def counterparty(self, obj):
        counterparty = obj.lead if obj.lead else obj.company
        if counterparty:
            if hasattr(_thread_local, 'deal_changelist_url'):
                url = _thread_local.deal_changelist_url
            else:
                url = reverse("site:crm_deal_changelist")
                _thread_local.deal_changelist_url = url
            url += f"?{counterparty._meta.model_name}={counterparty.id}&active=all"  # NOQA
            name = counterparty.full_name
            if obj.department:

                if obj.department_id in _thread_local.department_id:
                    works_globally = _thread_local.department_id[obj.department_id]
                else:
                    works_globally = Department.objects.get(id=obj.department_id).works_globally
                    _thread_local.department_id[obj.department_id] = works_globally
                if works_globally:
                    name += f", {counterparty.country}"
            link = f'<a href="{url}">{name}</a>'
            return mark_safe(link)
        return LEADERS

    @admin.display(description=mail_outline_safe_icon)
    def create_email(self, obj):
        if obj.id:
            recipient = title = ''
            if getattr(obj.contact, 'email', None):
                recipient = obj.contact._meta.model_name  # NOQA
                title = _("Create Email to Contact")
            elif getattr(obj.lead, 'email', None):
                recipient = obj.lead._meta.model_name  # NOQA
                title = _("Create Email to Lead")
            if recipient:
                url = reverse(
                    'create_email', args=(obj.id,)
                ) + f"?object=deal&recipient={recipient}"
                if url:
                    return mark_safe(
                        f'<ul class="object-tools" style="margin-left: 0px;margin-top: 0px;">\
                        <li><a title="{title}" href="#" onClick="{popup_window(url)}"> '
                        '<i class="material-icons" style="font-size: 17px;vertical-align: middle;">create</i> '
                        '<i class="material-icons" style="font-size: 17px;vertical-align: middle;">drafts</i>'
                        ' </a></li></ul>'
                    )
        return LEADERS

    @staticmethod
    @admin.display(description='')
    def deal_counter(obj):
        counter = None
        if obj.company:
            counter = Deal.objects.filter(company=obj.company).count()
        elif obj.lead:
            counter = Deal.objects.filter(lead=obj.lead).count()

        return mark_safe(
            deal_counter_icon.format(deal_counter_title, counter)
        ) if counter else ''

    @admin.display(description=perm_phone_msg_safe_icon)
    def deal_messengers(self, obj):
        if obj.contact:
            instance = obj.contact
        else:
            instance = obj.lead
        return self.messengers(instance)

    @admin.display(ordering='name')
    def dynamic_name(self, obj):
        if obj.important:
            return mark_safe('<mark title="{title}">{name}</mark>'.format(
                title=gettext("Important deal"),
                name=obj.name)
            )
        return obj.name

    @staticmethod
    def inquiry(obj):
        text = obj.request.description
        return mark_safe(textarea_tag.format(text))

    @admin.display(description='')
    def marks(self, instance):
        icons, icon, days = '', '', 0
        if getattr(instance, 'is_unanswered_inquiry', False):
            inquiry = CrmEmail.objects.filter(
                deal=instance,
                inquiry=True,
                trash=False
            ).order_by('-creation_date').annotate(
                subsequent=F('request__subsequent')
            ).values('creation_date', 'subsequent').first()
            if not inquiry['subsequent']:
                days = (timezone.now() - inquiry['creation_date']).days
            title = _(
                'I have been waiting for an answer to my request for %d days') % days
            if days == 2:
                icon = f'<i class="material-icons" title="{title}" ' \
                       f'style="font-size:small;color: var(--body-quiet-color)">sentiment_neutral</i>'
            elif days in (3, 4):
                icon = f'<i class="material-icons" title="{title}" ' \
                       f'style="font-size:small;color: var(--body-quiet-color)">sentiment_dissatisfied</i>'
            elif days in (5, 6):
                icon = f'<i class="material-icons" title="{title}" ' \
                       f'style="font-size:small;color: var(--body-quiet-color)">sentiment_very_dissatisfied</i>'
            elif 7 <= days:
                icon = f'<i class="material-icons" title="{title}" ' \
                       f'style="font-size:small;color: var(--error-fg)">mood_bad</i>'
        elif getattr(instance, 'is_unanswered_email', False):
            icon = mail_outline_small_icon
        icons += icon
        if getattr(instance, 'is_unread_chat', False):
            icons += message_icon
        if getattr(instance, 'is_received_payment', False):
            icons += payment_received_icon
            if getattr(instance, 'is_empty_shipping_date', False):
                icons += local_shipping_icon
            if instance.is_no_product:
                icons += add_shopping_cart_icon
        if getattr(instance, 'is_expired_shipment_date', False) and \
                not getattr(instance, 'is_goods_shipped', False):
            icons += expired_local_shipping_icon

        return mark_safe(icons)

    @admin.display(description=_('Expected'))
    def expected(self, obj):
        expected_amount = 0
        currency = obj.currency if obj.currency else ''
        if obj.amount:
            expected_amount = obj.amount - obj.paid_amount
        return f"{expected_amount} {currency}"

    @admin.display(description=_('Paid'))
    def paid(self, obj):
        obj.paid_amount = 0
        currency = obj.currency if obj.currency else ''
        if obj.amount:
            paid_amount = Payment.objects.filter(
                deal=obj,
                status=Payment.RECEIVED
            ).aggregate(amount=Sum('amount'))['amount']
            if paid_amount:
                obj.paid_amount = paid_amount
        return f"{obj.paid_amount} {currency}"

    @admin.display(
        description=mark_safe(
            f'<div title="{relevant_deal_str}">{gettext("Rel")}</div>'
        ),
        ordering='relevant',
        boolean=True
    )
    def rel(self, obj):
        return obj.relevant

    @admin.display(
        description=closing_date_safe_icon,
        ordering='closing_date'
    )
    def closed(self, obj):
        return obj.closing_date or LEADERS

    @admin.display(description=_('Translation'))
    def translation(self, obj):
        text = obj.request.translation
        return mark_safe(
            f'<textarea name="description" cols="80" rows="5" '
            f'class="vLargeTextField">{text}</textarea>'
        )

    @admin.display(description=company_safe_icon)
    def view_company(self, obj):
        if obj.company:
            company = ', '.join(
                (obj.company.full_name, obj.company.country.name)
            )
            company_url = reverse(
                'site:crm_company_change', args=(obj.company_id,)
            )
            li = f'<li><a title="{company_tip}" href="#" onClick="{popup_window(company_url)}">' \
                 f'<i class="material-icons" style="font-size: 17px;vertical-align: middle;">visibility</i> ' \
                 f'<i class="material-icons" style="font-size: 17px;vertical-align: middle;">edit</i>' \
                 f'</a></li>'
            return mark_safe(
                f'{company} <ul class="object-tools" style="margin-left: 0px;margin-top: 0px;">{li}</ul>'
            )
        if obj.lead:
            return _("Contact is Lead (no company)")
        return LEADERS

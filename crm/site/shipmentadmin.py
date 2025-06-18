from django.contrib import admin
from django.db.models import Q
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models import Sum
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _

from common.utils.email_to_participants import email_to_participants
from common.utils.helpers import get_trans_for_user
from common.utils.helpers import get_today
from common.utils.helpers import LEADERS
from crm.models import Payment
from crm.models import Shipment
from crm.models import Stage
from crm.utils.admfilters import ByDepartmentFilter
from crm.utils.admfilters import CrmDateFieldListFilter
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter
from crm.utils.helpers import get_counterparty_header
from crm.utils.helpers import NO_DEAL_AMOUNT_STR
from crm.utils.helpers import get_owner_header
from common.utils.helpers import save_message

actual_date_str = _('actual')
actual_date_title = _("Actual shipping date.")
actual_shipping_date_str = mark_safe(
    f'<i title="{actual_date_title}" class="material-icons" '
    f'style="color: var(--body-quiet-color)">event_available</i><br>{actual_date_str}'
)
deal_paid_title = _("Deal is paid.")
next_payment_str = _("Next<br>payment")
order_str = _('order')
ORDER_NUMBER_STR = mark_safe(f"{order_str} &#8470;")
PCS = _('pcs')
product_not_shipped_title = _("The product has not been shipped yet.")
product_shipped_title = _("The product has been shipped.")
shipment_str = _("shipment")
shipment_title = _("Product shipment")
to_contract_str = _("to contract")
to_contract_title = _("Date of shipment according to a contract.")
contract_shipping_date_str = mark_safe(
    f'<i title="{to_contract_title}" class="material-icons" '
    f'style="color: var(--body-quiet-color)">event_busy</i><br>{to_contract_str}'
)
view_deal_title = _("View the deal")


class ShipmentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'product',
                'quantity',
                ('shipping_date', 'planned_shipping_date'),
                'actual_shipping_date',
                'serial_number',
                ('order_number', 'contract_number'),
                'counterparty',
                'person',
            )
        }),
    )
    ordering = ['-shipping_date']
    readonly_fields = (
        'product',
        'quantity',
        'quantity_abbreviation',
        'order_number',
        'counterparty',
        'person',
        'contract_number',
        'coloured_shipping_date',
        'shipping_date',
        'deal_is_paid',
        'actual_date',
        'next_payment',
        'id_deal',
        'shipped',
        'the_country'
    )

    # -- ModelAdmin Methods -- #

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = Shipment.objects.get(id=object_id)
        if request.user.has_perm('crm.view_deal'):
            extra_context['deal_url'] = reverse(
                "site:crm_deal_change", args=(obj.deal_id,)
            )
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def get_changelist_instance(self, request):
        cl = super().get_changelist_instance(request)
        payments = Payment.objects.filter(
            deal=OuterRef('deal')
        ).order_by().values('deal')
        received_payment = payments.filter(
            status=Payment.RECEIVED
        ).annotate(
            payment_sum=Sum('amount')
        )
        next_payment = payments.filter(
            status=Payment.GUARANTEED
        ).order_by('-payment_date')
        cl.result_list = cl.result_list.annotate(
            received_payment_sum=Subquery(
                received_payment.values('payment_sum')),
            next_payment_amount=Subquery(next_payment.values('amount')[:1]),
            next_payment_currency=Subquery(
                next_payment.values('currency__name')[:1]),
            next_payment_date=Subquery(
                next_payment.values('payment_date')[:1]),
        )
        return cl

    def get_list_display(self, request):
        list_display = [
            'product',
            'quantity_abbreviation',
            'coloured_shipping_date',
            'actual_date',
            'shipped',
            'deal_is_paid',
            'next_payment',
            'order_number'         
        ]
        if request.user.has_perm('crm.view_deal'):
            list_display.append('id_deal')
        list_display.extend(['counterparty', 'the_country', 'person'])
        return list_display

    def get_list_filter(self, request):
        list_filter = []
        if any((
                request.user.is_superuser,
                request.user.is_chief,
                request.user.is_superoperator,
                request.user.is_accountant
        )):
            if ByDepartmentFilter not in list_filter:
                list_filter.append(ByDepartmentFilter)

        list_filter.extend((
            'product_is_shipped',
            ('actual_shipping_date',CrmDateFieldListFilter),
            ('product', ScrollRelatedOnlyFieldListFilter)
        ))
        return list_filter
                           
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        queryset = qs.filter(
            shipping_date__isnull=False
        )
        if request.user.is_manager and not any((
            request.user.is_superoperator,
            request.user.is_chief,
            request.user.is_superuser
        )):
            queryset = queryset.filter(
                Q(deal__owner=request.user) |
                Q(deal__co_owner=request.user)
            )
        return queryset

    def has_add_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if "actual_shipping_date" in form.changed_data:
            obj.product_is_shipped = bool(obj.actual_shipping_date)
        super().save_model(request, obj, form, change)
        if change and 'actual_shipping_date' in form.changed_data:
            if obj.product_is_shipped:
                product_is_shipped_str = "The product has been shipped."
                date = get_today()
                deal = obj.deal
                stage = Stage.objects.get(
                    goods_shipped=True,
                    department=deal.department,
                )
                trans_msg = get_trans_for_user(product_is_shipped_str, deal.owner)
                if deal.stage != stage:
                    deal.stage = stage
                    deal.change_stage_data(date)
                    deal.next_step = f'{trans_msg} ({request.user})'
                    deal.next_step_date = date
                    deal.save()
                recipient_list = []
                url = obj.deal.get_absolute_url()

                for user in (obj.deal.owner, obj.deal.co_owner):
                    if user and user != request.user:
                        trans_msg = get_trans_for_user(product_is_shipped_str, user)
                        save_message(
                            user,
                            f'{trans_msg} {_("Deal")} - <a href="{url}"> '
                            f'{deal.name}</a>',
                            'INFO'
                        )
                        if getattr(user, 'email'):
                            recipient_list.append(user)
                    if recipient_list:
                        email_to_participants(obj.deal, product_is_shipped_str, recipient_list)

    # -- ModelAdmin Callables -- #

    @staticmethod
    @admin.display(
        description=actual_shipping_date_str,
        ordering="-actual_shipping_date"
    )
    def actual_date(obj):
        if obj.actual_shipping_date:
            shipping_date = date_format(
                obj.actual_shipping_date,
                format='SHORT_DATE_FORMAT',
                use_l10n=True
            )           
        else:
            shipping_date = LEADERS
        return mark_safe(
            f'<div title="{actual_date_title}" '
            f'>{shipping_date}</div>'
        )

    @staticmethod
    @admin.display(
        description=contract_shipping_date_str,
    )
    def coloured_shipping_date(obj):
        shipping_date = date_format(
            obj.shipping_date,
            format='SHORT_DATE_FORMAT',
            use_l10n=True
        )
        color = 'black'
        if all((not obj.product_is_shipped,
                obj.shipping_date < get_today())):
            color = 'var(--error-fg)'
        return mark_safe(
            f'<div title="{to_contract_title}" '
            f'style="color: {color};">{shipping_date}</div>'
        )

    @admin.display(description=_("contract number"))
    def contract_number(self, obj):
        payment = Payment.objects.filter(deal__id=obj.deal_id).first()
        return payment.contract_number if payment else LEADERS

    @admin.display(description=get_counterparty_header())
    def counterparty(self, obj):
        return obj.deal.contact or obj.deal.lead

    @admin.display(description=_("paid"))
    def deal_is_paid(self, obj):
        value = NO_DEAL_AMOUNT_STR
        if obj.deal.amount:
            value = '0 &nbsp;%'
            if obj.received_payment_sum:
                value = round(
                    obj.received_payment_sum / obj.deal.amount * 100
                )
                value = f"{value}&nbsp;%"
        return mark_safe(
            f'<div title="{deal_paid_title}">{value}</div>'
        )           

    @staticmethod
    @admin.display(description=_('Deal'))
    def id_deal(obj):
        url = reverse(
            "site:crm_deal_change", args=(obj.deal_id,)
        )
        return mark_safe(
            f'<a title="{view_deal_title}" href="{url}">{obj.deal_id}</a>'
        )
 
    @admin.display(description=mark_safe(next_payment_str))
    def next_payment(self, obj):
        if obj.next_payment_amount:
            date = date_format(
                obj.next_payment_date,
                format='SHORT_DATE_FORMAT',
                use_l10n=True
            )
            return mark_safe(
                f"{obj.next_payment_amount} "
                f"{obj.next_payment_currency}<br>{date}"
            )
        return LEADERS

    @staticmethod
    @admin.display(description=ORDER_NUMBER_STR)
    def order_number(obj):
        payment = Payment.objects.filter(deal__id=obj.deal_id).first()
        return getattr(payment, "order_number", None) or LEADERS

    @staticmethod
    @admin.display(description=get_owner_header())
    def person(obj):
        return obj.deal.owner

    @staticmethod
    def planned_date(obj):
        return obj.planned_shipping_date

    @staticmethod
    @admin.display(
        description=mark_safe(
            f'<i title="{shipment_title}" class="material-icons" '
            f'style="color: var(--body-quiet-color)">local_shipping</i><br>{shipment_str}'
        )
    )
    def shipped(obj):
        if obj.product_is_shipped:
            color = 'green'
            title = product_shipped_title
            icon = 'local_shipping'
        else:
            color = 'var(--body-quiet-color)'
            title = product_not_shipped_title
            icon = 'business'            
        return mark_safe(
            f'<i title="{title}" class="material-icons" '
            f'style="color:{color}; font-size:large">{icon}</i>'
        )

    @admin.display(description=mark_safe(
        f'<i class="material-icons" style="color: var(--body-quiet-color)">place</i>'),
        ordering='deal__country'
    )
    def the_country(self, obj):
        return obj.deal.country or LEADERS

    @staticmethod
    @admin.display(description=PCS)
    def quantity_abbreviation(obj):
        return obj.quantity

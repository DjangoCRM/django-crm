from decimal import Decimal
from django.conf import settings
from django.contrib import admin
from django.db.models import Case
from django.db.models import CharField
from django.db.models import DecimalField
from django.db.models import Exists
from django.db.models import F
from django.db.models import OuterRef, Subquery
from django.db.models import Sum
from django.db.models import Value
from django.db.models import When
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from common.models import Department
from common.utils.helpers import get_today
from crm.models import Currency
from crm.models import Output
from crm.models import Rate
from crm.utils.admfilters import PaymentByDepartmentFilter
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter
from crm.utils.admfilters import CrmDateFieldListFilter
from crm.utils.helpers import get_counterparty_header

OFFICIAL_RATE = next(
    (x[1] for x in Rate.RATE_TYPE if x[0] == Rate.OFFICIAL))
APPROXIMATE_RATE = next(
    (x[1] for x in Rate.RATE_TYPE if x[0] == Rate.APPROXIMATE))


class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'value',
        'currency',
        'status',
        'coloured_payment_date',
        'counterparty',
        'products',
        'person'
    )
    list_filter = (
        ('deal__owner', ScrollRelatedOnlyFieldListFilter),
        'status',
        ('payment_date', CrmDateFieldListFilter),
    )
    ordering = ('-payment_date',)
    raw_id_fields = ('deal',)
    readonly_fields = (
        'name',
        'person',
        'products',
        'counterparty',
        'coloured_payment_date',
        'value'
    )
    save_on_top = False

    # -- ModelAdmin methods -- #

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        if response.status_code == 302:
            return response
        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        rate = Rate.objects.filter(
            currency=OuterRef('currency'),
            payment_date=OuterRef('payment_date')
        )
        total_data = queryset.annotate(
            state_value=Case(
                When(
                    Exists(rate),
                    then=F('amount') *
                    Subquery(rate.values('rate_to_state_currency')[:1])
                ),
                default=F('amount') * F('currency__rate_to_state_currency'),
                output_field=DecimalField(),
            ),
            marketing_value=Case(
                When(
                    Exists(rate),
                    then=F('amount') *
                    Subquery(rate.values('rate_to_marketing_currency')[:1])
                ),
                default=F('amount') *
                F('currency__rate_to_marketing_currency'),
                output_field=DecimalField(),
            ),
            rate_type=Case(
                When(
                    Exists(rate),
                    then=Subquery(rate.values('rate_type')[:1]),
                ),
                default=Value(Rate.APPROXIMATE),
                output_field=CharField(),
            ),
        ).aggregate(
            state_amount=Sum('state_value'),
            marketing_amount=Sum('marketing_value'),
            type=Sum(
                Case(
                    When(rate_type__exact=Rate.APPROXIMATE, then=1,),
                    When(rate_type__exact=Rate.OFFICIAL, then=0,),
                    output_field=DecimalField(),
                )
            )
        )
        vatk = Decimal(100 + settings.VAT) / 100
        sta = total_data['state_amount']
        response.context_data['state_amount'] = round(sta, 2) if sta else 0
        response.context_data['vat_state_amount'] = round(
            sta * vatk, 2
            ) if sta else 0
        mta = total_data['marketing_amount']
        response.context_data['marketing_amount'] = round(mta, 2) if mta else 0
        response.context_data['vat_marketing_amount'] = round(
            mta * vatk, 2
            ) if mta else 0
        response.context_data['rate_type'] = OFFICIAL_RATE \
            if total_data['type'] == 0 else APPROXIMATE_RATE
        response.context_data['state_currency'] = Currency.objects.filter(
            is_state_currency=True
        ).first()
        response.context_data['marketing_currency'] = Currency.objects.filter(
            is_marketing_currency=True
        ).first()

        return response

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'currency':
            set_currency_initial(request, kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)   
    
    def has_change_permission(self, request, obj=None):
        value = super(admin.ModelAdmin, self).has_change_permission(
            request, obj)
        if not value or not obj:
            return value
        if request.user.is_manager \
                and request.user not in (obj.deal.owner, obj.deal.co_owner) \
                or request.user.is_operator \
                and obj.deal.department_id != request.user.department_id:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        value = super(admin.ModelAdmin, self).has_delete_permission(
            request, obj)
        if not value or not obj:
            return value
        if request.user.is_manager \
                and request.user not in (obj.deal.owner, obj.deal.co_owner):
            return False
        return True

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': [
                    ('amount', 'currency'),
                    ('payment_date', 'status'),
                    ('contract_number', 'invoice_number'),
                    'order_number',
                    'deal'
                ]
            }),
        ]
        if settings.MARK_PAYMENTS_THROUGH_REP:
            fieldsets[0][1]['fields'].append('through_representation')
        return fieldsets

    def get_list_filter(self, request):
        list_filter = list(self.list_filter)
        if request.user.is_superuser or request.user.is_chief or request.user.is_superoperator:
            if not list_filter.count(PaymentByDepartmentFilter):
                list_filter.insert(0, PaymentByDepartmentFilter)
        return list_filter

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superoperator:
            return qs.filter(
                deal__department__in=request.user.groups.filter(
                    department__isnull=False
                )
            )
        if request.user.department_id and not request.user.is_accountant:
            return qs.filter(deal__department__id=request.user.department_id)
        return qs

    # -- ModelAdmin Callables -- #

    @admin.display(
        description=mark_safe(
            f'<i class="material-icons" title="{_("Payment date")}"'
            f' style="color: var(--body-quiet-color)">event_busy</i>'),
        ordering='payment_date'
    )
    def coloured_payment_date(self, obj):
        if obj.status == 'r':
            return obj.payment_date
        color = 'gray'
        if obj.payment_date < get_today():
            color = 'var(--error-fg)'
        date = date_format(
            obj.payment_date, format='SHORT_DATE_FORMAT', use_l10n=True
        )
        return mark_safe(
            f'<span style="color: {color};">{date}</span>'
        )

    @admin.display(description=mark_safe(
        f'<i class="material-icons" title={_("Payments")}'
        f' style="color: var(--body-quiet-color)">payments</i>'
    ), ordering='deal__name')
    def name(self, obj):
        return obj.deal

    @staticmethod
    def products(obj):
        products = ', '.join([
            f'{otp.product} - {otp.quantity}{otp.pcs}'
            for otp in Output.objects.filter(deal=obj.deal)
        ])
        return products if products else '-'

    @admin.display(
        description=mark_safe(
            '<i class="material-icons" title="Owner" style="color: var(--body-quiet-color)">person</i>')
    )
    def person(self, obj):
        if getattr(obj.deal, 'co_owner', None):
            return f'{obj.deal.owner}, {obj.deal.co_owner}'
        else:
            return obj.deal.owner

    @admin.display(description=get_counterparty_header())
    def counterparty(self, obj):
        return obj.deal.lead if obj.deal.lead else obj.deal.contact
    
    # -- ModelAdmin callables -- #

    @admin.display(description=_('Amount'), ordering='amount')
    def value(self, obj):        # NOQA
        if obj.amount and obj.through_representation:
            title = obj._meta.get_field('through_representation').verbose_name  # NOQA
            icon = '<i class="material-icons" style="font-size: 17px;vertical-align: middle;">swap_calls</i>'
            return mark_safe(
                f'<span title="{title}" style="color: var(--orange-fg)">'
                f'{obj.amount}{icon}</span>')
        else:
            return obj.amount


# -- Custom Methods -- #


def set_currency_initial(request, initial, **kwargs) -> None:
    if request.user.department_id:
        initial = Department.objects.get(
            id=request.user.department_id
        ).default_currency_id                
    else:
        initial = Currency.objects.get(
            is_state_currency=True
        ).id

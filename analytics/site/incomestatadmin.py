from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.handlers.wsgi import WSGIRequest
from django.db import connection
from django.db.models import Case
from django.db.models import DecimalField
from django.db.models import Exists
from django.db.models import F
from django.db.models import FloatField
from django.db.models import Subquery
from django.db.models import Sum
from django.db.models import Q
from django.db.models import OuterRef
from django.db.models import Value as V  # NOQA
from django.db.models import When
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.template.response import TemplateResponse
from django.http.response import HttpResponseRedirect
from django.http.response import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.dateformat import DateFormat
from django.urls import path
from django.urls import reverse

from analytics.models import IncomeStatSnapshot
from analytics.site.anlmodeladmin import AnlModelAdmin
from analytics.utils.helpers import get_current_currency_amount
from analytics.utils.helpers import get_income_over_time
from analytics.utils.helpers import get_currency_info
from analytics.utils.helpers import GroupConcat
from common.utils.helpers import get_today
from common.utils.helpers import LEADERS
from crm.models import Output
from crm.models import Payment
from crm.models import Rate
from crm.utils.admfilters import ByOwnerFilter
from crm.utils.admfilters import USER_MODEL
from crm.utils.helpers import get_products_header
from crm.utils.helpers import get_owner_header


class IncomeStatAdmin(AnlModelAdmin):
    change_list_template = 'analytics/snapshots_change_list.html'
    list_filter = (ByOwnerFilter,)
    page_title = _('Income Summary')

    # -- ModelAdmin methods -- #

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        params = {}
        department_id = request.user.department_id
        params['department_id'] = department_id
        if not department_id:
            department_id = request.GET.get('department')
            if department_id and department_id != 'all':
                params['department_id'] = int(department_id)
        username = request.GET.get('owner')
        if username and username != 'all':
            params['owner__username'] = username
        elif username == 'all':
            params['owner'] = None
        elif not username:
            params['owner'] = None
            if request.user.is_manager:
                owner = request.user  # .username
                params['owner'] = owner
                username = request.user.username
        snapshots = IncomeStatSnapshot.objects.filter(
            **params
        ).order_by('-id')[:4]
        extra_context['snapshots'] = snapshots
        extra_context['today'] = get_today()
        extra_context['username'] = username
        extra_context['next'] = request.build_absolute_uri()
        snapshot = super().changelist_view(
            request, extra_context=extra_context,
        )
        if hasattr(snapshot, 'render'):
            snapshot = snapshot.render()
            snapshot = snapshot.content.decode()
            extra_context['snapshot'] = snapshot
        return super().changelist_view(
            request, extra_context=extra_context,
        )

    def get_urls(self):
        urls = [
            path("view-snapshot/<int:object_id>/",
                 staff_member_required(self.snapshot_view),
                 name='snapshot_view'
                 ),
            path("save-snapshot/",
                 staff_member_required(self.save_snapshot),
                 name='save_snapshot'
                 )
        ]
        return urls + super().get_urls()

    # -- Custom methods -- #

    @staticmethod
    def snapshot_view(request, object_id):  # NOQA
        snapshot = IncomeStatSnapshot.objects.get(id=object_id)
        style = '<style>\
            #changelist-filter{display:none;}\
            input[type="submit"] {display:none;}\
        </style>'
        data = snapshot.webpage.split('<head>')
        return HttpResponse(data[0] + style + data[1])

    @staticmethod
    def save_snapshot(request):
        department_id = request.user.department_id
        webpage = request.POST.get('snapshot')
        username = request.POST.get('username')
        if username in ('all', 'None'):
            owner = None
        else:
            owner = USER_MODEL.objects.filter(
                username=username
            ).first()
        snapshot = IncomeStatSnapshot(
            owner=owner,
            department_id=department_id,
            webpage=webpage,
            modified_by=request.user,
        )
        snapshot.save()
        messages.success(
            request,
            _('The snapshot has been saved successfully.')
        )
        url = request.POST.get('next')
        return HttpResponseRedirect(url)

    def create_context_data(self, request: WSGIRequest,
                            response: TemplateResponse, queryset: QuerySet) -> None:

        currency_code, rate_field_name, button_title = get_currency_info(
            request)
        response.context_data['button_title'] = button_title

        payment_received_qs = Payment.objects.filter(
            deal__in=queryset,
            status=Payment.RECEIVED,
            payment_date__gt=self.year_ago_date,
        )
        income_over_time, income_max = get_income_over_time(
            payment_received_qs,
            'payment_date',
            rate_field_name
        )
        current_period_total = round(
            sum(x['total'] or 0 for x in income_over_time), 2)

        year_ago_date = self.year_ago_date
        payment_received_previous_period_qs = Payment.objects.filter(
            deal__in=queryset,
            status=Payment.RECEIVED,
            payment_date__lt=year_ago_date.replace(
                day=1) + relativedelta(months=1),
            payment_date__gte=self.year_ago_date +
            relativedelta(months=-12, days=+1),
        )
        income_previous_period_over_time, income_previous_max = get_income_over_time(
            payment_received_previous_period_qs,
            'payment_date',
            rate_field_name,
            self.year_ago_date.date()
        )
        income_max = max(income_max, income_previous_max)
        previous_period_total = sum(
            x['total'] or 0
            for x in income_previous_period_over_time
        )
        delta = round(current_period_total - previous_period_total, 2)
        signed_number = ("+" if delta > 0 else "") + str(delta)
        title = _(
            'Income monthly (total amount for the current period: {} {} ({}))'
        ).format(current_period_total, currency_code, signed_number)
        self.add_chart_data(
            response, title, income_over_time, income_max
        )
        title = _('Income monthly in the previous period') + \
            f' ({currency_code})'
        self.add_chart_data(
            response, title, income_previous_period_over_time, income_max
        )
        title = _("Payments received")
        payment_this_month_qs = payment_received_qs.filter(
            payment_date__month=self.current_month,
            payment_date__year=self.today.year,
        ).order_by("payment_date")
        payment_this_month_qs, total_amount = get_current_currency_amount(
            payment_this_month_qs, rate_field_name
        )
        icon = '<i class="material-icons" style="font-size: 17px;vertical-align: middle;">swap_calls</i>'
        rep_title = Payment._meta.get_field('through_representation').verbose_name  # NOQA
        table = {
            'title': f'{title} ({DateFormat(self.today).format("M Y")})',
            'headers': (
                self.get_payment_header(), get_products_header(),
                _("Amount"), self.get_date_header(),
                _('Order'), get_owner_header(),
            ),
            'body': [
                (
                    get_payment_link(p.deal),
                    get_products(p.deal),
                    mark_safe(
                        f'<span title="{rep_title}" style="color: var(--orange-fg)">'
                        f'{round(p.value, 2)} {currency_code}{icon}</span>'
                        ) if p.through_representation 
                        else  f'{round(p.value, 2)} {currency_code}',
                    p.payment_date,
                    p.order_number or LEADERS,
                    f'{p.deal.owner}, {p.deal.co_owner}'
                    if p.deal.co_owner else p.deal.owner
                )
                for p in payment_this_month_qs
            ]
        }

        total_row = (
            mark_safe(f'<b>{_("Total amount")}</b>'),
            LEADERS,
            mark_safe(
                f"<b>{total_amount or '0.00'} {currency_code}</b>"
            )
        )
        table['footers'] = total_row
        response.context_data['data_tables'] = [table]

        # Guaranteed income
        title = _('Guaranteed income')
        self.add_table_expected(
            queryset, Payment.GUARANTEED, title,
            response, currency_code, rate_field_name,
            rep_title, icon
        )

        title = _('High probability income')
        self.add_table_expected(
            queryset, Payment.HIGH_PROBABILITY, title,
            response, currency_code, rate_field_name,
            rep_title, icon
        )

        title = _('Low probability income')
        self.add_table_expected(
            queryset, Payment.LOW_PROBABILITY, title,
            response, currency_code, rate_field_name,
            rep_title, icon
        )

        # income averaged over the year --------
        totals, income_over_year = [], []
        for item in income_over_time:
            item = item.copy()
            earliest_date = item['period'] + relativedelta(months=+1)
            latest_date = earliest_date + relativedelta(months=-12, days=+1)
            payment_queryset = Payment.objects.filter(
                deal__in=queryset,
                status=Payment.RECEIVED,
                payment_date__lt=earliest_date,
                payment_date__gte=latest_date,
            )
            rate = Rate.objects.filter(
                currency=OuterRef('currency'),
                payment_date=OuterRef('payment_date')
            )
            total = payment_queryset.aggregate(
                total=Sum(
                    Case(
                        When(
                            Exists(rate),
                            then=F('amount') *
                            Subquery(rate.values(rate_field_name)[:1]),
                        ),
                        default=F('amount') *
                        F(f'currency__{rate_field_name}'),
                        output_field=DecimalField()
                    )
                )
            )['total']
            item['total'] = total or 0
            income_over_year.append(item)
            totals.append(item['total'])
        max_value = max(*totals)

        title = _('Income averaged over the year ({}).').format(currency_code)
        self.add_chart_data(
            response, title, income_over_year, max_value
        )
        # summary data --------
        total_won_deals = queryset.filter(
            closing_reason__success_reason=True,
            active=False,
            closing_date__gte=self.year_ago_date,
        ).count()
        average_income = round(current_period_total / 12)
        response.context_data['summary'] = {
            _('Total won deals'): total_won_deals,
            _('Average won deals a month'): round(total_won_deals / 12, 1),
            _('Average income amount a month'): f"{average_income} {currency_code}"

        }
        response.context_data['page_title'] = self.page_title

    def add_table_expected(
            self, queryset, status, title,
            response, currency_code, rate_field_name,
            rep_title, icon
    ):
        next_month = (self.today + relativedelta(months=+1)).month
        next_month_date = (self.today + relativedelta(months=+1)
                           ).date().replace(day=1)
        next2_month = (self.today + relativedelta(months=+2)).month
        next3_month_date = (
            self.today + relativedelta(months=+3)
        ).date().replace(day=1)

        deals_qs = queryset.filter(
            payment__payment_date__lt=next3_month_date,
            payment__status=status
        ).distinct()

        payments = Payment.objects.filter(
            deal=OuterRef('pk'),
            status=status
        ).order_by().values('deal')

        rate = Rate.objects.filter(
            currency=OuterRef('currency'),
            payment_date=OuterRef('payment_date')
        )
        current_month_sum = payments.annotate(
            value=Sum(
                Case(
                    When(
                        Exists(rate),
                        then=F('amount') *
                        Subquery(rate.values(rate_field_name)[:1]),
                    ),
                    default=F('amount') * F(f'currency__{rate_field_name}'),
                    output_field=DecimalField()
                ),
                filter=Q(payment_date__lt=next_month_date)
            ),
        )
        current_month_through_rep = payments.filter(
            payment_date__lt=next_month_date,
            through_representation=True
        )
        next_month_sum = payments.annotate(
            value=Sum(
                F('amount') * F(f'currency__{rate_field_name}'),
                filter=Q(payment_date__month=next_month),
            ),
        )
        next_month_through_rep = payments.filter(
            payment_date__month=next_month,
            through_representation=True
        )
        next2_month_sum = payments.annotate(
            value=Sum(
                F('amount') * F(f'currency__{rate_field_name}'),
                filter=Q(payment_date__month=next2_month),
            ),
        )
        next2_month_through_rep = payments.filter(
            payment_date__month=next2_month,
            through_representation=True
        )
        annotate_params = {
            "current_month_sum": Subquery(current_month_sum.values('value')),
            "current_month_through_rep": Exists(current_month_through_rep),
            "next_month_sum": Subquery(next_month_sum.values('value')),
            "next_month_through_rep": Exists(next_month_through_rep),
            "next2_month_sum": Subquery(next2_month_sum.values('value')),
            "next2_month_through_rep": Exists(next2_month_through_rep),
        }
        if connection.vendor == 'mysql':    # for compatibility with postgresql
            annotate_params['orders'] = Subquery(
                payments.annotate(orders=GroupConcat(
                    'order_number')).values('orders')
            )
        deals = deals_qs.annotate(**annotate_params)
        table = {
            'title': title,
            'headers': (
                self.get_payment_header(),
                get_products_header(),
                DateFormat(self.today).format('M Y'),
                DateFormat(
                    self.today + relativedelta(months=+1)
                ).format('M Y'),
                DateFormat(
                    self.today + relativedelta(months=+2)
                ).format('M Y'),
                _('Order'),
                get_owner_header(),
            ),
            'body': []
        }
        total = deals.aggregate(
            current_month_amount=Sum('current_month_sum'),
            next_month_amount=Sum('next_month_sum'),
            next2_month_amount=Sum('next2_month_sum'),
            sum=Coalesce(
                Sum('current_month_sum'),
                V(0),
                output_field=FloatField()
            ) + Coalesce(
                Sum('next_month_sum'),
                V(0),
                output_field=FloatField()
            ) + Coalesce(
                Sum('next2_month_sum'),
                V(0),
                output_field=FloatField()
            )
        )
        for d in deals:
            if connection.vendor != 'mysql':    # for compatibility with postgresql
                order_number = Payment.objects.filter(
                    deal=d,
                    status=status,
                    order_number__isnull=False
                ).values_list('order_number', flat=True)
                d.orders = ", ".join(order_number) if order_number else ''

            row = (
                get_payment_link(d),
                get_products(d),
                format_sum(d.current_month_sum, currency_code, 
                           d.current_month_through_rep, rep_title, icon),
                format_sum(d.next_month_sum, currency_code, 
                           d.next_month_through_rep, rep_title, icon),
                format_sum(d.next2_month_sum, currency_code, 
                           d.next2_month_through_rep, rep_title, icon),
                d.orders if d.orders else LEADERS,
                f'{d.owner}, {d.co_owner}' if d.co_owner else d.owner
            )
            table['body'].append(row)

        title = _("Total amount")
        total_row = (
            mark_safe(f'<b>{title}</b>'),
            "",
            mark_safe(
                f"<b>{round(total['current_month_amount'], 2)} {currency_code}</b>"
            ) if total['current_month_amount'] else LEADERS,
            mark_safe(
                f"<b>{round(total['next_month_amount'], 2)} {currency_code}</b>"
            ) if total['next_month_amount'] else LEADERS,
            mark_safe(
                f"<b>{round(total['next2_month_amount'], 2)} {currency_code}</b>"
            ) if total['next2_month_amount'] else LEADERS,
            '',
            mark_safe(
                f"<b>{round(total['sum'], 2) if total['sum'] else '0.00'} {currency_code}</b>"
            ),
        )
        table['footers'] = total_row
        response.context_data['data_tables'].append(table)


def format_sum(sum, currency_code, through_rep, rep_title, icon):
    if not sum:
        return LEADERS
    return mark_safe(
        f'<span title="{rep_title}" style="color: var(--orange-fg)">'
        f'{round(sum, 2)} {currency_code}{icon}</span>'
        ) if through_rep else  f'{round(sum, 2)} {currency_code}'   


def get_payment_link(deal):
    if deal.contact:
        value_str = f'{deal.contact.company}, {deal.contact.company.country}'
    else:
        if deal.lead.company_name:
            value_str = deal.lead.company_name
        else:
            value_str = deal.lead.first_name
    deal_url = f'{reverse("site:crm_deal_change", args=(deal.id,))}#Payments'
    # deal_url = f'{reverse("site:crm_deal_change", args=(deal.id,))}#id_payment_set-TOTAL_FORMS'
    return mark_safe(
        f'<a href="{deal_url}" target="_blank">{value_str}</a>'
    )


def get_products(deal):
    products = ', '.join([
        f'{otp.product} - {otp.quantity}{otp.pcs}'
        for otp in Output.objects.filter(deal=deal)
    ])
    return products or LEADERS

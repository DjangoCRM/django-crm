from django.contrib.admin import SimpleListFilter
from django.contrib.admin.views.main import PAGE_VAR
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.core.paginator import Paginator
from django.db.models import Case
from django.db.models import CharField
from django.db.models import DecimalField
from django.db.models import Exists
from django.db.models import F
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Subquery
from django.db.models import Sum
from django.db.models import When
from django.db.models.functions import Cast
from django.db.models.query import QuerySet
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from analytics.site.anlmodeladmin import AnlModelAdmin
from analytics.utils.helpers import get_currency_info
from common.models import Department
from common.utils.helpers import LEADERS
from common.utils.helpers import USER_MODEL
from crm.models import Output
from crm.models import Payment
from crm.models import Rate
from crm.site.shipmentadmin import ORDER_NUMBER_STR
from crm.utils.admfilters import ChoicesSimpleListFilter
from crm.utils.admfilters import CrmDateFieldListFilter
from crm.utils.helpers import get_owner_header
from crm.utils.helpers import get_counterparty_header
from crm.utils.helpers import get_products_header

payment_date_title = _("Payment date")
PCS = _('pcs')


class ByCountryFilter(ChoicesSimpleListFilter):
    template = "crm/filter_scroll.html"
    title = _('Country')
    parameter_name = 'country__id__exact'

    def lookups(self, request, model_admin):
        result = [('all', _('All'))]
        department_id = request.user.department_id
        default_country = None
        if department_id:
            default_country = Department.objects.get(
                id=department_id).default_country
        qs = model_admin.get_queryset(request)
        country_id = request.GET.get(self.parameter_name)
        is_null = qs.filter(deal__country_id=None).exists()
        if is_null:
            qs = qs.exclude(deal__country_id=None)

        countries = qs.distinct().annotate(
            str_id=Cast('deal__country_id', output_field=CharField()),
            country_name=F('deal__country__name')
        ).values_list(
            'str_id', 'country_name'
        ).order_by('country_name')

        if country_id not in (None, 'all', 'IsNull'):
            country = countries.get(str_id=country_id)
            countries = countries.exclude(str_id=country_id)
            result.append(country)

        elif country_id is None:
            if default_country:
                result.append((None, default_country.name))
            else:
                result = [(None, _('All'))]

        result.extend([*countries])
        if is_null or country_id == 'IsNull':
            result.append(('IsNull', LEADERS))

        return result

    def queryset(self, request, queryset):
        value = self.value()
        department_id = request.user.department_id
        default_country_id = None
        if not value:
            if department_id:
                default_country_id = Department.objects.get(
                    id=department_id).default_country_id
            if default_country_id:
                return queryset.filter(deal__country_id=default_country_id)
            return queryset

        if value == 'all':
            return queryset

        if value == 'IsNull':
            return queryset.filter(deal__country_id__isnull=True)

        return queryset.filter(deal__country_id=int(self.value()))


class ByOwnerFilter(ChoicesSimpleListFilter):
    title = _('Owner')
    parameter_name = 'owner'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        lookups = [(None, _('All'))]
        if not any((
                request.user.is_superuser,
                request.user.is_superoperator,
                request.user.is_chief,
                request.user.is_accountant
        )):
            q_params = Q(deal__owner=request.user)
            q_params |= Q(deal__co_owner=request.user)
            qs = qs.exclude(q_params)
            lookups = [('all', _('All')), (None, request.user.username)]

        lookups.extend(self.get_owner_lookups(qs))
        if qs.filter(deal__owner=None).exists():
            lookups.append(('IsNull', LEADERS))
        if len(lookups) > 9:
            self.template = "crm/filter_scroll.html"
        return lookups

    @staticmethod
    def get_owner_lookups(queryset: QuerySet[USER_MODEL]) -> list:
        q_params = Q(deal__owner=OuterRef('pk'))
        if hasattr(queryset.model, 'co_owner'):
            q_params |= Q(deal__co_owner=OuterRef('pk'))
        filtered_qs = queryset.filter(q_params)
        owners = USER_MODEL.objects.annotate(
            user=Exists(filtered_qs)
        ).filter(user=True).values_list('username', 'username').order_by('username')

        return [(x[0], x[1]) for x in owners]

    def queryset(self, request, queryset):
        if not any((
                request.user.is_superuser,
                request.user.is_superoperator,
                request.user.is_chief,
                request.user.is_accountant
        )):
            if self.value() is None:
                return self.get_owner_queryset(queryset, request.user.username)

        if self.value() in (x[1] for x in self.lookup_choices):
            return self.get_owner_queryset(queryset, self.value())

        if self.value() == 'IsNull':
            return queryset.filter(deal__owner=None)
        return queryset

    @staticmethod
    def get_owner_queryset(queryset, username):
        q_params = Q(deal__owner__username=username)
        q_params |= Q(deal__co_owner__username=username)
        return queryset.filter(q_params)


class ByProductFilter(SimpleListFilter):
    template = "crm/filter_scroll.html"
    title = _('Product')
    parameter_name = 'product_id'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        payed_deal_ids = qs.values_list('deal_id')
        outputs = Output.objects.filter(deal_id__in=payed_deal_ids).distinct()
        department_id = request.GET.get('department') or request.user.department_id
        if department_id and department_id != 'all':
            outputs = outputs.filter(
                deal__department_id=int(department_id)
            ).distinct()
        products = outputs.values_list(
            'product_id',
            'product__name'
        ).order_by('product__name')
        return [*products]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        deal_ids = Output.objects.filter(
            product_id=int(self.value())
        ).values_list('deal_id', flat=True)
        return queryset.filter(deal_id__in=list(deal_ids))


class OutputStatAdmin(AnlModelAdmin):
    change_list_template = 'analytics/outputstat.html'
    page_title = _("Sold products summary (by date of payment receipt)")


    def get_list_filter(self, request):
        list_filter = [
            ByOwnerFilter,
            ("payment_date", CrmDateFieldListFilter),
            ByProductFilter,
        ]
        department_id = request.GET.get('department') or request.user.department_id
        if department_id and department_id != 'all':
            if Department.objects.get(id=department_id).works_globally:
                list_filter.append(ByCountryFilter)
        return list_filter

    def get_queryset(self, request):
        qs = Payment.objects.filter(status=Payment.RECEIVED)
        if request.user.department_id:
            return qs.filter(deal__department_id=request.user.department_id)
        elif request.user.is_superoperator:
            return qs.filter(
                deal__department__in=request.user.groups.filter(
                    department__isnull=False
                )
            )
        later_payments = Payment.objects.filter(
            deal=OuterRef('deal'),
            status=Payment.RECEIVED,
            payment_date__gt=OuterRef('payment_date')
        )
        qs = qs.annotate(
            later_payments=Exists(later_payments)
        ).filter(later_payments=False)
        return qs

    # -- custom methods -- #
    
    def create_context_data(self, request: WSGIRequest,
                            response: TemplateResponse, queryset: QuerySet) -> None:
        per_page = 100
        payed_deal_ids = queryset.values_list('deal_id')
        output_qs = Output.objects.filter(
            deal_id__in=list(payed_deal_ids)
        )

        product_id = request.GET.get('product_id')
        if product_id and not product_id == 'all':
            output_qs = output_qs.filter(product_id=product_id)
        output_qs = output_qs.annotate(payment_date=Subquery(
            Payment.objects.filter(
                deal=OuterRef('deal'),
                status=Payment.RECEIVED
            ).values("payment_date")[:1]
        )).order_by("-payment_date")
        currency_code, rate_field_name, button_title = get_currency_info(request)
        response.context_data['button_title'] = button_title
        rate = Rate.objects.filter(
            currency=OuterRef('currency'),
            payment_date=Subquery(
                Payment.objects.filter(
                    deal=OuterRef(OuterRef('deal')),
                    status=Payment.RECEIVED
                ).values('payment_date')[:1]
            )
        )
        output_qs = output_qs.annotate(
            value=Case(
                When(
                    Exists(rate),
                    then=F('amount') * Subquery(rate.values(rate_field_name)[:1]),
                ),
                default=F('amount') * F(f'currency__{rate_field_name}'),
                output_field=DecimalField()
            ),
            price=F('value') / F('quantity')
        )
        
        page_num = int(request.GET.get(PAGE_VAR, 0))
        paginator = Paginator(output_qs, per_page)
        try:
            page = paginator.get_page(page_num + 1)
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)
        page.params = dict(request.GET.items())
        page.page_num = page_num
        response.context_data['page'] = page
        response.context_data['page_range'] = page.paginator.page_range
    
        title = _("Sold products")
        table = {
            'title': f'{title}',
            'headers': (
                get_products_header(),
                PCS,
                _("Price"),
                get_counterparty_header(),
                get_owner_header(),
                ORDER_NUMBER_STR,
                mark_safe(
                    f'<i class="material-icons" title="{payment_date_title}" '
                    'style="color: var(--body-quiet-color)">event</i>'
                )
            ),
            'body': [
                (
                    get_products(o),
                    f'{o.quantity} {PCS}',
                    f'{round(o.price, 2)} {currency_code}',
                    o.deal.lead or o.deal.contact,
                    f'{o.deal.owner}, {o.deal.co_owner}'
                    if o.deal.co_owner else o.deal.owner,
                    get_order_number(o),
                    f'{o.payment_date}'
                )
                for o in page
            ]
        }
        total = output_qs.aggregate(quantity=Sum('quantity'), amount=Sum('value'))
        total_row = (
            mark_safe(f'<b>{_("Total amount")}</b>'),
            f"{total['quantity']} {PCS}",
            mark_safe(
                f"<b>{round(total['amount'], 2) if total['amount'] else '0.00'}"
                f" {currency_code}</b>")
        )
        table['body'].append(total_row)
        response.context_data['data_tables'] = [table]
        response.context_data['page_title'] = self.page_title
        response.context_data['next'] = request.build_absolute_uri()


def get_order_number(output):
    payment = Payment.objects.filter(deal__id=output.deal_id).first()
    return getattr(payment, "order_number") or LEADERS


def get_products(output):
    deal_url = f"{reverse('site:crm_deal_change', args=(output.deal.id,))}#Outputs"
    return mark_safe(
        f'<a href="{deal_url}" target="_blank">{output.product}</a'
    )

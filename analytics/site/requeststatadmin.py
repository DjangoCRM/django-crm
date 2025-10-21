from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count
from django.db.models import F
from django.db.models import FloatField
from django.db.models import Q
from django.db.models.functions import Round
from django.db.models.query import QuerySet
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext

from analytics.site.anlmodeladmin import AnlModelAdmin
from analytics.utils.helpers import get_values_over_time
from common.models import Department
from crm.utils.admfilters import ByOwnerFilter

page_title = _("Request source statistics")
source_table_title = _("Number of requests for each source")
country_table_title = _("Requests over country")
all_period_pcs_title = _("for all period")
year_pcs_title = _("for last 365 days")
conversion_str = _("conversion")
total_requests_str = _("Total requests")
not_specified_str = _("Not specified")
name_safe_title = mark_safe(
    '<i class="material-icons" style="color: var(--body-quiet-color)">subject</i>'
)


class BaseRequestStatAdmin(AnlModelAdmin):
    change_list_template = 'analytics/summary_change_list.html'
    list_filter = (ByOwnerFilter,)

    # -- custom methods -- #

    @staticmethod
    def get_conversion(value1: int, value2: int):
        return round(value1 * 100 / value2, 2) if value2 else 0

    def get_total_requests(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(
            receipt_date__gte=self.year_ago_date
        ).exclude(lead__disqualified=True)

    @staticmethod
    def get_total_won_deals(total_requests: QuerySet):
        return total_requests.filter(
            Q(deal__closing_reason__success_reason=True) |
            Q(deal__stage__success_stage=True) |
            Q(deal__stage__conditional_success_stage=True),
        ).distinct()


class RequestStatAdmin(BaseRequestStatAdmin):
    page_title = _('Request Summary for last 365 days')

    # -- custom methods -- #

    def create_context_data(self, request: WSGIRequest,
                            response: TemplateResponse, queryset: QuerySet) -> None:
        total_requests = self.get_total_requests(queryset)
        total_requests_count = total_requests.count()
        total_won_deals = self.get_total_won_deals(total_requests)

        # conversion for primary requests
        primary_requests = total_requests.filter(subsequent=False)
        primary_requests_count = primary_requests.count()
        primary_won_deals = total_won_deals.filter(
            deal__request__in=primary_requests
        )
        primary_won_deals_count = primary_won_deals.count()
        primary_conversion = self.get_conversion(
            primary_won_deals_count,
            primary_requests_count
        )

        # conversion for subsequent requests
        subsequent_requests = total_requests.filter(subsequent=True)
        subsequent_requests_count = subsequent_requests.count()
        subsequent_won_deals = total_won_deals.filter(
            deal__request__in=subsequent_requests
        )
        subsequent_won_deals_count = subsequent_won_deals.count()
        subsequent_conversion = self.get_conversion(
            subsequent_won_deals_count,
            subsequent_requests_count
        )
        conversion_for_primary_str = gettext(
            "Conversion of primary requests into successful deals"
        )
        response.context_data['summary'] = {
            gettext('Total requests'): total_requests_count,
            gettext('Primary requests'): primary_requests_count,
            conversion_for_primary_str: f'{primary_conversion} %',
            gettext('Subsequent requests'): subsequent_requests_count,
            gettext('Conversion of subsequent requests'): f'{subsequent_conversion} %',
        }
        # chart: 'Requests by month'
        average_monthly_value_str = _("average monthly value")
        requests_by_month_str = _('Requests by month')
        average_value = round(total_requests_count / 12, 1)
        title = f"{requests_by_month_str} ({average_monthly_value_str} {average_value})"
        summary_over_time_total, max_value = get_values_over_time(
            total_requests,
            'receipt_date'
        )
        self.add_chart_data(
            response, title, summary_over_time_total, max_value
        )

        # chart: 'Relevant requests'
        relevant_requests = total_requests.filter(deal__relevant=True)
        relevant_requests_count = relevant_requests.count()
        title = gettext('Relevant requests') + f' {relevant_requests_count}'
        summary_over_time_rel, maximum = get_values_over_time(
            relevant_requests,
            'receipt_date'
        )
        self.add_chart_data(
            response, title, summary_over_time_rel, max_value
        )
        response.context_data['page_title'] = self.page_title

        # Summary over countries
        department_id = request.GET.get(
            'department') or request.user.department_id     # NOQA
        if department_id and department_id != 'all':
            if Department.objects.get(id=department_id).works_globally:
                requests = queryset
                summary_over_country = requests.values('country__name').annotate(
                    request_total=Count('pk'),
                    won_deals_total=Count(
                        'pk',
                        filter=Q(deal__closing_reason__success_reason=True)
                        | Q(deal__stage__conditional_success_stage=True)
                    ),
                    year_request_total=Count('pk', filter=Q(creation_date__gte=self.year_ago_date)),
                    year_won_deals_total=Count(
                        'pk',
                        filter=(Q(deal__closing_reason__success_reason=True)
                                | Q(deal__stage__conditional_success_stage=True))
                        & Q(creation_date__gte=self.year_ago_date)
                    ),
                    conversion=Round(
                        F('won_deals_total') * 100 / F('request_total'),
                        precision=1, output_field=FloatField()
                    ),
                    year_conversion=Round(
                        F('year_won_deals_total') * 100 / F('year_request_total'),
                        precision=1, output_field=FloatField()
                    )
                ).order_by('-request_total', 'country__name')

                country_table = {
                    'title': country_table_title,
                    'headers': (name_safe_title, year_pcs_title, all_period_pcs_title),
                    'body': [
                        (
                            country['country__name'],
                            f"{country['year_request_total']} ({conversion_str} "
                            f"{country['year_conversion'] if country['year_conversion'] is not None else 0}%)",
                            f"{country['request_total']} ({conversion_str} {country['conversion']}%)"
                        )
                        for country in summary_over_country
                    ]
                }
                response.context_data['data_tables'] = (country_table,)

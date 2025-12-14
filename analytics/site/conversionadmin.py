from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from analytics.site.requeststatadmin import BaseRequestStatAdmin
from analytics.utils.helpers import get_values_over_time


class ConversionStatAdmin(BaseRequestStatAdmin):
    change_list_template = 'analytics/conversion_summary_change_list.html'
    page_title = _("Conversion of requests into successful deals (for the last 365 days)")

    # -- custom methods -- #

    def create_context_data(self, request: WSGIRequest,
                            response: TemplateResponse, queryset: QuerySet) -> None:
        
        total_requests = self.get_total_requests(queryset)
        total_requests_count = total_requests.count()
        total_won_deals = self.get_total_won_deals(total_requests)
        total_won_deals_count = total_won_deals.count()
        conversion = self.get_conversion(
            total_won_deals_count,
            total_requests_count
        )

        # conversions for primary requests
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

        conversion_of_primary_requests_str = _("Conversion of primary requests")
        response.context_data['summary'] = {
            _('Conversion'): f'{conversion} %',
            conversion_of_primary_requests_str: f'{primary_conversion} %',
            _("Total requests"): total_requests_count,
            _("Total primary requests"): primary_requests_count,
        }

        # chart: 'Conversion'
        total_requests_over_time, max_value1 = get_values_over_time(
            total_requests,
            'receipt_date'
        )
        total_won_deals_over_time, max_value2 = get_values_over_time(
            total_won_deals,
            'receipt_date'
        )
        title = mark_safe(
            f"{_('Conversion')} ({conversion} %)<br><br>"
            f"{_('Total requests')} = {total_requests_count}"
        )
        conversion_over_time = list(map(
            lambda x, y:
            {
                'period': x['period'],
                'total': round(x['total'] / y['total'] * 100, 1)
                if y['total'] else 0
            },
            total_won_deals_over_time, total_requests_over_time
        ))
        max_value = max(
            (x['total'] for x in conversion_over_time)
        )
        self.add_chart_data(
            response, title, conversion_over_time, max_value
        )

        # chart: "Conversion for primary requests"
        primary_requests_over_time, max_value1 = get_values_over_time(
            primary_requests,
            'receipt_date'
        )
        primary_won_deals_over_time, max_value2 = get_values_over_time(
            primary_won_deals,
            'receipt_date'
        )
        primary_conversion_over_time = list(map(
            lambda x, y:
            {
                'period': x['period'],
                'total': round(x['total'] / y['total'] * 100, 1)
                if y['total'] else 0
            },
            primary_won_deals_over_time, primary_requests_over_time
        ))
        max_value2 = max(
            (x['total'] for x in conversion_over_time)
        )
        self.add_chart_data(
            response,
            mark_safe(
                f"{conversion_of_primary_requests_str} ({primary_conversion} %)<br><br>"
                f"{_('Total primary requests')} = {primary_requests_count}"
            ),
            primary_conversion_over_time,
            max_value2
        )
        response.context_data['page_title'] = self.page_title

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count
from django.db.models import F
from django.db.models import Q
from django.db.models import Value
from django.db.models.query import QuerySet
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from analytics.models import RequestStat
from analytics.site.anlmodeladmin import AnlModelAdmin
from analytics.utils.helpers import get_values_over_time

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


class LeadSourceStatAdmin(AnlModelAdmin):
    change_list_template = 'admin/analytics/leadsourcestat/leadsource_summary_change_list.html'
    list_filter = ('name',)

    # -- custom methods -- #

    def create_context_data(self, request: WSGIRequest,
                            response: TemplateResponse, queryset: QuerySet) -> None:

        response.context_data['page_title'] = page_title

        department_id = request.user.department_id  # NOQA
        requests = RequestStat.objects.all()
        if department_id:
            requests = requests.filter(department_id=department_id)

        requests_with_source = requests.filter(lead_source__in=queryset)
        requests_without_source = requests.filter(lead_source=None)
        number_requests_with = requests_with_source.count()
        number_requests_without = requests_without_source.count()
        total_requests_number = number_requests_with + number_requests_without

        year_requests = requests.filter(creation_date__gte=self.year_ago_date)
        year_requests_with_source = year_requests.filter(lead_source__in=queryset)
        year_requests_without_source = year_requests.filter(lead_source=None)
        year_number_requests_with = year_requests_with_source.count()
        year_number_requests_without = year_requests_without_source.count()
        year_total_requests_number = year_number_requests_with + year_number_requests_without

        annotate_params = {
            "request_total": Count(
                'request', filter=Q(request__in=requests_with_source),
                distinct=True
            ),
            "year_request_total": Count(
                'request', filter=Q(request__in=year_requests_with_source),
                distinct=True
            )
        }
        if total_requests_number:
            annotate_params['pers'] = F('request_total') / total_requests_number * 100
        else:
            annotate_params['pers'] = Value(0)
        if year_total_requests_number:
            annotate_params['year_pers'] = F('year_request_total') / year_total_requests_number * 100
        else:
            annotate_params['year_pers'] = Value(0)
        source_qs = queryset.annotate(**annotate_params).order_by('-year_request_total')

        # Add table data
        table = {
            'title': source_table_title,
            'headers': (name_safe_title, year_pcs_title, all_period_pcs_title),
            'body': [
                (
                    source.name,
                    f"{source.year_request_total} ({source.year_pers}%)",
                    f"{source.request_total} ({source.pers}%)"
                )
                for source in source_qs
            ]
        }
        not_specified_pers = round(
            number_requests_without / total_requests_number * 100
        ) if total_requests_number else 0
        year_not_specified_pers = round(
            year_number_requests_without / year_total_requests_number * 100
        ) if total_requests_number else 0
        not_specified_row = (
            not_specified_str,
            f"{year_number_requests_without} ({year_not_specified_pers}%)",
            f"{number_requests_without} ({not_specified_pers}%)"
        )
        table['body'].append(not_specified_row)
        total_row = (
            mark_safe(f"<b>{total_requests_str}</b>"),
            mark_safe(f"<b>{year_total_requests_number} (100%)</b>"),
            mark_safe(f"<b>{total_requests_number} (100%)")
        )
        table['footers'] = total_row
        response.context_data['data_tables'] = [table]

        # Add chart data if one lead source was selected
        if queryset.count() == 1:
            summary_over_time, max_value = get_values_over_time(
                year_requests_with_source,
                'receipt_date'
            )
            title = _('Relevant requests over month')
            self.add_chart_data(
                response, title, summary_over_time, max_value
            )

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Avg
from django.db.models import DurationField
from django.db.models import F
from django.db.models.query import QuerySet
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from analytics.site.anlmodeladmin import AnlModelAdmin
from analytics.utils.helpers import get_values_over_time
from crm.utils.admfilters import ByOwnerFilter


class DealStatAdmin(AnlModelAdmin):
    change_list_template = 'analytics/summary_change_list.html'
    list_filter = (ByOwnerFilter,)
    page_title = _('Deal Summary for last 365 days')

    # -- custom methods -- #

    def create_context_data(self, request: WSGIRequest,
                            response: TemplateResponse, queryset: QuerySet) -> None:
        
        response.context_data['page_title'] = self.page_title 
        year_qs = queryset.filter(request__receipt_date__gte=self.year_ago_date)
        total_deals = year_qs.count()
        rel_qs = year_qs.filter(relevant=True)
        total_rel_deals = rel_qs.count()
        won_qs = queryset.filter(
            closing_reason__success_reason=True,
            active=False,
            closing_date__gte=self.year_ago_date,
        )
        avg_win_closing = won_qs.aggregate(
            days=Avg(
                F('win_closing_date') - F('creation_date'),
                output_field=DurationField()
            )
        )
        days = avg_win_closing['days'].days if avg_win_closing.get('days', None) else 0
        won_num = won_qs.count()

        response.context_data['summary'] = {
            _('Total deals'): total_deals,
            _('Relevant deals'): total_rel_deals,
            _('Closed successfully (primary)'): won_num,
            _('Average days to close successfully (primary)'): days,
        }
        title = _('Total deals') + f' ({total_deals})'
        summary_over_time_total, max_value = get_values_over_time(
            year_qs,
            'request__receipt_date'
        )
        self.add_chart_data(
            response, title, summary_over_time_total, max_value
        )
        total_max_value = max_value
        
        irrel_qs = year_qs.filter(relevant=False)       
        title = _('Irrelevant deals') + f' ({irrel_qs.count()})'      
        relevant_over_time, max_value = get_values_over_time(
            irrel_qs,
            'request__receipt_date'
        )
        self.add_chart_data(
            response, title, relevant_over_time, total_max_value
        )
        
        title = _('Relevant deals') + f' ({total_rel_deals})'        
        relevant_over_time, max_value = get_values_over_time(
            rel_qs,
            'request__receipt_date'
        )
        self.add_chart_data(
            response, title, relevant_over_time, total_max_value
        )
        
        title = _('Won deals') + f' ({won_num})'        
        won_deals_over_time, max_value = get_values_over_time(
            won_qs,
            'closing_date'
        )
        self.add_chart_data(
            response, title, won_deals_over_time, max_value
        )

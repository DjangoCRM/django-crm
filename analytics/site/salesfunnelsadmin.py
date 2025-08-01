from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count
from django.db.models.query import QuerySet
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from analytics.site.anlmodeladmin import AnlModelAdmin
from crm.utils.admfilters import ByOwnerFilter


class SalesFunnelAdmin(AnlModelAdmin):
    change_list_template = 'admin/analytics/salesfunnel/sales_funnel_change_list.html'
    list_filter = (ByOwnerFilter,)

    # -- custom methods -- #

    def create_context_data(self, request: WSGIRequest,
                            response: TemplateResponse, queryset: QuerySet) -> None:
        qs = queryset.filter(
            closing_date__gte=self.year_ago_date,
            relevant=True, 
            active=False
        )
        amount = qs.count()
        data = qs.values('stage__name').annotate(total=Count('id')).order_by('stage')
        high = amount_x = amount
        low = 9E10
        for x in data:
            perc_x = round(x['total'] * 100 / amount_x)
            perc = perc_x if perc_x != 100 else 0
            x['perc'] = f'-{perc}%'
            amount_x -= x['total']
            x['rest'] = amount_x if amount_x else x['total']
            low = x['rest'] if x['rest'] < low else low

        data_list = list(data)
        data_list.insert(0, {
            'stage__name': _('Total closed deals'),
            'total': amount,
            'perc': '',
            'rest': amount,
        })
        response.context_data['sales_funnel'] = [{
            'stage__name': x['stage__name'],
            'total': x['total'] or 2,
            'perc': x['perc'],
            'pct': (int(round((x['rest'] or 2)) / high * 100))
            if high > low else 2,
        } for x in data_list]

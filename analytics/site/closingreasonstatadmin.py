from django.contrib.admin import SimpleListFilter
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count
from django.db.models.query import QuerySet
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from analytics.site.anlmodeladmin import AnlModelAdmin
from analytics.utils.helpers import get_values_over_time
from crm.models import Deal
from crm.models import Product


class ProductFilter(SimpleListFilter):
    title = _('Products')
    parameter_name = 'product_id'

    def lookups(self, request, model_admin):
        data = Product.objects.values_list('id', 'name', flat=False)
        unl = [(x[0], x[1]) for x in data]
        return (*unl,)

    def queryset(self, request, queryset):
        return queryset


class ClosingReasonStatAdmin(AnlModelAdmin):
    change_list_template = 'admin/analytics/closingreasonstat/closingreasons_summary_change_list.html'
    list_filter = (
        'name',
        ProductFilter,
    )
    
    # -- custom methods -- #

    def create_context_data(self, request: WSGIRequest,
                            response: TemplateResponse, queryset: QuerySet) -> None:
        product_id = request.GET.get('product_id')
        department_id = request.user.department_id
        deals = Deal.objects.filter(relevant=True, active=False)
        if department_id:
            deals = deals.filter(department_id=department_id)
        if product_id:
            deals = deals.filter(
                output__product=product_id
            )

        total_deals = deals.count()
        total_qs = queryset.filter(deal__in=deals).annotate(
            total=Count('deal', distinct=True),
            pers=Count('deal', distinct=True)/total_deals*100
        ).order_by('-total')

        response.context_data['summary'] = {
            'total': total_qs,
            'requests': total_deals,
            'product': Product.objects.get(id=product_id) if product_id else None
        }
        total_reasons = queryset.count()
        if total_reasons == 1:
            closing_reason = queryset.first()

            title = _('Closing reason over month')
            reason_queryset = queryset.filter(
                deal__request__creation_date__gte=self.year_ago_date,
                deal__closing_reason=closing_reason
            )
            reason_over_time, maximum = get_values_over_time(
                reason_queryset,
                'deal__request__receipt_date',
            )
            self.add_chart_data(
                response, title, reason_over_time, maximum
            )
            response.context_data['summary_over_country'] = deals.filter(
                creation_date__gte=self.year_ago_date,
                closing_reason=closing_reason
            ).values('country__name').annotate(
                total=Count('id')
            ).order_by('-total', 'country__name')
        else:
            if product_id:
                response.context_data['summary_over_country'] = deals.filter(
                    output__product=product_id
                ).values('country__name').annotate(
                    total=Count('id')
                ).order_by('-total', 'country__name')
            else:
                response.context_data['summary_over_country'] = deals.filter(
                ).values('country__name').annotate(
                    total=Count('id')
                ).order_by('-total', 'country__name')

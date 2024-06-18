from dateutil.relativedelta import relativedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime, now
from django.utils.translation import gettext_lazy as _

from analytics.utils.helpers import get_item_list
from crm.site import crmmodeladmin


class AnlModelAdmin(crmmodeladmin.CrmModelAdmin):

    # -- ModelAdmin methods -- #

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        if response.status_code == 302:
            return response
        response.context_data['charts'] = list()
        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        self.today = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
        self.current_month = self.today.month
        self.year_ago_date = localtime(now()) + relativedelta(months=-12)
        self.create_context_data(request, response, queryset)
        return response

    def get_urls(self):
        urls = [
            path("currency-switching/",
                 staff_member_required(self.currency_switching_view),
                 name="currency_switching"
                 )
        ]
        return urls + super().get_urls()

    # -- custom methods -- #

    @staticmethod
    def currency_switching_view(request: WSGIRequest) -> HttpResponseRedirect:

        url = request.POST.get('next')
        if 'rate_field_name' in request.session:
            if request.session['rate_field_name'] == 'rate_to_marketing_currency':
                request.session['rate_field_name'] = 'rate_to_state_currency'
            else:
                request.session['rate_field_name'] = 'rate_to_marketing_currency'
            return HttpResponseRedirect(url)

        request.session['rate_field_name'] = 'rate_to_state_currency'
        return HttpResponseRedirect(url)

    def create_context_data(self, request: WSGIRequest,
                            response: TemplateResponse, queryset: QuerySet) -> None:
        """Should be realized in child class."""

    def check_time_periods(self, queryset: QuerySet) -> list:
        date = self.today.replace(day=1) + relativedelta(months=-11)
        return get_item_list(queryset, date)

    @staticmethod
    def add_chart_data(response: TemplateResponse, title: str, param, max_value) -> None:
        aa = {
            'title': title,
            'data': ({
                'period': x['period'],
                'total': round(x['total']) or 0,
                'pct':
                    (int(round((x['total'] or 0)) / max_value * 100)) or 2
                    if max_value else 2,
            } for x in param)
        }
        response.context_data['charts'].append(aa)

    @staticmethod
    def get_payment_header():
        return mark_safe(
            f'<i class="material-icons" title={_("Payments")} style="color: var(--body-quiet-color)">payments</i>'
        )

    @staticmethod
    def get_date_header():
        return mark_safe(
            '<i class="material-icons" title="{}" style="color: var(--body-quiet-color)">today</i>'.format(_("Payment date"))
        )

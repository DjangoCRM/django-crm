from django.contrib import admin, messages
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext_lazy as _

from crm.forms.admin_forms import CurrencyForm
from crm.models import Currency


class CurrencyAdmin(admin.ModelAdmin):
    form = CurrencyForm
    list_display = (
        'name', 'rate_to_state_currency',
        'rate_to_marketing_currency', 'is_state_currency', 
        'is_marketing_currency', 'update_date'
    )
    readonly_fields = ('update_date',)

    # -- ModelAdmin methods -- #

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        check_currency(request)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        check_currency(request)


# -- Custom methods -- #

def check_currency(request: WSGIRequest) -> None:
    if not Currency.objects.filter(is_state_currency=True).exists():
        messages.warning(
            request,
            _("State currency must be specified.")
        )
    if not Currency.objects.filter(is_marketing_currency=True).exists():
        messages.warning(
            request,
            _("Marketing currency must be specified.")
        )

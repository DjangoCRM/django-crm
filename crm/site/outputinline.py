import threading

from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from crm.models import Output
from crm.models import Product
from crm.site.crmstackedinline import CrmStackedInline
from crm.utils.helpers import add_id_to_raw_id_field_label
from common.utils.helpers import LEADERS


_thread_local = threading.local()


class OutputInline(CrmStackedInline):
    fieldsets = (
        (None, {
            'fields': (
                ('product', 'quantity'),
                ('amount', 'show_currency'),
                ('shipping_date', 'actual_shipping_date'),
                ('serial_number', 'product_is_shipped')
            )
        }),
    )
    icon = '<a name="Outputs"></a><i class="material-icons" style="color: var(--primary-fg)">shopping_cart</i>'
    model = Output
    name_plural = model._meta.verbose_name_plural
    raw_id_fields = ('product',)
    readonly_fields = ["show_currency", "error_message"]
    verbose_name_plural = mark_safe(f'{icon} {name_plural}')

    class Media:
        js = ('crm/js/outputinline.js',)

    # -- ModelAdmin methods -- #

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'product':
            kwargs["queryset"] = Product.objects.filter(
                department_id=request.user.department_id
            )
        if db_field.name == 'currency':
            kwargs["required"] = False
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_fieldsets(self, request, obj=None):
        if obj:
            _thread_local.currency = str(obj.currency)
            has_existing_outputs = obj.output_set.exists()
            if not has_existing_outputs and not all((obj.tier_name, obj.currency)):
                return (
                    (None, {
                        'fields': ("error_message",)
                    }),
                )
        return super().get_fieldsets(request, obj)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        add_id_to_raw_id_field_label(self, formset.form)
        return formset

    # -- ModelAdmin Callables -- #

    @admin.display(description=_('Currency'))
    def show_currency(self, obj):
        if _thread_local.currency:
            return _thread_local.currency
        return LEADERS


    @staticmethod
    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--orange-fg)">info_outline</i>'
    ))
    def error_message(obj):
        msg = _(
            'First, specify the price tier and currency in the deal.'
        )
        return mark_safe(f'<span style="color: var(--orange-fg)">{msg}</span>')

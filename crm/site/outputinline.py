from django.utils.safestring import mark_safe

from crm.models import Output
from crm.models import Product
from .crmstackedinline import CrmStackedInline
from crm.utils.helpers import add_id_to_raw_id_field_label


class OutputInline(CrmStackedInline):
    fieldsets = (
        (None, {
            'fields': (
                ('product', 'quantity'),
                ('amount', 'currency'),
                ('shipping_date', 'actual_shipping_date'),
                ('serial_number', 'product_is_shipped')
            )
        }),
    )
    icon = '<a name="Outputs"></a><i class="material-icons" style="color: var(--primary-fg)">shopping_cart</i>'
    model = Output
    name_plural = model._meta.verbose_name_plural
    raw_id_fields = ('product',)
    verbose_name_plural = mark_safe(f'{icon} {name_plural}')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'product':
            kwargs["queryset"] = Product.objects.filter(
                department_id=request.user.department_id
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
       
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        add_id_to_raw_id_field_label(self, formset.form)
        return formset

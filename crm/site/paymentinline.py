from django.conf import settings
from django.utils.safestring import mark_safe

from crm.models import Payment
from crm.site.crmstackedinline import CrmStackedInline


class PaymentInline(CrmStackedInline):
    fieldsets = (
        (None, {
            'fields': (
                ('amount', 'currency'),
                ('payment_date', 'status'),
                ('contract_number', 'invoice_number'),
                ('order_number', 'through_representation')
            )
        }),
    )
    icon = '<a id="Payments"></a><i class="material-icons" style="color: var(--primary-fg)">attach_money</i>'
    model = Payment
    name_plural = model._meta.verbose_name_plural
    verbose_name_plural = mark_safe(f'{icon} {name_plural}')

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': [
                    ('amount', 'currency'),
                    ('payment_date', 'status'),
                    ('contract_number', 'invoice_number'),
                ]
            }),
        ]
        if settings.MARK_PAYMENTS_THROUGH_REP:
            fieldsets[0][1]['fields'].append(('order_number', 'through_representation'))
        else:
            fieldsets[0][1]['fields'].append('order_number')
        return fieldsets

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj  # NOQA
        return super().get_formset(request, obj, **kwargs)

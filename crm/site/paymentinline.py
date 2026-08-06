from django.conf import settings
from django.utils.safestring import mark_safe

from crm.models import Payment
from crm.site.crmstackedinline import CrmStackedInline


class PaymentInline(CrmStackedInline):
    icon = '<a id="Payments"></a><i class="material-icons" style="color: var(--primary-fg)">attach_money</i>'
    model = Payment

    @property
    def verbose_name_plural(self):
        return mark_safe(f'{self.icon} {self.model._meta.verbose_name_plural}')

    def get_fieldsets(self, request, obj=None):
        base_fields = [
            ('amount', 'currency'),
            ('payment_date', 'status'),
            ('contract_number', 'invoice_number'),
        ]

        if settings.MARK_PAYMENTS_THROUGH_REP:
            base_fields.append(('order_number', 'through_representation'))
        else:
            base_fields.append('order_number')

        return [(None, {'fields': base_fields})]

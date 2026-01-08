from django.contrib import admin

from crm.admin import crm_site
from crm.admin import TranslateNameModelAdmin
from quality.models import TransactionQualitySignal
from quality.models import TransactionQualityEvent


class TransactionQualitySignalAdmin(TranslateNameModelAdmin):
    list_display = ('name', 'weight', 'notes', 'department')


class TransactionQualityEventAdmin(TranslateNameModelAdmin):
    list_display = ('signal', 'weight', 'details', )



admin.site.register(TransactionQualitySignal,
    TransactionQualitySignalAdmin
)
admin.site.register(TransactionQualityEvent,
    TransactionQualityEventAdmin
)

crm_site.register(
    TransactionQualitySignal,
    TransactionQualitySignalAdmin
)
crm_site.register(
    TransactionQualityEvent,
    TransactionQualityEventAdmin
)

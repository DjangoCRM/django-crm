from django.contrib import admin
from common.admin import FileInline


class TransactionQualityEventAdmin(admin.ModelAdmin):
    list_display = ('signal', 'weight', 'details', )
    inlines = [FileInline]
    readonly_fields = ['deal', 'creation_date']

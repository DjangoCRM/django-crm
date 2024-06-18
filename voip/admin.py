from django.contrib import admin
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter
from voip.models import Connection


class ConnectionAdmin(admin.ModelAdmin):
    list_display = (
        'callerid', 'provider', 'number', 'type', 'owner', 'active'
    )
    list_filter = (
        'active', 'type',
        ('owner', ScrollRelatedOnlyFieldListFilter)
    )
    fieldsets = (
        (None, {
            'fields': (
                ('provider', 'active'),
                ('number', 'type'),
                'callerid', 'owner'
            )
        }),
    )


admin.site.register(Connection, ConnectionAdmin)

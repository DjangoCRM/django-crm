from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from common.utils.get_signature_preview import get_signature_preview
from crm.site.crmmodeladmin import CrmModelAdmin
from crm.utils.admfilters import ByOwnerFilter


class SignatureAdmin(CrmModelAdmin):
    list_display = (
        'name',
        'person',
        'type',
        'update_date'
    )
    list_filter = (ByOwnerFilter,)
    readonly_fields = (
        'owner',
        'modified_by',
        'update_date',
        'creation_date',
        'department',
        'preview'
    )
    save_on_top = False
    
    # -- ModelAdmin methods -- #
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (_('Change'), {
                'fields': (
                    ('name', 'default', 'type'),
                    'content',
                )
            }),
            (_('Additional information'), {
                'classes': ('collapse',),
                'fields': (
                    'department', 
                    ('owner', 'modified_by'),
                    ('creation_date', 'update_date')
                )
            })
        ]
        if obj:
            fieldsets.insert(
                0, (_('Preview'), {
                    'fields': ('preview',)
                })
            )
        return fieldsets
    
    # -- ModelAdmin callables -- #
    
    @admin.display(description='')
    def preview(self, obj):
        return get_signature_preview(obj)

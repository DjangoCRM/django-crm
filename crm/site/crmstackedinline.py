from django.contrib.admin import StackedInline

from crm.site.paymentadmin import set_currency_initial
from crm.utils.clarify_permission import clarify_permission


class CrmStackedInline(StackedInline):
    extra = 0

    # -- StackedInline methods -- #

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'currency':
            set_currency_initial(request, kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def has_add_permission(self, request, obj):
        # who can change parent object should
        # have permission to add inline
        return self.has_change_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        value = super().has_change_permission(request, obj)
        if not value or not obj:
            return value
        return clarify_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # who can change parent object should
        # have permission to delete inline
        return self.has_change_permission(request, obj)

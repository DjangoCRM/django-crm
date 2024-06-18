from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from common.admin import FileInline
from crm.utils.admfilters import ByDepartmentFilter
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter


class ProductAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': (
                'name', 'type',
                'product_category',
                'description', ('price', 'currency')
            )
        }),
        (_('Additional information'), {
            'classes': ('collapse',),
            'fields': [
                'modified_by',
                ('creation_date', 'update_date'),
            ]
        }),
    ]
    inlines = [FileInline]
    list_display = (
        'name',
        'price',
        'currency',
        'type',
        'product_category'
        )
    list_filter = ('type', ('product_category', ScrollRelatedOnlyFieldListFilter))
    radio_fields = {"type": admin.HORIZONTAL}
    readonly_fields = ('modified_by', 'creation_date', 'update_date')
    save_on_top = False
    search_fields = ['name', 'description']

    # -- ModelAdmin methods -- #

    def get_list_filter(self, request):
        list_filter = list(self.list_filter)
        if request.user.is_superuser or request.user.is_chief:
            list_filter.insert(0, ByDepartmentFilter)
        return list_filter

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.department_id:
            qs = qs.filter(department_id=request.user.department_id)
        elif request.user.is_superoperator:
            qs = qs.filter(
                department__in=request.user.groups.filter(
                    department__isnull=False
                )
            )
        return qs

    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user
        if not obj.department and request.user.department_id:
            obj.department_id = request.user.department_id
        super().save_model(request, obj, form, change)

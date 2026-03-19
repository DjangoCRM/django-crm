from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from common.admin import FileInline
from crm.utils.admfilters import ByDepartmentFilter
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter


CATEGORY = _('Category')


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
        'name_icon',
        'price',
        'currency',
        'get_type',
        'get_category'
    )
    list_filter = ('type', ('product_category',
                   ScrollRelatedOnlyFieldListFilter))
    radio_fields = {"type": admin.HORIZONTAL}
    readonly_fields = ('modified_by', 'creation_date', 'update_date')
    save_on_top = False
    search_fields = ['name', 'description']

    # -- ModelAdmin methods -- #

    def changelist_view(self, request, extra_context=None):
        self.changelist_url = reverse("site:crm_product_changelist")
        self.query_dict = request.GET.copy()
        return super().changelist_view(
            request, extra_context=extra_context,
        )

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

    # -- ModelAdmin callables -- #

    @admin.display(
        description=CATEGORY,
        ordering='product_category__name'
    )
    def get_category(self, obj):
        category = obj.product_category
        if category:
            self.query_dict['product_category__id__exact'] = category.id
            url = f"{self.changelist_url}?{self.query_dict.urlencode()}"
            return mark_safe(
                f'<a href="{url}" title="{CATEGORY}">{category.name}</a>'
            )

    @admin.display(
        description=_("Type"),
        ordering='type'
    )
    def get_type(self, obj):
        self.query_dict['type__exact'] = obj.type
        url = f"{self.changelist_url}?{self.query_dict.urlencode()}"
        return mark_safe(
            f'<a href="{url}" title="{_('Type')}">{obj.TYPE_CHOICES[obj.type]}</a>'
        )

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">subject</i>'
    ), ordering='name')
    def name_icon(self, obj):
        return obj.name

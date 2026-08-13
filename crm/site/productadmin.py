from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from common.admin import FileInline
from common.utils.helpers import SAFE_SUBJECT_ICON
from common.utils.resize_image import resize_image
from crm.utils.admfilters import ByDepartmentFilter
from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter


CATEGORY = _('Category')


class ProductAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': (
                'main_image_preview', 'main_image',
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
    readonly_fields = ('modified_by', 'creation_date', 'update_date',
        'main_image_preview'
    )
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
        # Resize new main image if present
        if 'main_image' in form.changed_data and obj.main_image:
            resize_main_image(obj)
        if change and 'main_image' in form.changed_data:
            # Delete old main image file if a new one is being uploaded
            try:
                old_instance = self.model.objects.get(pk=obj.pk)
                if old_instance.main_image and old_instance.main_image != obj.main_image:
                    old_instance.main_image.delete(save=False)
            except self.model.DoesNotExist:
                pass
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

    @admin.display(description='')
    def main_image_preview(self, obj):
        if obj.main_image:
            return mark_safe(
                f'<img src="{obj.main_image.url}" style="width:200px;height:200px;">'
            )
        return mark_safe(
            '<i class="material-icons" style="font-size: 200px;vertical-align: middle;'
            'border-radius:50%;color: var(--body-quiet-color)">inventory_2</i>'
        )

    @admin.display(description=SAFE_SUBJECT_ICON, ordering='name')
    def name_icon(self, obj):
        if obj.main_image:
            return mark_safe(
                f'<span style="white-space: nowrap;">'
                f'<img src="{obj.main_image.url}" style="vertical-align: middle;'
                'width:20px;height:20px;">'
                f'&nbsp;{obj.name}</span>'
            )
        return obj.name


def resize_main_image(obj) -> None:
    """
    Resize uploaded main image to a maximum of 200x200 pixels.
    """
    if obj.main_image:
        resized_image = resize_image(obj.main_image)

        # Create a new File object
        obj.main_image.file = resized_image
        obj.main_image.name = f"{obj.name}.png"

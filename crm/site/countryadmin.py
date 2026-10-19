from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from common.utils.helpers import SAFE_SUBJECT_ICON


class CountryAdmin(admin.ModelAdmin):
    class Media:
        css = {
            "all": ["css/flag-icons.css"],
        }
    fieldsets = (
        (None, {'fields': [
            'flag_preview', 'name', "alternative_names",
            'subregion', 'intermediary_region',
            'owner',
        ], }),
        (_('Additional information'), {
            'classes': ('collapse',),
            'fields': ('iso_code', 'phone_code', "url_name")
        }),
    )
    list_display = ('flag_and_name', 'subregion',
                    'owner', 'iso_code', 'phone_code')
    ordering = ["name"]
    readonly_fields = ('flag_preview',)
    search_fields = ('name', "alternative_names", 'iso_code', 'phone_code')

    # -- ModelAdmin Callables -- #

    @staticmethod
    @admin.display(description=SAFE_SUBJECT_ICON)
    def flag_and_name(obj):
        return obj.flag_and_name

    @admin.display(description='')
    def flag_preview(self, obj):
        if obj.iso_code:
            return mark_safe(
                f'<span class="fi fi-{obj.iso_code}" style="font-size: 200px;vertical-align: middle;"></span>'
            )
        return mark_safe(
            f'<span class="fi fi-xx" style="font-size: 200px;vertical-align: middle;"></span>'
        )

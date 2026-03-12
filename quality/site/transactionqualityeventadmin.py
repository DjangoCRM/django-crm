from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from common.admin import FileInline
from common.utils.get_file_links import get_file_links
from common.utils.helpers import SAFE_ATTACH_FILE_ICON


class TransactionQualityEventAdmin(admin.ModelAdmin):
    list_display = ('signal', 'percentage', 'details', 'files')
    inlines = [FileInline]
    readonly_fields = ['deal', 'creation_date']

    # -- ModelAdmin callables -- #

    @admin.display(description=SAFE_ATTACH_FILE_ICON)
    def files(self, obj):
        files = obj.files.all()
        if files:
            return get_file_links(files)
        return ''

    @admin.display(description=_("Weight (%)"))
    def percentage(self, obj):
        return f"{obj.weight}%"

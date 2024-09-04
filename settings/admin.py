from django.contrib import admin

from crm.site.crmadminsite import crm_site
from settings.models import BannedCompanyName
from settings.models import PublicEmailDomain
from settings.models import StopPhrase
# from settings.models import Reminders


class BannedCompanyNameAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class PublicEmailDomainAdmin(admin.ModelAdmin):
    list_display = ('domain',)
    search_fields = ('domain',)


class RemindersAdmin(admin.ModelAdmin):

    # -- ModelAdmin methods -- #

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class StopPhraseAdmin(admin.ModelAdmin):
    list_display = ('phrase', 'last_occurrence_date')
    search_fields = ('phrase',)


crm_site.register(BannedCompanyName, BannedCompanyNameAdmin)
crm_site.register(PublicEmailDomain, PublicEmailDomainAdmin)
crm_site.register(StopPhrase, StopPhraseAdmin)

admin.site.register(BannedCompanyName, BannedCompanyNameAdmin)
admin.site.register(PublicEmailDomain, PublicEmailDomainAdmin)
# admin.site.register(Reminders, RemindersAdmin)
admin.site.register(StopPhrase, StopPhraseAdmin)

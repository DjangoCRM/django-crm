from django.contrib import admin
from django.contrib.auth.models import Permission

from analytics.models import ClosingReasonStat
from analytics.models import ConversionStat
from analytics.models import DealStat
from analytics.models import IncomeStat
from analytics.models import IncomeStatSnapshot
from analytics.models import LeadSourceStat
from analytics.models import OutputStat
from analytics.models import RequestStat
from analytics.models import SalesFunnel
from analytics.site.conversionadmin import ConversionStatAdmin
from analytics.site.closingreasonstatadmin import ClosingReasonStatAdmin
from analytics.site.dealstatadmin import DealStatAdmin
from analytics.site.incomestatadmin import IncomeStatAdmin
from analytics.site.leadsourcestatadmin import LeadSourceStatAdmin
from analytics.site.outputstatadmin import OutputStatAdmin
from analytics.site.requeststatadmin import RequestStatAdmin
from analytics.site.salesfunnelsadmin import SalesFunnelAdmin
from crm.site.crmadminsite import crm_site


class IncomeStatSnapshotAdmin(admin.ModelAdmin):
    list_display = ('creation_date', 'id', 'owner',
                    'department', 'modified_by')
    list_filter = ('creation_date', 'owner', 'department')


admin.site.register(IncomeStatSnapshot, IncomeStatSnapshotAdmin)
admin.site.register(Permission)

crm_site.register(ClosingReasonStat, ClosingReasonStatAdmin)
crm_site.register(ConversionStat, ConversionStatAdmin)
crm_site.register(DealStat, DealStatAdmin)
crm_site.register(IncomeStat, IncomeStatAdmin)
admin.site.register(IncomeStat, IncomeStatAdmin)
crm_site.register(LeadSourceStat, LeadSourceStatAdmin)
crm_site.register(OutputStat, OutputStatAdmin)
crm_site.register(RequestStat, RequestStatAdmin)
crm_site.register(SalesFunnel, SalesFunnelAdmin)

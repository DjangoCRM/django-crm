from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import Base1
from crm.models import ClosingReason
from crm.models import Deal
from crm.models import LeadSource
from crm.models import Payment
from crm.models import Request


class IncomeStatSnapshot(Base1):
    
    class Meta:
        verbose_name = _('IncomeStat Snapshot')
        verbose_name_plural = _('IncomeStat Snapshots')
            
    webpage = models.TextField(
        blank=True, default='',
    )        
    update_date = None


class OutputStat(Payment):
    
    class Meta:
        proxy = True
        verbose_name = _('Sales Report')
        verbose_name_plural = _('Sales Report')
        

class RequestStat(Request):
    
    class Meta:
        proxy = True
        verbose_name = _('Request Summary')
        verbose_name_plural = _('Requests Summary')
        
        
class LeadSourceStat(LeadSource):
    
    class Meta:
        proxy = True
        verbose_name = _('Lead source Summary')
        verbose_name_plural = _('Lead source Summary')
        
        
class ClosingReasonStat(ClosingReason):
    
    class Meta:
        proxy = True
        verbose_name = _('Closing reason Summary')
        verbose_name_plural = _('Closing reason Summary')
        
        
class DealStat(Deal):
    
    class Meta:
        proxy = True
        verbose_name = _('Deal Summary')
        verbose_name_plural = _('Deal Summary')
        
         
class IncomeStat(Deal):
    
    class Meta:
        proxy = True
        verbose_name = _('Income Summary')
        verbose_name_plural = _('Income Summary')
        
        
class SalesFunnel(Deal):
    
    class Meta:
        proxy = True
        verbose_name = _('Sales funnel')
        verbose_name_plural = _('Sales funnel')
        
        
class ConversionStat(Request):
    
    class Meta:
        proxy = True
        verbose_name = _('Conversion Summary')
        verbose_name_plural = _('Conversion Summary')

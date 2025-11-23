"""
CRM Analytics Dashboard Plugins for django-dash
"""
from dash.base import BaseDashboardPlugin
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from datetime import datetime, timedelta
from decimal import Decimal
import json

from crm.models import Deal, Lead, Contact, Request
from analytics.models import IncomeStat, DealStat, LeadSourceStat
from analytics.utils.helpers import get_quarter_start, get_quarter_end


class SalesOverviewPlugin(BaseDashboardPlugin):
    """Sales Overview Dashboard Plugin"""
    
    name = 'sales_overview'
    title = _('Sales Overview')
    description = _('Key sales metrics and KPIs')
    category = _('Analytics')
    
    def process(self, request, **kwargs):
        """Process the plugin data"""
        # Get date range (last 30 days by default)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Sales metrics
        deals_qs = Deal.objects.filter(
            creation_date__date__range=[start_date, end_date]
        )
        
        total_deals = deals_qs.count()
        won_deals = deals_qs.filter(stage__title__icontains='won').count()
        lost_deals = deals_qs.filter(stage__title__icontains='lost').count()
        
        total_revenue = deals_qs.filter(
            stage__title__icontains='won'
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        # Conversion rates
        win_rate = (won_deals / total_deals * 100) if total_deals > 0 else 0
        
        # Lead metrics
        leads_count = Lead.objects.filter(
            creation_date__date__range=[start_date, end_date]
        ).count()
        
        converted_leads = Lead.objects.filter(
            creation_date__date__range=[start_date, end_date],
            contact__isnull=False
        ).count()
        
        lead_conversion_rate = (converted_leads / leads_count * 100) if leads_count > 0 else 0
        
        context = {
            'total_deals': total_deals,
            'won_deals': won_deals,
            'lost_deals': lost_deals,
            'total_revenue': total_revenue,
            'win_rate': round(win_rate, 1),
            'leads_count': leads_count,
            'converted_leads': converted_leads,
            'lead_conversion_rate': round(lead_conversion_rate, 1),
            'period_start': start_date,
            'period_end': end_date,
        }
        
        return render_to_string('analytics/dash/sales_overview.html', context)


class RevenueChartPlugin(BaseDashboardPlugin):
    """Revenue Chart Dashboard Plugin"""
    
    name = 'revenue_chart'
    title = _('Revenue Chart')
    description = _('Monthly revenue trends')
    category = _('Analytics')
    
    def process(self, request, **kwargs):
        """Process revenue chart data"""
        # Get last 12 months data
        end_date = datetime.now().date()
        start_date = end_date.replace(day=1) - timedelta(days=365)
        
        # Monthly revenue data
        monthly_revenue = Deal.objects.filter(
            creation_date__date__range=[start_date, end_date],
            stage__title__icontains='won'
        ).annotate(
            month=TruncMonth('creation_date')
        ).values('month').annotate(
            revenue=Sum('amount')
        ).order_by('month')
        
        # Prepare chart data
        chart_data = {
            'labels': [],
            'datasets': [{
                'label': 'Revenue',
                'data': [],
                'borderColor': 'rgb(54, 162, 235)',
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'tension': 0.1
            }]
        }
        
        for item in monthly_revenue:
            chart_data['labels'].append(item['month'].strftime('%b %Y'))
            chart_data['datasets'][0]['data'].append(float(item['revenue'] or 0))
        
        context = {
            'chart_data': json.dumps(chart_data),
            'chart_id': 'revenue-chart'
        }
        
        return render_to_string('analytics/dash/revenue_chart.html', context)


class LeadSourcesPlugin(BaseDashboardPlugin):
    """Lead Sources Analysis Plugin"""
    
    name = 'lead_sources'
    title = _('Lead Sources')
    description = _('Lead distribution by sources')
    category = _('Analytics')
    
    def process(self, request, **kwargs):
        """Process lead sources data"""
        # Get lead sources data
        lead_sources = Lead.objects.values(
            'lead_source__name'
        ).annotate(
            count=Count('id'),
            converted=Count('id', filter=Q(contact__isnull=False))
        ).order_by('-count')[:10]
        
        # Prepare chart data
        chart_data = {
            'labels': [],
            'datasets': [
                {
                    'label': 'Total Leads',
                    'data': [],
                    'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                },
                {
                    'label': 'Converted',
                    'data': [],
                    'backgroundColor': 'rgba(75, 192, 192, 0.5)',
                }
            ]
        }
        
        total_leads = 0
        total_converted = 0
        
        for source in lead_sources:
            source_name = source['lead_source__name'] or 'Unknown'
            chart_data['labels'].append(source_name)
            chart_data['datasets'][0]['data'].append(source['count'])
            chart_data['datasets'][1]['data'].append(source['converted'])
            
            total_leads += source['count']
            total_converted += source['converted']
        
        conversion_rate = (total_converted / total_leads * 100) if total_leads > 0 else 0
        
        context = {
            'chart_data': json.dumps(chart_data),
            'chart_id': 'lead-sources-chart',
            'total_leads': total_leads,
            'total_converted': total_converted,
            'conversion_rate': round(conversion_rate, 1),
            'sources_data': lead_sources
        }
        
        return render_to_string('analytics/dash/lead_sources.html', context)


class SalesFunnelPlugin(BaseDashboardPlugin):
    """Sales Funnel Analysis Plugin"""
    
    name = 'sales_funnel'
    title = _('Sales Funnel')
    description = _('Deal progression through sales stages')
    category = _('Analytics')
    
    def process(self, request, **kwargs):
        """Process sales funnel data"""
        # Get deals by stage
        funnel_data = Deal.objects.values(
            'stage__title'
        ).annotate(
            count=Count('id'),
            total_value=Sum('amount')
        ).order_by('stage__index')
        
        # Calculate funnel metrics
        total_deals = Deal.objects.count()
        total_value = Deal.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        funnel_stages = []
        for i, stage in enumerate(funnel_data):
            stage_name = stage['stage__title'] or f'Stage {i+1}'
            stage_count = stage['count']
            stage_value = stage['total_value'] or Decimal('0')
            
            # Calculate percentages
            count_percentage = (stage_count / total_deals * 100) if total_deals > 0 else 0
            value_percentage = (stage_value / total_value * 100) if total_value > 0 else 0
            
            funnel_stages.append({
                'name': stage_name,
                'count': stage_count,
                'value': stage_value,
                'count_percentage': round(count_percentage, 1),
                'value_percentage': round(value_percentage, 1),
            })
        
        context = {
            'funnel_stages': funnel_stages,
            'total_deals': total_deals,
            'total_value': total_value
        }
        
        return render_to_string('analytics/dash/sales_funnel.html', context)


class TopPerformersPlugin(BaseDashboardPlugin):
    """Top Performers Plugin"""
    
    name = 'top_performers'
    title = _('Top Performers')
    description = _('Top performing sales representatives')
    category = _('Analytics')
    
    def process(self, request, **kwargs):
        """Process top performers data"""
        # Get current month start
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Top performers by deals won
        top_by_deals = Deal.objects.filter(
            stage__title__icontains='won',
            creation_date__gte=month_start
        ).values(
            'owner__first_name', 
            'owner__last_name'
        ).annotate(
            deals_count=Count('id'),
            total_revenue=Sum('amount')
        ).order_by('-deals_count')[:5]
        
        # Top performers by revenue
        top_by_revenue = Deal.objects.filter(
            stage__title__icontains='won',
            creation_date__gte=month_start
        ).values(
            'owner__first_name', 
            'owner__last_name'
        ).annotate(
            deals_count=Count('id'),
            total_revenue=Sum('amount')
        ).order_by('-total_revenue')[:5]
        
        context = {
            'top_by_deals': top_by_deals,
            'top_by_revenue': top_by_revenue,
            'month_name': now.strftime('%B %Y')
        }
        
        return render_to_string('analytics/dash/top_performers.html', context)


class RecentActivityPlugin(BaseDashboardPlugin):
    """Recent Activity Plugin"""
    
    name = 'recent_activity'
    title = _('Recent Activity')
    description = _('Latest CRM activities')
    category = _('Analytics')
    
    def process(self, request, **kwargs):
        """Process recent activity data"""
        # Recent deals (last 10)
        recent_deals = Deal.objects.select_related(
            'owner', 'contact', 'company'
        ).order_by('-creation_date')[:10]
        
        # Recent leads (last 10)
        recent_leads = Lead.objects.select_related(
            'owner', 'lead_source'
        ).order_by('-creation_date')[:10]
        
        # Recent requests (last 10)
        recent_requests = Request.objects.select_related(
            'owner', 'contact'
        ).order_by('-creation_date')[:10]
        
        context = {
            'recent_deals': recent_deals,
            'recent_leads': recent_leads,
            'recent_requests': recent_requests
        }
        
        return render_to_string('analytics/dash/recent_activity.html', context)


class KPIMetricsPlugin(BaseDashboardPlugin):
    """KPI Metrics Plugin"""
    
    name = 'kpi_metrics'
    title = _('KPI Metrics')
    description = _('Key Performance Indicators')
    category = _('Analytics')
    
    def process(self, request, **kwargs):
        """Process KPI metrics"""
        # Current period (this month)
        now = datetime.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Previous period (last month)
        if now.month == 1:
            prev_month_start = now.replace(year=now.year-1, month=12, day=1)
            prev_month_end = current_month_start - timedelta(days=1)
        else:
            prev_month_start = now.replace(month=now.month-1, day=1)
            prev_month_end = current_month_start - timedelta(days=1)
        
        # Current month metrics
        current_deals = Deal.objects.filter(creation_date__gte=current_month_start)
        current_won_deals = current_deals.filter(stage__title__icontains='won')
        current_revenue = current_won_deals.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        current_leads = Lead.objects.filter(creation_date__gte=current_month_start).count()
        
        # Previous month metrics
        prev_deals = Deal.objects.filter(
            creation_date__range=[prev_month_start, prev_month_end]
        )
        prev_won_deals = prev_deals.filter(stage__title__icontains='won')
        prev_revenue = prev_won_deals.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        prev_leads = Lead.objects.filter(
            creation_date__range=[prev_month_start, prev_month_end]
        ).count()
        
        # Calculate changes
        def calculate_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return ((current - previous) / previous) * 100
        
        revenue_change = calculate_change(float(current_revenue), float(prev_revenue))
        deals_change = calculate_change(current_won_deals.count(), prev_won_deals.count())
        leads_change = calculate_change(current_leads, prev_leads)
        
        context = {
            'current_revenue': current_revenue,
            'current_deals': current_won_deals.count(),
            'current_leads': current_leads,
            'revenue_change': round(revenue_change, 1),
            'deals_change': round(deals_change, 1),
            'leads_change': round(leads_change, 1),
            'current_month': now.strftime('%B %Y'),
            'previous_month': prev_month_start.strftime('%B %Y')
        }
        
        return render_to_string('analytics/dash/kpi_metrics.html', context)
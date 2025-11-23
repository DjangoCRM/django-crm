"""
Analytics Dashboard Views - Custom Built-in Dashboard
"""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncDay
from datetime import datetime, timedelta
from decimal import Decimal

from crm.models import Deal, Lead, Contact, Request
from django.contrib.auth.models import User


@staff_member_required
def analytics_dashboard(request):
    """Main analytics dashboard view"""
    context = {
        'page_title': 'Analytics Dashboard',
        'dashboard_data': get_dashboard_data()
    }
    return render(request, 'analytics/dashboard.html', context)


@staff_member_required
def dashboard_api(request):
    """API endpoint for dashboard data"""
    return JsonResponse(get_dashboard_data())


def get_dashboard_data():
    """Get all dashboard data"""
    # Date ranges
    now = datetime.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_30_days = now - timedelta(days=30)
    
    # Previous month
    if now.month == 1:
        prev_month_start = now.replace(year=now.year-1, month=12, day=1)
        prev_month_end = current_month_start - timedelta(days=1)
    else:
        prev_month_start = now.replace(month=now.month-1, day=1)
        prev_month_end = current_month_start - timedelta(days=1)
    
    # Current period metrics
    current_deals = Deal.objects.filter(creation_date__gte=current_month_start)
    current_won_deals = current_deals.filter(stage__title__icontains='won')
    current_revenue = current_won_deals.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    current_leads = Lead.objects.filter(creation_date__gte=current_month_start).count()
    
    # Previous period metrics
    prev_deals = Deal.objects.filter(creation_date__range=[prev_month_start, prev_month_end])
    prev_won_deals = prev_deals.filter(stage__title__icontains='won')
    prev_revenue = prev_won_deals.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    prev_leads = Lead.objects.filter(creation_date__range=[prev_month_start, prev_month_end]).count()
    
    # Calculate changes
    def calculate_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return ((current - previous) / previous) * 100
    
    # Last 30 days overview
    deals_30_days = Deal.objects.filter(creation_date__date__gte=last_30_days)
    total_deals = deals_30_days.count()
    won_deals = deals_30_days.filter(stage__title__icontains='won').count()
    lost_deals = deals_30_days.filter(stage__title__icontains='lost').count()
    total_revenue_30 = deals_30_days.filter(stage__title__icontains='won').aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
    # Conversion rates
    win_rate = (won_deals / total_deals * 100) if total_deals > 0 else 0
    leads_30_days = Lead.objects.filter(creation_date__date__gte=last_30_days).count()
    converted_leads = Lead.objects.filter(creation_date__date__gte=last_30_days, contact__isnull=False).count()
    lead_conversion_rate = (converted_leads / leads_30_days * 100) if leads_30_days > 0 else 0
    
    # Monthly revenue chart (last 12 months)
    year_ago = now - timedelta(days=365)
    monthly_revenue = Deal.objects.filter(
        creation_date__date__gte=year_ago,
        stage__title__icontains='won'
    ).annotate(
        month=TruncMonth('creation_date')
    ).values('month').annotate(
        revenue=Sum('amount')
    ).order_by('month')
    
    # Lead sources
    lead_sources = Lead.objects.values('lead_source__name').annotate(
        count=Count('id'),
        converted=Count('id', filter=Q(contact__isnull=False))
    ).order_by('-count')[:10]
    
    # Sales funnel
    funnel_data = Deal.objects.values('stage__title').annotate(
        count=Count('id'),
        total_value=Sum('amount')
    ).order_by('stage__index')
    
    # Top performers (current month)
    top_by_deals = Deal.objects.filter(
        stage__title__icontains='won',
        creation_date__gte=current_month_start
    ).values('owner__first_name', 'owner__last_name').annotate(
        deals_count=Count('id'),
        total_revenue=Sum('amount')
    ).order_by('-deals_count')[:5]
    
    top_by_revenue = Deal.objects.filter(
        stage__title__icontains='won',
        creation_date__gte=current_month_start
    ).values('owner__first_name', 'owner__last_name').annotate(
        deals_count=Count('id'),
        total_revenue=Sum('amount')
    ).order_by('-total_revenue')[:5]
    
    # Recent activity
    recent_deals = Deal.objects.select_related('owner', 'contact', 'company').order_by('-creation_date')[:10]
    recent_leads = Lead.objects.select_related('owner', 'lead_source').order_by('-creation_date')[:10]
    recent_requests = Request.objects.select_related('owner', 'contact').order_by('-creation_date')[:10]
    
    return {
        'sales_overview': {
            'total_revenue': float(total_revenue_30),
            'total_deals': total_deals,
            'won_deals': won_deals,
            'lost_deals': lost_deals,
            'win_rate': round(win_rate, 1),
            'leads_count': leads_30_days,
            'converted_leads': converted_leads,
            'lead_conversion_rate': round(lead_conversion_rate, 1),
            'period_start': last_30_days.strftime('%Y-%m-%d'),
            'period_end': now.strftime('%Y-%m-%d'),
        },
        'kpi_metrics': {
            'current_revenue': float(current_revenue),
            'current_deals': current_won_deals.count(),
            'current_leads': current_leads,
            'revenue_change': round(calculate_change(float(current_revenue), float(prev_revenue)), 1),
            'deals_change': round(calculate_change(current_won_deals.count(), prev_won_deals.count()), 1),
            'leads_change': round(calculate_change(current_leads, prev_leads), 1),
            'current_month': current_month_start.strftime('%B %Y'),
            'previous_month': prev_month_start.strftime('%B %Y'),
        },
        'revenue_chart': {
            'labels': [item['month'].strftime('%b %Y') for item in monthly_revenue],
            'data': [float(item['revenue'] or 0) for item in monthly_revenue],
        },
        'lead_sources': {
            'sources': list(lead_sources),
            'total_leads': sum(item['count'] for item in lead_sources),
            'total_converted': sum(item['converted'] for item in lead_sources),
        },
        'sales_funnel': {
            'stages': list(funnel_data),
            'total_deals': Deal.objects.count(),
            'total_value': float(Deal.objects.aggregate(Sum('amount'))['amount__sum'] or 0),
        },
        'top_performers': {
            'by_deals': list(top_by_deals),
            'by_revenue': list(top_by_revenue),
            'month_name': current_month_start.strftime('%B %Y'),
        },
        'recent_activity': {
            'deals': [
                {
                    'id': deal.id,
                    'name': deal.name or f'Deal #{deal.id}',
                    'amount': float(deal.amount or 0),
                    'contact': deal.contact.full_name if deal.contact else None,
                    'company': deal.company.full_name if deal.company else None,
                    'owner': f'{deal.owner.first_name} {deal.owner.last_name}',
                    'stage': deal.stage.title if deal.stage else 'New',
                    'creation_date': deal.creation_date.isoformat(),
                }
                for deal in recent_deals
            ],
            'leads': [
                {
                    'id': lead.id,
                    'name': lead.full_name or f'Lead #{lead.id}',
                    'company': lead.company_name,
                    'email': lead.email,
                    'phone': lead.phone,
                    'owner': f'{lead.owner.first_name} {lead.owner.last_name}' if lead.owner else None,
                    'source': lead.lead_source.name if lead.lead_source else None,
                    'disqualified': lead.disqualified,
                    'was_in_touch': lead.was_in_touch,
                    'creation_date': lead.creation_date.isoformat(),
                }
                for lead in recent_leads
            ],
            'requests': [
                {
                    'id': request.id,
                    'subject': request.subject or f'Request #{request.id}',
                    'contact': request.contact.full_name if request.contact else None,
                    'owner': f'{request.owner.first_name} {request.owner.last_name}' if request.owner else None,
                    'creation_date': request.creation_date.isoformat(),
                }
                for request in recent_requests
            ],
        },
    }
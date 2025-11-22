# Frontend Integration Views

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from crm.models import Contact, Company, Deal, Lead
from tasks.models import Task
from common.models import UserProfile


@login_required
def dashboard_view(request):
    """Main dashboard view with clean design."""
    
    # Get current user's data
    user_profile = getattr(request.user, 'userprofile', None)
    
    # Calculate stats
    now = timezone.now()
    last_month = now - timedelta(days=30)
    
    # Base querysets (filter by user if needed)
    base_deals = Deal.objects.all()
    base_contacts = Contact.objects.all()
    base_companies = Company.objects.all()
    base_leads = Lead.objects.all()
    base_tasks = Task.objects.all()
    
    if user_profile and not request.user.is_superuser:
        base_deals = base_deals.filter(owner=request.user)
        base_contacts = base_contacts.filter(owner=request.user)
        base_companies = base_companies.filter(owner=request.user)
        base_leads = base_leads.filter(owner=request.user)
        base_tasks = base_tasks.filter(owner=request.user)
    
    # Current period stats
    active_deals = base_deals.filter(stage__name__icontains='active')
    total_revenue = base_deals.aggregate(total=Sum('amount'))['total'] or 0
    new_leads = base_leads.filter(created_at__gte=last_month)
    
    # Previous period for comparison
    prev_month = last_month - timedelta(days=30)
    prev_deals = base_deals.filter(created_at__lt=last_month, created_at__gte=prev_month)
    prev_revenue = prev_deals.aggregate(total=Sum('amount'))['total'] or 0
    prev_leads = base_leads.filter(created_at__lt=last_month, created_at__gte=prev_month)
    
    # Calculate changes
    revenue_change = 0
    if prev_revenue > 0:
        revenue_change = round(((total_revenue - prev_revenue) / prev_revenue) * 100, 1)
    
    deals_change = 0
    if prev_deals.count() > 0:
        deals_change = round(((active_deals.count() - prev_deals.count()) / prev_deals.count()) * 100, 1)
    
    leads_change = 0
    if prev_leads.count() > 0:
        leads_change = round(((new_leads.count() - prev_leads.count()) / prev_leads.count()) * 100, 1)
    
    # Conversion rate
    total_leads = base_leads.count()
    converted_leads = base_leads.filter(status='converted').count()
    conversion_rate = round((converted_leads / total_leads * 100), 1) if total_leads > 0 else 0
    
    prev_total_leads = prev_leads.count()
    prev_converted_leads = prev_leads.filter(status='converted').count()
    prev_conversion_rate = round((prev_converted_leads / prev_total_leads * 100), 1) if prev_total_leads > 0 else 0
    conversion_change = round(conversion_rate - prev_conversion_rate, 1)
    
    # Recent data
    recent_deals = base_deals.select_related('company', 'contact', 'stage').order_by('-created_at')[:5]
    
    # Mock recent activities (you might want to create an Activity model)
    recent_activities = []
    for deal in recent_deals[:3]:
        recent_activities.append({
            'title': f'Deal created: {deal.name}',
            'description': f'New deal worth ${deal.amount} was created',
            'created_at': deal.created_at,
        })
    
    # Navigation counts
    navigation_counts = {
        'contacts_count': base_contacts.count(),
        'companies_count': base_companies.count(),
        'deals_count': base_deals.count(),
        'leads_count': base_leads.count(),
        'tasks_count': base_tasks.filter(stage__name__icontains='active').count(),
        'messages_count': 0,  # You might integrate with chat app
    }
    
    context = {
        'stats': {
            'total_revenue': total_revenue,
            'revenue_change': revenue_change,
            'active_deals_count': active_deals.count(),
            'deals_change': deals_change,
            'new_leads_count': new_leads.count(),
            'leads_change': leads_change,
            'conversion_rate': conversion_rate,
            'conversion_change': conversion_change,
        },
        'recent_deals': recent_deals,
        'recent_activities': recent_activities,
        'breadcrumbs': [{'title': 'Dashboard', 'url': '#'}],
        **navigation_counts
    }
    
    return render(request, 'frontend/dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def dashboard_stats(request):
    """API endpoint for dashboard stats (for real-time updates)."""
    
    user_profile = getattr(request.user, 'userprofile', None)
    
    # Base querysets
    base_deals = Deal.objects.all()
    base_contacts = Contact.objects.all()
    base_companies = Company.objects.all()
    base_leads = Lead.objects.all()
    base_tasks = Task.objects.all()
    
    if user_profile and not request.user.is_superuser:
        base_deals = base_deals.filter(owner=request.user)
        base_contacts = base_contacts.filter(owner=request.user)
        base_companies = base_companies.filter(owner=request.user)
        base_leads = base_leads.filter(owner=request.user)
        base_tasks = base_tasks.filter(owner=request.user)
    
    stats = {
        'contactsCount': base_contacts.count(),
        'companiesCount': base_companies.count(),
        'dealsCount': base_deals.count(),
        'leadsCount': base_leads.count(),
        'tasksCount': base_tasks.filter(stage__name__icontains='active').count(),
    }
    
    return JsonResponse(stats)


@login_required
def dashboard_analytics(request):
    """HTMX view for analytics tab."""
    # This would contain analytics-specific data
    context = {
        'analytics_data': {
            'sales_trend': [100, 120, 115, 140, 160, 180, 195],
            'lead_sources': {
                'Website': 45,
                'Referral': 30,
                'Social Media': 15,
                'Direct': 10,
            }
        }
    }
    return render(request, 'frontend/dashboard_analytics.html', context)


@login_required
def dashboard_reports(request):
    """HTMX view for reports tab."""
    context = {
        'reports': [
            {'name': 'Sales Report', 'description': 'Monthly sales performance', 'url': '#'},
            {'name': 'Lead Report', 'description': 'Lead conversion analysis', 'url': '#'},
            {'name': 'Activity Report', 'description': 'Team activity summary', 'url': '#'},
        ]
    }
    return render(request, 'frontend/dashboard_reports.html', context)


@login_required
@require_http_methods(["GET"])
def search_global(request):
    """Global search endpoint."""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    user_profile = getattr(request.user, 'userprofile', None)
    results = []
    
    # Search contacts
    contacts_qs = Contact.objects.filter(
        first_name__icontains=query
    ) | Contact.objects.filter(
        last_name__icontains=query
    ) | Contact.objects.filter(
        email__icontains=query
    )
    
    if user_profile and not request.user.is_superuser:
        contacts_qs = contacts_qs.filter(owner=request.user)
    
    for contact in contacts_qs[:5]:
        results.append({
            'type': 'contact',
            'title': contact.full_name,
            'subtitle': contact.email,
            'url': f'/admin/crm/contact/{contact.id}/change/',
            'icon': '👤'
        })
    
    # Search companies
    companies_qs = Company.objects.filter(name__icontains=query)
    
    if user_profile and not request.user.is_superuser:
        companies_qs = companies_qs.filter(owner=request.user)
    
    for company in companies_qs[:5]:
        results.append({
            'type': 'company',
            'title': company.name,
            'subtitle': f'{company.industry or "Company"}',
            'url': f'/admin/crm/company/{company.id}/change/',
            'icon': '🏢'
        })
    
    # Search deals
    deals_qs = Deal.objects.filter(name__icontains=query)
    
    if user_profile and not request.user.is_superuser:
        deals_qs = deals_qs.filter(owner=request.user)
    
    for deal in deals_qs[:5]:
        results.append({
            'type': 'deal',
            'title': deal.name,
            'subtitle': f'${deal.amount} • {deal.stage.name if deal.stage else "No stage"}',
            'url': f'/admin/crm/deal/{deal.id}/change/',
            'icon': '📈'
        })
    
    return render(request, 'frontend/search_results.html', {'results': results})


@login_required
def quick_actions(request):
    """Quick actions modal content."""
    return render(request, 'frontend/quick_actions.html')


@login_required 
@require_http_methods(["GET"])
def dashboard_updates(request):
    """Real-time dashboard updates endpoint."""
    # This would typically check for new data and return updates
    # For now, just return success to maintain the polling
    return JsonResponse({'status': 'ok', 'timestamp': timezone.now().isoformat()})


# Error handlers with clean design
def handler404(request, exception):
    """Custom 404 page."""
    return render(request, 'frontend/errors/404.html', status=404)


def handler500(request):
    """Custom 500 page."""
    return render(request, 'frontend/errors/500.html', status=500)


def handler403(request, exception):
    """Custom 403 page.""" 
    return render(request, 'frontend/errors/403.html', status=403)
# 🚀 Django Dash Installation Instructions

## Current Status
✅ All files created and configured
✅ Settings updated
✅ URLs configured  
✅ Plugin registry ready

## Next Steps

### 1. Install django-dash package
```bash
# In your virtual environment:
pip install django-dash
```

### 2. Apply migrations
```bash
python manage.py migrate
```

### 3. Setup dashboard
```bash
python manage.py setup_dashboard --user admin --layout 2_col
```

### 4. Start server
```bash
python manage.py runserver
```

### 5. Access dashboard
Visit: `http://127.0.0.1:8000/admin/123/dash/`

## Troubleshooting

### If you get import errors:
1. Make sure django-dash is installed: `pip list | grep django-dash`
2. Check that all migrations are applied: `python manage.py migrate --check`
3. Verify user exists: `python manage.py createsuperuser` (if needed)

### If no plugins show:
```bash
python manage.py shell
>>> from dash.base import plugin_registry
>>> plugin_registry.get_plugins()
# Should show 7 plugins
```

### Alternative setup:
If the command fails, you can manually create a dashboard workspace in Django admin:
1. Go to `/admin/123/`
2. Find "Dashboard" section
3. Add new "Dashboard workspace"
4. Set layout to `layouts/2_col.html`
5. Add plugins manually

## What You'll Get

🎯 **7 Analytics Widgets:**
- Sales Overview (key metrics)
- Revenue Chart (monthly trends)  
- Lead Sources (source analysis)
- Sales Funnel (deal progression)
- KPI Metrics (period comparison)
- Top Performers (best sales reps)
- Recent Activity (latest CRM data)

🎨 **Modern Features:**
- Responsive design
- Interactive charts
- Auto-refresh
- Bootstrap 5 UI
- Mobile-friendly

## Support
- Check `analytics/DJANGO_DASH_INTEGRATION.md` for detailed documentation
- All plugin code is in `analytics/dash_plugins/crm_analytics_plugins.py`
- Templates are in `analytics/templates/analytics/dash/`
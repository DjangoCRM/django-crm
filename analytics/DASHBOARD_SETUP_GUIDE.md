# 🚀 Quick Setup Guide - Django Dash Analytics Dashboard

## 📋 Pre-requisites
- Django CRM running
- Admin access at `/admin/123/`
- Python environment ready

## ⚡ Quick Setup (3 steps)

### 1. Install django-dash
```bash
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

## 🎯 Access Dashboard

### URL:
```
http://127.0.0.1:8000/admin/123/dash/
```

### Navigation:
1. Login to admin: `/admin/123/`
2. Look for "DASHBOARD" section
3. Click "Dashboard workspaces" or "Analytics Dashboard"

## 📊 What You'll See

### 🎨 **7 Analytics Widgets:**
- 📈 **Sales Overview** - Key metrics and KPIs
- 💰 **Revenue Chart** - Monthly trends
- 🎯 **Lead Sources** - Source analysis 
- 🔄 **Sales Funnel** - Deal progression
- 🏆 **Top Performers** - Best sales reps
- 📋 **Recent Activity** - Latest CRM activities  
- 📊 **KPI Metrics** - Month-over-month comparison

### 📱 **3 Layout Options:**
- **1 Column** - Mobile/narrow screens
- **2 Columns** - Desktop (default)  
- **3 Columns** - Wide screens

## 🎛️ Customization

### Change Layout:
```bash
python manage.py setup_dashboard --layout 3_col
```

### Add Sample Data:
```bash
python manage.py loaddemo
```

## ✅ Verification

### Check if working:
1. Visit dashboard URL
2. See 7 widgets loaded
3. Charts display data
4. Links work to admin
5. Responsive on mobile

### Troubleshooting:
```bash
# Check plugins registered
python manage.py shell
>>> from dash.base import plugin_registry  
>>> len(plugin_registry.get_plugins())
# Should return 7

# Check database
python manage.py migrate --check
```

## 🎉 Done!

Your analytics dashboard is ready at:
**http://127.0.0.1:8000/admin/123/dash/**

### Features:
✅ Real-time analytics
✅ Responsive design  
✅ Interactive charts
✅ Modern UI
✅ Auto-refresh
✅ Mobile-friendly

### Next Steps:
- Explore different layouts
- Customize widget positions  
- Add more data for richer analytics
- Share dashboard with team

"""
Django Dash Plugin Registry for CRM Analytics
"""
from dash.base import plugin_registry
from .crm_analytics_plugins import (
    SalesOverviewPlugin,
    RevenueChartPlugin,
    LeadSourcesPlugin,
    SalesFunnelPlugin,
    TopPerformersPlugin,
    RecentActivityPlugin,
    KPIMetricsPlugin,
)

# Register all CRM analytics plugins
plugin_registry.register(SalesOverviewPlugin)
plugin_registry.register(RevenueChartPlugin)
plugin_registry.register(LeadSourcesPlugin)
plugin_registry.register(SalesFunnelPlugin)
plugin_registry.register(TopPerformersPlugin)
plugin_registry.register(RecentActivityPlugin)
plugin_registry.register(KPIMetricsPlugin)
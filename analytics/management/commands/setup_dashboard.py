"""
Management command to setup CRM Analytics Dashboard with django-dash
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dash.models import DashboardWorkspace, DashboardWorkspacePlugin
from dash.base import plugin_registry


class Command(BaseCommand):
    help = 'Setup CRM Analytics Dashboard with default layout and plugins'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username for dashboard owner (default: admin)',
            default='admin'
        )
        parser.add_argument(
            '--layout',
            type=str,
            help='Dashboard layout (default: 2_col)',
            choices=['1_col', '2_col', '3_col'],
            default='2_col'
        )

    def handle(self, *args, **options):
        username = options['user']
        layout = options['layout']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found. Please create user first.')
            )
            return

        # Create or get dashboard workspace
        workspace, created = DashboardWorkspace.objects.get_or_create(
            user=user,
            name='CRM Analytics Dashboard',
            defaults={
                'layout': f'layouts/{layout}.html',
                'is_public': False,
                'is_clonable': True,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created dashboard workspace for {username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Dashboard workspace for {username} already exists')
            )
            
        # Plugin configurations based on layout
        if layout == '2_col':
            plugin_configs = [
                ('sales_overview', 'main-1', 1),
                ('kpi_metrics', 'main-2', 2),
                ('revenue_chart', 'main-3', 3),
                ('top_performers', 'sidebar-1', 4),
                ('recent_activity', 'sidebar-2', 5),
                ('sales_funnel', 'sidebar-3', 6),
            ]
        elif layout == '3_col':
            plugin_configs = [
                ('kpi_metrics', 'left-1', 1),
                ('sales_overview', 'left-2', 2),
                ('revenue_chart', 'center-1', 3),
                ('lead_sources', 'center-2', 4),
                ('top_performers', 'right-1', 5),
                ('recent_activity', 'right-2', 6),
                ('sales_funnel', 'full-width', 7),
            ]
        else:  # 1_col
            plugin_configs = [
                ('kpi_metrics', 'main-1', 1),
                ('sales_overview', 'main-2', 2),
                ('revenue_chart', 'main-3', 3),
                ('sales_funnel', 'main-4', 4),
                ('lead_sources', 'main-5', 5),
                ('top_performers', 'main-6', 6),
            ]

        # Add plugins to workspace
        for plugin_name, placeholder, position in plugin_configs:
            plugin_class = None
            for registered_plugin in plugin_registry.get_plugins():
                if registered_plugin.name == plugin_name:
                    plugin_class = registered_plugin
                    break
            
            if plugin_class:
                plugin_obj, created = DashboardWorkspacePlugin.objects.get_or_create(
                    workspace=workspace,
                    plugin_uid=f'{plugin_class.__module__}.{plugin_class.__name__}',
                    defaults={
                        'placeholder_uid': placeholder,
                        'position': position,
                        'plugin_data': '{}',
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Added plugin: {plugin_name} to {placeholder}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Plugin {plugin_name} already exists')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Plugin {plugin_name} not found in registry')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDashboard setup complete!'
                f'\nAccess URL: /admin/123/dash/workspaces/{workspace.id}/'
                f'\nLayout: {layout}'
                f'\nPlugins: {len(plugin_configs)}'
            )
        )
        
        # Display available plugins
        self.stdout.write(self.style.SUCCESS('\nAvailable plugins:'))
        for plugin in plugin_registry.get_plugins():
            self.stdout.write(f'  - {plugin.name}: {plugin.title}')
            
        # Display helpful commands
        self.stdout.write(self.style.SUCCESS('\nUseful commands:'))
        self.stdout.write('  python manage.py runserver')
        self.stdout.write(f'  # Then visit: http://127.0.0.1:8000/admin/123/dash/workspaces/{workspace.id}/')
        self.stdout.write('  # Or: http://127.0.0.1:8000/admin/123/dash/')
        
        # Display sample data suggestion
        if not self._has_sample_data():
            self.stdout.write(
                self.style.WARNING(
                    '\nNo sample data found. Consider running:'
                    '\n  python manage.py loaddemo'
                    '\n  # This will populate the dashboard with sample data'
                )
            )

    def _has_sample_data(self):
        """Check if there's sample data in the system"""
        from crm.models import Deal, Lead
        return Deal.objects.count() > 0 or Lead.objects.count() > 0
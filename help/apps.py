from django.apps import AppConfig


class HelpConfig(AppConfig):
    name = 'help'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from help.dashboard import register_help_dashboard_providers

        register_help_dashboard_providers()

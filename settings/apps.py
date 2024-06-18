from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SettingsConfig(AppConfig):
    name = 'settings'
    label = 'settings'
    verbose_name = _('Settings')
    default_auto_field = 'django.db.models.AutoField'

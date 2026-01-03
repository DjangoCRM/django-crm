from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class QualityConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'quality'
    verbose_name = _('Transaction quality')
    label = 'quality'

from tendo.singleton import SingleInstanceException
from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AnalyticsConfig(AppConfig):
    name = 'analytics'
    label = 'analytics'
    verbose_name = _('Analytics')
    default_auto_field = 'django.db.models.AutoField'
    
    def ready(self):
        if not settings.TESTING:
            from analytics.utils.monthly_snapshot_saving import MonthlySnapshotSaving
            try:
                self.mss = MonthlySnapshotSaving()      # NOQA
                self.mss.start()
            except SingleInstanceException:
                pass

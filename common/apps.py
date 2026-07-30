from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from common.utils.worker_runtime import should_start_background_workers
from common.utils.worker_runtime import start_common_schedulers


class CommonConfig(AppConfig):
    name = 'common'
    verbose_name = _('Common')
    label = 'common'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from common.signals.handlers import user_creation_handler   # NOQA

        if not should_start_background_workers():
            return

        start_common_schedulers(self)

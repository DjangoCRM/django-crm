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
        from types import MethodType

        from django.contrib import admin

        from common.admin import register_shared_models_on_crm_site
        from common.dashboard import register_common_dashboard_providers
        from common.signals.handlers import user_creation_handler   # NOQA
        from common.site.crmsite import default_admin_index

        register_common_dashboard_providers()
        admin.site.index = MethodType(default_admin_index, admin.site)
        register_shared_models_on_crm_site()

        if not should_start_background_workers():
            return

        start_common_schedulers(self)

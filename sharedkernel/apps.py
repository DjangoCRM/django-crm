from django.apps import AppConfig


class SharedKernelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sharedkernel'
    verbose_name = 'Shared Kernel'

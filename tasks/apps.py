from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TasksConfig(AppConfig):
    name = 'tasks'
    label = 'tasks'
    verbose_name = _('Tasks')
    default_auto_field = 'django.db.models.AutoField'

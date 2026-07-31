"""Common dashboard counter providers."""

from django.utils.safestring import mark_safe

from common.models import Reminder
from common.models import UserProfile
from sharedkernel.dashboard import register_counter

icon_str = '<i class="material-icons" style="font-size: 17px;vertical-align: middle;">%s</i>'
alarm_icon = icon_str % 'alarm'
people_icon = icon_str % 'people'


def register_common_dashboard_providers() -> None:
    register_counter('common_model_icons', 10, 'common', apply_common_model_icons)


def apply_common_model_icons(request, models) -> None:
    del request
    _set_icon(Reminder, models, alarm_icon)
    _set_icon(UserProfile, models, people_icon)


def _set_icon(klass, models, icon) -> None:
    model_name = klass._meta.verbose_name_plural.capitalize()    # NOQA
    model = next((m for m in models if m['name'] == model_name), None)
    if model:
        model['name'] = mark_safe(f'{model_name} {icon}')

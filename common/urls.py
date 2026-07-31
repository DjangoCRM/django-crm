from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from common.views.debugs import debug
from common.views.reload_field import reload_field
from common.views.toggle_default_sorting import toggle_default_sorting

urlpatterns = [
    path(
        'debug/',
        login_required(debug),
        name='debug'
    ),
    path(
        "toggle-default-sorting",
        toggle_default_sorting,
        name="toggle_default_sorting"
    ),
    path(
        'reload-field/',
        login_required(reload_field),
        name='reload_field'
    ),
]

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from common.views.copy_department import copy_department
from common.views.debugs import debug
from common.views.reload_field import reload_field
from common.views.select_email_account import select_email_account
from common.views.select_emails_import import select_emails_import
from common.views.toggle_default_sorting import toggle_default_sorting
from common.views.user_transfer import user_transfer

urlpatterns = [
    path(
        'select-emails-import/request/',
        staff_member_required(select_emails_import),
        name='select_emails_import_request'
    ),
    path(
        'select-email-account/',
        staff_member_required(select_email_account),
        name='select_email_account'
    ),
    path(
        'user-transfer/',
        login_required(user_transfer),
        name='user_transfer'
    ),
    path(
        'copy-department/',
        login_required(copy_department),
        name='copy_department'
    ),
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

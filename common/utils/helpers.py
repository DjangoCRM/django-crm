import secrets
from django.contrib.auth import get_user_model

# Temporary compatibility re-exports — import from common.queries instead.
from common.queries import add_chat_context
from common.queries import add_phone_q_params
from common.queries import annotate_chat
from common.queries import get_active_users
from common.queries import get_department_id
from common.queries import get_manager_departments

# Temporary compatibility re-exports — import from sharedkernel.presentation instead.
from sharedkernel.presentation import CONTENT_COPY_ICON
from sharedkernel.presentation import CONTENT_COPY_LINK
from sharedkernel.presentation import COPY_STR
from sharedkernel.presentation import CRM_NOTICE
from sharedkernel.presentation import FRIDAY_SATURDAY_SUNDAY_MSG
from sharedkernel.presentation import LEADERS
from sharedkernel.presentation import OBJ_DOESNT_EXIT_STR
from sharedkernel.presentation import ONCLICK_STR
from sharedkernel.presentation import SAFE_ATTACH_FILE_ICON
from sharedkernel.presentation import SAFE_SUBJECT_ICON
from sharedkernel.presentation import get_formatted_short_date
from sharedkernel.presentation import get_verbose_name
from sharedkernel.presentation import popup_window

# Temporary compatibility re-exports — import from common.services instead.
from common.services.datetimes import get_delta_date
from common.services.datetimes import get_now
from common.services.datetimes import get_today
from common.services.messaging import compose_message
from common.services.messaging import compose_subject
from common.services.notifications import notify_admins_no_email
from common.services.notifications import save_message
from common.services.notifications import send_crm_email
from common.services.notifications import set_toggle_tooltip
from common.services.tokens import token_default
from common.services.translations import get_trans_for_lang
from common.services.translations import get_trans_for_user
from common.services.translations import get_user_language_code

USER_MODEL = get_user_model()

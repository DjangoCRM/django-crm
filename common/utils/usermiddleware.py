import zoneinfo
from django.apps import apps
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.contrib import messages
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

from common.models import UserProfile


class UserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            groups = request.user.groups.all()      
            set_user_timezone(profile)
            set_user_groups(request, groups)
            set_user_department(request, groups)
            iem = apps.get_app_config('crm')
            iem.import_emails(request.user)
            activate_stored_messages_to_user(request, profile)
            check_user_language(profile)
        return self.get_response(request)


def activate_stored_messages_to_user(request: WSGIRequest, profile: UserProfile) -> None:
    if profile.messages:
        while profile.messages:
            msg = mark_safe(profile.messages.pop(0))    # NOQA
            level = profile.messages.pop(0)             # NOQA
            messages.add_message(request, getattr(messages, level), msg)
        profile.save(update_fields=['messages'])


def check_user_language(profile: UserProfile) -> None:
    cur_language = get_language()
    if cur_language != profile.language_code:
        profile.language_code = cur_language
        profile.save(update_fields=['language_code'])


def set_user_department(request: WSGIRequest, groups) -> None:
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        if any((
            request.user.is_superuser,
            request.user.is_chief,
            request.user.is_superoperator,  # NOQA
            request.user.is_accountant      # NOQA
        )):
            if request.GET.get('department'):
                department_id = request.GET.get('department')
            else:
                department_id = request.session.get('department_id')
            if department_id and department_id != 'all':
                department_id = int(department_id)
                request.user.department_id = department_id
                request.session['department_id'] = department_id
            else:
                request.user.department_id = None
                request.session['department_id'] = None
        else:
            department = groups.filter(
                department__isnull=False
            ).first()
            request.user.department_id = department.id if department else None
            request.user.is_chief = False


def set_user_groups(request: WSGIRequest, groups) -> None:
    group_names = groups.values_list('name', flat=True)
    request.user.is_superoperator = 'superoperators' in group_names
    request.user.is_operator = 'operators' in group_names
    request.user.is_chief = 'chiefs' in group_names
    request.user.is_manager = 'managers' in group_names
    request.user.is_accountant = 'accountants' in group_names
    request.user.is_task_operator = 'task_operators' in group_names
    request.user.is_department_head = 'department heads' in group_names

    if request.user.is_operator:
        departments = groups.filter(department__isnull=False).count()
        if departments > 1:
            request.user.is_superoperator = True
            request.user.is_operator = False
    

def set_user_timezone(profile: UserProfile) -> None:
    utc_timezone = getattr(profile, 'utc_timezone', None)  
    if settings.USE_TZ and utc_timezone:
        if profile.activate_timezone:
            timezone.activate(
                zoneinfo.ZoneInfo(profile.utc_timezone)
            )
        else:
            timezone.deactivate()

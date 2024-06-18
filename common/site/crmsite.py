from django.conf import settings
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.admin.utils import quote
from django.db.models import Count
from django.db.models import Q
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch
from django.urls import reverse
from django.utils.timezone import localtime, now
from django.utils.translation import get_language
from django.utils.safestring import mark_safe

from common.models import Reminder, UserProfile
from common.utils.hide_main_tasks import hide_main_tasks
from common.utils.helpers import LEADERS
from crm.models import CrmEmail
from crm.models import Request
from help.models import Page
from tasks.models import Memo
from tasks.models import Task

icon_str = '<i class="material-icons" style="font-size: 17px;vertical-align: middle;">%s</i>'
alarm_icon = icon_str % 'alarm'
people_icon = icon_str % 'people'

admin.site.empty_value_display = LEADERS
admin.site.site_header = settings.ADMIN_HEADER
admin.site.site_title = settings.ADMIN_TITLE
admin.site.index_title = settings.INDEX_TITLE


def get_url(name: str):

    def get_admin_url(self):
        """
        Return the admin URL to edit the object represented by this log entry.
        """
        if self.content_type and self.object_id:
            url_name = name % (self.content_type.app_label, self.content_type.model)
            try:
                return reverse(url_name, args=(quote(self.object_id),))
            except NoReverseMatch:
                pass
        return None

    return get_admin_url


def index(self, request, extra_context=None):
    LogEntry.get_admin_url = get_url('admin:%s_%s_change')
    app_list = self.get_app_list(request)
    context = {
        **self.each_context(request),
        'title': self.index_title,
        'app_list': app_list,
        **(extra_context or {}),
    }
    request.current_app = self.name

    return TemplateResponse(
        request,
        self.index_template or 'admin/index.html',
        context
    )


admin.AdminSite.index = index


class BaseSite(admin.AdminSite):
    site_header = settings.PROJECT_NAME
    index_title = settings.INDEX_TITLE
    site_title = settings.SITE_TITLE
    site_url = None
    final_catch_all_view = False

    # -- AdminSite methods -- #

    def index(self, request, extra_context=None):
        LogEntry.get_admin_url = get_url('site:%s_%s_change')
        app_list = []
        app_dict = self._build_app_dict(request)
        for app_label in settings.APP_ON_INDEX_PAGE:
            app = next((
                app for app in app_dict.values()
                if app['app_label'] == app_label),
                None
            )
            if app:
                app_list.append(app)
                get_counters(request, app_label, app['models'])

                if app_label in settings.MODEL_ON_INDEX_PAGE:
                    set_app_models(app, app_label)
                else:
                    app['models'].sort(key=lambda x: x['name'])

        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            **(extra_context or {}),
        }
        request.current_app = self.name

        return TemplateResponse(
            request,
            self.index_template or 'admin/index.html',
            context
        )
    
    def app_index(self, request, app_label, extra_context=None):
        extra_context = extra_context or {}
        app_dict = self._build_app_dict(request, app_label)
        app_dict = app_dict.get(app_label)
        app_dict['models'].sort(key=lambda x: x['name'])
        extra_context["app_list"] = [app_dict]
        get_counters(request, app_label, app_dict['models'])

        return super().app_index(request, app_label, extra_context)

    def each_context(self, request):
        help_url = get_help_url(request)
        context = super().each_context(request)
        context['help_url'] = help_url
        app_list = []
        for app_label in settings.APP_ON_INDEX_PAGE:
            app = next((
                app for app in context['available_apps']
                if app['app_label'] == app_label),
                None
            )
            if app:
                app_list.append(app)
                get_counters(request, app_label, app['models'])
        context['available_apps'] = app_list

        # This is copyright information. Please don't change it!
        context['copyright_string'] = settings.COPYRIGHT_STRING
        context['project_site'] = settings.PROJECT_SITE

        return context

# -- custom methods-- #


def get_counters(request, app_label, models):
    if app_label == 'crm':
        if any((
            request.user.is_manager,
            request.user.is_operator,
            request.user.is_superoperator,
            request.user.is_superuser,
            request.user.is_chief,
        )):
            get_outbox_email_count(request, models)
            get_request_count(request, models)

    elif app_label == 'tasks':
        get_task_count(request, models)
        get_memo_count(request, models)

    elif app_label == 'common':
        set_icon(Reminder, models, alarm_icon)
        set_icon(UserProfile, models, people_icon)


def get_outbox_email_count(request, models):
    outbox_count = CrmEmail.objects.filter(
        owner=request.user,
        sent=False, 
        incoming=False, 
        trash=False
    ).count()
    if outbox_count:
        model_name = CrmEmail._meta.verbose_name_plural
        post = next((m for m in models if m['name'] == model_name), None)
        if post:
            post['name'] = mark_safe(
                f"{model_name}: "
                f"<span style='color: var(--error-fg)'>outbox ({outbox_count})</span>"
            )


def get_memo_count(request, models):
    memo_count = Memo.objects.filter(
        stage=Memo.PENDING,
        to=request.user,
    ).count()
    if memo_count:
        model_name = Memo._meta.verbose_name_plural
        memo = next((
            m for m in models
            if m['name'] == model_name),
            None
        )
        memo['name'] = mark_safe(
            f"{model_name} "
            f"(<span style='color: var(--error-fg)'>{memo_count}</span>)"
        )


def get_request_count(request, models):
    today = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
    qs = Request.objects.filter(pending=True)
    q_params = Q()
    if any((
        request.user.is_operator,
        request.user.is_superoperator,
        request.user.is_superuser,
        request.user.is_chief,
    )):
        q_params = Q(owner__groups__name__in=('superoperators', 'operators'))
        q_params |= Q(owner__isnull=True)
        if request.user.department_id:
            qs = qs.filter(department_id=request.user.department_id)
    elif request.user.is_manager:
        q_params = Q(owner=request.user) | Q(co_owner=request.user)

    counts = qs.filter(q_params).aggregate(
        regular=Count('pk', filter=Q(creation_date__gte=today)),
        urgent=Count('pk', filter=Q(creation_date__lt=today))
    )
    if counts['urgent'] or counts['regular']:
        set_counters(Request, models, counts)


def get_task_count(request, models):
    today = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
    qs = Task.objects.filter(
        stage__active=True,
        responsible=request.user,
    )
    qs = hide_main_tasks(request, qs)
    counts = qs.aggregate(
        regular=Count('pk', filter=Q(next_step_date__isnull=True) | Q(next_step_date__gte=today)),
        urgent=Count('pk', filter=Q(next_step_date__isnull=False) & Q(next_step_date__lt=today))
    )
    if counts['urgent'] or counts['regular']:
        set_counters(Task, models, counts)


def set_app_models(app: dict, app_label: str) -> None:
    models = []
    for object_name in settings.MODEL_ON_INDEX_PAGE[app_label]['app_model_list']:
        model = next((
            model for model in app['models']
            if model['object_name'] == object_name),
            None
        )
        if model:
            models.append(model)
    app['models'] = models
    app['name'] = mark_safe(f"{app['name']} &ldca;")


def set_icon(klass, models, icon) -> None:
    model_name = klass._meta.verbose_name_plural.capitalize()    # NOQA
    model = next((m for m in models if m['name'] == model_name), None)
    if model:
        model['name'] = mark_safe(f'{model_name} {icon}')


def set_counters(model, models, counts):
    model_name = model._meta.verbose_name_plural.capitalize()    # NOQA
    model = next((m for m in models if m['name'] == model_name), None)
    if counts['urgent'] and counts['regular']:
        model['name'] = mark_safe(
            f"{model_name} "
            f"(<span style='color: var(--error-fg)'>{counts['urgent']}</span>"
            f" + {counts['regular']})"
        )
    elif counts['regular']:
        model['name'] = mark_safe(
            f"{model_name} ({counts['regular']})"
        )
    elif counts['urgent']:
        model['name'] = mark_safe(
            f"{model_name} "
            f"(<span style='color: var(--error-fg)'>{counts['urgent']}</span>)"
        )


def get_help_url(request):
    help_url = app_label = model = page = ''  # index/home page
    index_url = reverse('site:index')
    path = request.path_info.replace(index_url, '').split('?')
    if path[0]:
        params = path[0].split('/')
        app_label = params[0]
        if app_label:
            try:
                model = params[1]  # page of model
                if model:
                    model = model.title()
                    page = 'l'
                    if params[2] or app_label == 'analytics':
                        page = 'i'
            except IndexError:
                pass  # page of app
    page = Page.objects.filter(
        app_label=app_label,
        model=model,
        page=page,
        language_code=get_language(),
        main=True  # always true
    ).first()
    if page:
        help_url = page.get_url(request.user)
    return help_url

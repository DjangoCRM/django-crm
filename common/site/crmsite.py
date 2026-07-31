from django.conf import settings
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

from common.site.help_url_data import HELP_URLS
from sharedkernel.dashboard import apply_dashboard_counters
from sharedkernel.dashboard import resolve_help_url
from sharedkernel.presentation import LEADERS

admin.site.empty_value_display = LEADERS
admin.site.site_header = settings.ADMIN_HEADER
admin.site.site_title = settings.ADMIN_TITLE
admin.site.index_title = settings.INDEX_TITLE


def default_admin_index(self, request, extra_context=None):
    """Explicit index handler for the default Django admin site."""
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
        context,
    )


class BaseSite(admin.AdminSite):
    site_header = settings.PROJECT_NAME
    index_title = settings.INDEX_TITLE
    site_title = settings.SITE_TITLE
    site_url = None
    final_catch_all_view = False

    # -- AdminSite methods -- #

    def index(self, request, extra_context=None):
        app_list = []
        app_dict = self._build_app_dict(request)
        for app_label in settings.APP_ON_INDEX_PAGE:
            app = next((
                app for app in app_dict.values()
                if app['app_label'] == app_label),
                None
            )
            if app:
                if app_label in settings.MODEL_ON_INDEX_PAGE:
                    app = set_app_models(app, app_label)
                else:
                    app['models'].sort(key=lambda x: x['name'])
                app_list.append(app)
                apply_dashboard_counters(request, app_label, app['models'])

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
        apply_dashboard_counters(request, app_label, app_dict['models'])

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
                apply_dashboard_counters(request, app_label, app['models'])
        context['available_apps'] = app_list

        # This is copyright information. Please don't change it!
        context['copyright_string'] = settings.COPYRIGHT_STRING
        context['project_site'] = settings.PROJECT_SITE

        return context

# -- custom methods-- #


def set_app_models(app: dict, app_label: str) -> dict:
    models = []
    for object_name in settings.MODEL_ON_INDEX_PAGE[app_label]['app_model_list']:
        model = next((
            model for model in app['models']
            if model['object_name'] == object_name),
            None
        )
        if model:
            models.append(model)

    updated_app = dict(app)
    updated_app['models'] = models
    updated_app['name'] = mark_safe(f"{updated_app['name']} &ldca;")
    return updated_app


def get_help_url(request) -> str:
    if getattr(settings, 'WEB_HELP', False):
        return _web_help_url(request)
    return resolve_help_url(request)


def _web_help_url(request) -> str:
    """Resolve static web-help URLs without importing help models."""
    help_url = app_label = model = page_type = ''
    index_url = reverse('site:index')
    path = request.path_info.replace(index_url, '').split('?')
    if path[0]:
        params = path[0].split('/')
        app_label = params[0]
        if app_label:
            try:
                model = params[1]
                if model:
                    page_type = 'l'
                    if params[2]:
                        if 'add' in params:
                            page_type = 'a'
                        elif 'delete' in params:
                            page_type = 'd'
                        else:
                            page_type = 'i'
            except IndexError:
                pass
    params = f"/{app_label}/{model}/{page_type}/"
    key = f"{get_language()}{params}"
    key_default = f"{settings.LANGUAGE_CODE}{params}"
    key_en = f"en{params}"
    return HELP_URLS.get(key) or HELP_URLS.get(
        key_default,
    ) or HELP_URLS.get(key_en, '')


# Backward-compatible alias for existing tests.
def get_url(name: str):
    from sharedkernel.admin_urls import resolve_log_entry_admin_url

    def get_admin_url(self):
        return resolve_log_entry_admin_url(self, name)

    return get_admin_url

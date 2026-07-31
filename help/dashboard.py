"""Help dashboard providers."""

from django.conf import settings
from django.urls import reverse
from django.utils.translation import get_language

from help.models import Page
from sharedkernel.dashboard import register_help_url_provider


def register_help_dashboard_providers() -> None:
    register_help_url_provider(resolve_help_url)


def resolve_help_url(request) -> str:
    if getattr(settings, 'WEB_HELP', False):
        return ''
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
                    model = model.title()
                    page_type = 'l'
                    if params[2] or app_label == 'analytics':
                        page_type = 'i'
            except IndexError:
                pass
    page = Page.objects.filter(
        app_label=app_label,
        model=model,
        page=page_type,
        main=True,
    ).filter(language_code__in=[get_language(), 'en']).first()
    if page:
        return page.get_url(request.user)
    return ''

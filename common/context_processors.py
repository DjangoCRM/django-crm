from django.conf import settings


def favicon_debug(request):
    return {'favicon_debug': settings.DEBUG}

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.handlers.wsgi import WSGIRequest
from urllib.parse import urlparse


def secure_url(url: str, request: WSGIRequest) -> str:
    """
    Checks the domain and scheme of an absolute url.
    If the domain is alien, returns the URL of the index page.
    """
    scheme, netloc, _, _, _, _ = urlparse(url)
    if netloc:
        site = Site.objects.get_current()
        domain = site.domain
        if netloc != domain:
            return '/'
        
        if scheme == 'http':
            if not settings.TESTING:
                # the testing request factory always uses http
                if scheme != request.scheme:
                    url = 'https' + url[4:]

    return url
 

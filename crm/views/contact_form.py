from geoip2.errors import AddressNotFoundError
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.gis.geoip2 import GeoIP2Exception
from django.contrib.sites.models import Site
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from crm.forms.contact_form import ContactForm
from crm.models import LeadSource
from crm.utils.create_form_request import create_form_request
from crm.utils.helpers import is_company_banned


# csrf_exempt decorator marks the view as being exempt
# from the protection ensured by the CsrfViewMiddleware.
# An alternative to this would be to set CSRF_COOKIE_SAMESITE='None'
# and CSRF_COOKIE_SECURE=True in the settings.


@xframe_options_exempt
@csrf_exempt
def contact_form(request, uuid):
    lead_source = get_object_or_404(LeadSource, uuid=uuid)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if not is_company_banned(data):
                if settings.GEOIP:
                    get_country_and_city(request, data)
                create_form_request(lead_source, form)
            template = lead_source.success_template
            thanks_message = _("Dear {}, thanks for your request!").format(data['name'])
            response = render(request, template, {"msg": thanks_message})
            return response
    else:
        form = ContactForm(initial={'leadsource_token': uuid})
    template = lead_source.form_template
    site = Site.objects.get_current()
    uri = reverse('contact_form', args=(uuid,))
    scheme = 'http' if settings.DEBUG else 'https'
    request_url = f"{scheme}://{site.domain}{uri}"
    context = {'form': form, "request_url": request_url}
    if settings.GOOGLE_RECAPTCHA_SITE_KEY:
        context['recaptcha_site_key'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    response = render(request, template, context)
    return response


def get_country_and_city(request: WSGIRequest, data: dict) -> str:
    err = ''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    if ip:
        try:
            g = GeoIP2()
            city = g.city(ip)
            city_name = city.get('city')    # can be None
            data['city'] = city_name if city_name else ''
            data['country'] = city.get('country_name')
            if not data['country']:
                data['country'] = g.country(ip).get('country_name')
        except (GeoIP2Exception, AddressNotFoundError) as e:
            err = e
    return err

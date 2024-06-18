from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from common.utils.helpers import send_crm_email
from crm.forms.contact_form import ContactForm
from crm.models import LeadSource
from crm.utils.create_form_request import create_form_request
from crm.utils.helpers import is_company_banned


@csrf_exempt
def add_request(request):
    if not request.method == "POST":
        return HttpResponse(status=405)   # 405 Method Not Allowed
    form = ContactForm(request.POST)
    if not form.is_valid():
        subj = " Invalid request form data from the site."
        send_mail_admins(request, subj, form)
        return HttpResponse(status=409)

    data = form.cleaned_data
    if is_company_banned(data):
        return HttpResponse(status=200)
    token = str(data['leadsource_token'])
    try:
        lead_source = LeadSource.objects.get(uuid=token)
    except ObjectDoesNotExist:
        subj = " Unauthorized  request from site form."
        send_mail_admins(request, subj)
        return HttpResponse(status=401)
    create_form_request(lead_source, form)
    return HttpResponse(status=200)


def send_mail_admins(request, subj, form: ContactForm = None):
    body = subj + '<br><br>POST:<br>'
    for k, v in request.POST.items():
        body += k + ': ' + v + '<br>'
    if form:
        body += f"<br>Form errors: <br>{form.errors.as_json()}"
    send_crm_email(subj, body, [adr[1] for adr in settings.ADMINS])

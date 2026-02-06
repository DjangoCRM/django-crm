from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _

from crm.models import Request
from crm.site.crmadminsite import crm_site
from massmail.forms.radio_select_form import RadioSelectForm
from massmail.models import EmailAccount


def select_email_account(request: WSGIRequest):
    if request.method == "POST":
        ea_id = request.POST.get('choice')
        url = reverse('select_emails_import_request') + f"?ea={ea_id}"
        params = request.GET.copy()
        del params['eas']
        return HttpResponseRedirect(url + f'&{params.urlencode()}')

    else:
        ids_str = request.GET.get('eas')
        ids = ids_str.split(',')
        eas = EmailAccount.objects.filter(
            id__in=ids
        ).distinct().order_by('name').values_list('id', 'name')
        form = RadioSelectForm(eas)
        extra_context = dict(
            crm_site.each_context(request),
            opts=Request._meta,  # NOQA
            title=_("Please select an Email account"),
            form=form
        )

    return render(request, 'common/select_object.html', extra_context)

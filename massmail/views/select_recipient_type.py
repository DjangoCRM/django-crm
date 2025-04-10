from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.urls import reverse
from crm.models import Contact
from crm.models import Company
from crm.models import Lead
from crm.site.crmadminsite import crm_site
from massmail.forms.radio_select_form import RadioSelectForm
from massmail.models import MailingOut


CHOICES = (
    (1, Contact._meta.verbose_name_plural),     # NOQA
    (2, Company._meta.verbose_name_plural),     # NOQA
    (3, Lead._meta.verbose_name_plural),        # NOQA
)


def select_recipient_type(request: WSGIRequest):
    if request.method == "POST":
        value = request.POST.get('choice')
        if value == '1':
            url = reverse('site:contact_make_massmail')
        elif value == '2':
            url = reverse('site:company_make_massmail')
        elif value == '3':
            messages.warning(request, _("Use the 'Action' menu."))
            url = reverse('site:crm_lead_changelist')
        return HttpResponseRedirect(url)

    else:
        form = RadioSelectForm(CHOICES)
        extra_context = dict(
            crm_site.each_context(request),
            opts=MailingOut._meta,     # NOQA
            title=_("Please select the type of recipients"),
            form=form
        )            

    return render(request, 'common/select_object.html', extra_context)

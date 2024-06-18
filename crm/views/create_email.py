import os
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.template.response import TemplateResponse
from django.utils.http import urlencode
from django.utils.translation import gettext as _

from common.models import TheFile
from common.utils.helpers import get_department_id
from crm.forms.add_files_form import AddFilesForm
from crm.models import CrmEmail
from crm.utils.ticketproc import get_ticket_str
from crm.site.crmadminsite import crm_site
from crm.settings import KEEP_TICKET
from massmail.models import EmailAccount
from massmail.models import Signature


def create_email(request, **kwargs):
    """Used to create an email on page of Contact, Deal, Lead, Company"""
    subject = content = ''
    fl, deal = [], None
    data = request.GET.dict()
    content_type = ContentType.objects.get(
        app_label='crm', model=data.get('object')
    )
    if data.get('object') == 'deal':
        deal = content_type.model_class().objects.get(id=kwargs['object_id'])
        subject = 'Re: ' + deal.name
        content = KEEP_TICKET % deal.ticket
        recipient = getattr(deal, data.get('recipient'))
        if not recipient:
            messages.error(request, _('No recipient'))
            return HttpResponseRedirect(request.get_full_path())
        fls = deal.files.all()
        if fls:
            fl = []
            for f in fls:
                fl.append(f.file)
            if fl and not request.method == 'POST':
                form = AddFilesForm(fl)
                context = dict(
                    crm_site.each_context(request),
                    opts=deal._meta,                # NOQA
                    app_label=deal._meta.app_label, # NOQA
                    original=deal,
                    form=form,
                )
                return TemplateResponse(
                    request, "crm/addfiles.html", context
                )
        if data.get('recipient') == 'partner_contact':
            data['recipient'] = 'contact'
    else:
        recipient = content_type.model_class(
        ).objects.get(id=kwargs['object_id'])
    signature_id = Signature.objects.filter(
        owner=request.user, default=True).values_list('id', flat=True).first()
    ea = EmailAccount.objects.filter(owner=request.user, main=True).first()
    params = {
        'from_field': ea.from_email if ea else '',
        'to': recipient.email,
        f"{data.get('recipient')}_id": recipient.id,
    }
    if deal:
        params['deal_id'] = deal.id
        params['ticket'] = deal.ticket
        params['content'] = content
        params['subject'] = subject
        if deal.request:
            params['request_id'] = deal.request_id
    if signature_id:
        params['signature_id'] = signature_id
    if not fl and request.method == 'GET':
        return HttpResponseRedirect(reverse(
            'site:crm_crmemail_add'
        ) + f"?{urlencode(params)}")

    if deal:
        params['subject'] = params['subject'] + get_ticket_str(deal.ticket)

    department_id = None
    if recipient.owner:
        department_id = get_department_id(recipient.owner)
    elif request.user.department_id:                    # NOQA
        department_id = request.user.department_id      # NOQA
    params['department_id'] = department_id
    params['owner'] = request.user
    eml = CrmEmail.objects.create(**params)
    if fl and request.method == 'POST':
        post_data = request.POST.copy()
        post_data.pop('csrfmiddlewaretoken')
        fnl = list(post_data.keys())
        for i in range(len(fnl)):
            file = next(
                f for f in fl if f.path.split(os.sep)[-1] == fnl[i - 1]
            )
            x = TheFile(
                file=file,
                content_object=eml
            )
            x.save()
    return HttpResponseRedirect(
        reverse('site:crm_crmemail_change', args=(eml.id,))
    )

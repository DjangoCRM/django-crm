from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from crm.models import Company
from crm.models import Contact
from crm.models import Lead
from massmail.models import MailingOut
from crm.site.crmadminsite import crm_site
from common.utils.permissions import object_not_found_response


def got_company_massmails(request, object_id):
    return got_massmails(
        request,
        object_id,
        ContentType.objects.get_for_model(Company)
    )


def got_contacts_massmails(request, object_id):
    return got_massmails(
        request,
        object_id,
        ContentType.objects.get_for_model(Contact)
    )


def got_leads_massmails(request, object_id):
    return got_massmails(
        request,
        object_id,
        ContentType.objects.get_for_model(Lead)
    )


def got_massmails(request, object_id, CONTENT_TYPE):
    model = CONTENT_TYPE.model_class()
    model_admin = crm_site._registry[model]
    obj = model_admin.get_queryset(request).filter(pk=object_id).first()
    if not obj or not model_admin.has_view_permission(request, obj):
        return object_not_found_response(request, model_admin, object_id)

    msgs = [0]
    mailingout_admin = crm_site._registry[MailingOut]
    mcs = mailingout_admin.get_queryset(request).filter(
        content_type=CONTENT_TYPE
    )
    for mc in mcs:
        successful_ids = mc.get_successful_ids()
        if object_id in successful_ids:
            msgs.append(mc.message_id)
    url = reverse('site:massmail_emlmessage_changelist') + f'?id__in={",".join(map(str, msgs))}'
    return HttpResponseRedirect(url)            
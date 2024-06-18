from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from crm.models import Company
from crm.models import Contact
from crm.models import Lead
from massmail.models import MailingOut


def got_company_massmails(request, object_id):
    return got_massmails(
        object_id,
        ContentType.objects.get_for_model(Company)
    )


def got_contacts_massmails(request, object_id):
    return got_massmails(
        object_id,
        ContentType.objects.get_for_model(Contact)
    )


def got_leads_massmails(request, object_id):
    return got_massmails(
        object_id,
        ContentType.objects.get_for_model(Lead)
    )


def got_massmails(object_id, CONTENT_TYPE):
    msgs = [0]
    mcs = MailingOut.objects.filter(content_type=CONTENT_TYPE)
    for mc in mcs:
        successful_ids = mc.get_successful_ids()
        if object_id in successful_ids:
            msgs.append(mc.message_id)
    url = reverse('site:massmail_emlmessage_changelist') + f'?id__in={",".join(map(str, msgs))}'
    return HttpResponseRedirect(url)            
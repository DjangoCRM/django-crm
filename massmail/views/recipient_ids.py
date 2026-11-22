from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from crm.site.crmadminsite import crm_site
from common.utils.permissions import object_not_found_response
from massmail.models import MailingOut


def view_recipient_ids(request, object_id, method):
    data = {
        ContentType.objects.get(app_label="crm", model="contact").id: 'site:crm_contact_changelist',
        ContentType.objects.get(app_label="crm", model="company").id: 'site:crm_company_changelist',
        ContentType.objects.get(app_label="crm", model="lead").id: 'site:crm_lead_changelist',
    }
    mailingout_admin = crm_site._registry[MailingOut]
    mo = mailingout_admin.get_queryset(request).filter(pk=object_id).first()
    if not mo or not mailingout_admin.has_view_permission(request, mo):
        return object_not_found_response(request, mailingout_admin, object_id)
    get_particular_ids = getattr(mo, method)
    l_ids = get_particular_ids()
    url = reverse(data[mo.content_type_id]) + '?id__in=' + '%s' % ",".join(map(str, l_ids))
    return HttpResponseRedirect(url)

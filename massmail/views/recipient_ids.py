from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType

from massmail.models import MailingOut


def view_recipient_ids(_, object_id, method):
    data = {
        ContentType.objects.get(app_label="crm", model="contact").id: 'site:crm_contact_changelist',
        ContentType.objects.get(app_label="crm", model="company").id: 'site:crm_company_changelist',
        ContentType.objects.get(app_label="crm", model="lead").id: 'site:crm_lead_changelist',
    }
    mo = MailingOut.objects.get(id=object_id)
    get_particular_ids = getattr(mo, method)
    l_ids = get_particular_ids()
    url = reverse(data[mo.content_type_id]) + '?id__in=' + '%s' % ",".join(map(str, l_ids))
    return HttpResponseRedirect(url)

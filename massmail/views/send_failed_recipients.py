from django.contrib import messages
from massmail.models import MailingOut
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from crm.site.crmadminsite import crm_site
from common.utils.permissions import object_not_found_response


def send_failed_recipients(request, object_id):
    mailingout_admin = crm_site._registry[MailingOut]
    mo = mailingout_admin.get_queryset(request).filter(pk=object_id).first()
    if not mo or not mailingout_admin.has_change_permission(request, mo):
        return object_not_found_response(request, mailingout_admin, object_id)
    mo.status = 'A'
    mo.move_to_recipient_ids()
    messages.success(
            request, 
            _('Failed recipients has been returned to the massmail successfully.')
    )    
    return HttpResponseRedirect(reverse('site:massmail_mailingout_changelist'))      
    
    
    
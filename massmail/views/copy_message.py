from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from crm.site.crmadminsite import crm_site
from common.utils.permissions import object_not_found_response
from massmail.models import EmlMessage, Signature


def copy_message(request, object_id):
    message_admin = crm_site._registry[EmlMessage]
    msg = message_admin.get_queryset(request).filter(pk=object_id).first()
    if not msg or not message_admin.has_view_permission(request, msg):
        return object_not_found_response(request, message_admin, object_id)
    if not message_admin.has_add_permission(request):
        raise PermissionDenied
    try:
        signature = Signature.objects.get(
            owner=request.user,
            default=True
        )
        msg.signature = signature
    except Signature.DoesNotExist:
        msg.signature = None
    msg.id = None
    msg.owner = request.user
    msg.save()
    url = reverse(
        'site:massmail_emlmessage_change',
        args=(msg.id,)
    )
    return HttpResponseRedirect(url) 

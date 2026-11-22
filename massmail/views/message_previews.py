from django.http import HttpResponse
from django.template import RequestContext
from django.template import Template
from crm.site.crmadminsite import crm_site
from massmail.models import EmlMessage
from settings.models import MassmailSettings
from common.utils.permissions import object_not_found_response


def message_preview(request, message_id):
    message_admin = crm_site._registry[EmlMessage]
    message = message_admin.get_queryset(request).filter(pk=message_id).first()
    if not message or not message_admin.has_view_permission(request, message):
        return object_not_found_response(request, message_admin, message_id)
    signature = message.signature
    signature_content = signature.content if signature else ''
    content = f"""
    {{% load mailbuilder %}}
    SUBJECT: {message.subject}<br>
    {message.content}<br>
    {signature_content}
    """
    unsubscribe_url = MassmailSettings.objects.get(pk=1).unsubscribe_url
    context = RequestContext(
        request,
        {
            'first_name': message.owner.username,
            'unsubscribe_url':unsubscribe_url,
            'preview': True
        }
    )
    template = Template(content)
    try:
        return HttpResponse(template.render(context))
    except FileNotFoundError:
        return HttpResponse("[Errno 2] No file or directory.")
    except Exception:
        return HttpResponse("Error rendering template.")

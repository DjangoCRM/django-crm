from django.http import HttpResponse
from django.template import RequestContext
from django.template import Template

from massmail.models import EmlMessage
from settings.models import MassmailSettings


def message_preview(request, message_id):
    
    message = EmlMessage.objects.get(id=message_id)
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

    return HttpResponse(template.render(context)) 

from django.http import HttpResponse
from massmail.models import EmlMessage
from django.template import RequestContext, Template


def message_preview(request, message_id):
    
    message = EmlMessage.objects.get(id=message_id)
    signature = message.signature
    signature_content = signature.content if signature else ''
    content = "{% load mailbuilder %}"
    content = f"""
    {content} 
    SUBJECT: {message.subject}<br>
    {message.content}<br>
    {signature_content}
    """
    context = RequestContext(
        request,
        {
            'first_name': message.owner.username,
            'unsubscribe_url': '',
            'preview': True
        }
    )
    template = Template(content)

    return HttpResponse(template.render(context)) 

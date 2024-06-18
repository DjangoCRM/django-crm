from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.template import RequestContext
from django.template import Template

from massmail.models import Signature

load_mailbuilder = "{% load mailbuilder %}"


def get_template(signature: Signature) -> Template:
    
    if signature.type == Signature.HTML:
        content = f"""
        {load_mailbuilder}
        <br>
        <br>
        {signature.content}
        """
    else:
        content = f"""
        {load_mailbuilder}<br>
        <pre>{signature.content}</pre>
        """
    return Template(content)


def signature_preview(request: WSGIRequest) -> HttpResponse:
    signature_id = request.GET.get('signature')
    if signature_id:
        signature = Signature.objects.get(id=signature_id)
        template = get_template(signature)
        context = RequestContext(
            request,
            {'preview': True}
        )
        return HttpResponse(template.render(context))
    return HttpResponse('')

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.template import RequestContext
from django.template import Template

from crm.site.crmadminsite import crm_site
from common.utils.permissions import object_not_found_response
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
        signature_admin = crm_site._registry[Signature]
        signature = signature_admin.get_queryset(request).filter(
            pk=signature_id
        ).first()
        if (
            not signature
            or not signature_admin.has_view_permission(request, signature)
        ):
            return object_not_found_response(
                request, signature_admin, signature_id
            )
        template = get_template(signature)
        context = RequestContext(
            request,
            {'preview': True}
        )
        return HttpResponse(template.render(context))
    return HttpResponse('')

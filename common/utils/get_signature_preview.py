from django.template import Context
from django.template import Template

from massmail.models import Signature
from massmail.views.signature_previews import get_template


def get_signature_preview(obj: Signature) -> Template:
    """
    Used as callable field in CrmEmailAdmin and EmlMessageAdmin.
    """
    template = get_template(obj)
    context = Context({'preview': True}) 
    return get_rendered_context(template, context)


def get_rendered_context(template: Template,
                    context: Context) -> str:
    """
    Handle template.render(context) method.
    """
    try:
        rendered_context = template.render(context)
    except (FileNotFoundError, TypeError) as err:
        e = str(err)
        return e.split(':')[0] + ': media' + e.split('media')[-1]
    return rendered_context

from django.template import Context
from django.template import Template

from common.utils.get_signature_preview import get_rendered_context
from massmail.models.email_message import EmlMessage


def get_rendered_msg(message: EmlMessage, show_signature: bool = True) -> str:
    """
    Render message content for a mailing with optional signature.
    """
    content = f"""
    {{% load mailbuilder %}}
    SUBJECT: {message.subject}<br>
    {message.content}<br>
    {message.signature.content if message.signature and show_signature else ''}
    """
    template = Template(content)
    context = Context({'preview': True})
    
    return get_rendered_context(template, context)

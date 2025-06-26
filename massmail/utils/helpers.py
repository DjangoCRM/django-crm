from django.template import Context
from django.template import Template

from common.utils.get_signature_preview import get_rendered_context


def get_rendered_msg(message):
    content = f"""
    {{% load mailbuilder %}}
    SUBJECT: {message.subject}<br>
    {message.content}<br>
    {message.signature.content if message.signature else ''}
    """
    template = Template(content)
    context = Context({'preview': True})
    return get_rendered_context(template, context)

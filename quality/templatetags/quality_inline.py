from django import template

from common.utils.helpers import SAFE_ATTACH_FILE_ICON

register = template.Library()


@register.filter
def file_links_for(inline_admin_form):
    """Returns rendered file links for an inline form, or empty string."""
    if not inline_admin_form.original:
        return ''
    return inline_admin_form.model_admin.file_links(
        inline_admin_form.original
    )


@register.simple_tag
def attach_icon():
    """Returns the paperclip icon used for file attachments."""
    return SAFE_ATTACH_FILE_ICON

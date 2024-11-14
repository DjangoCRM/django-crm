from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

chat_red_icon = '<i class="material-icons" style="font-size: 17px;color: var(--error-fg);">forum</i>'
chat_icon = '<i class="material-icons" style="font-size: 17px;color: var(--body-quiet-color);">forum</i>'
chat_link_str = '<a href="{}?content_type__id={}&object_id={}" title="{}" target="_blank">{}</a>'
view_chat_str = _("View chat messages")


def get_chat_link(obj) -> str:
    value = ''
    content_type = ContentType.objects.get_for_model(obj.__class__)
    url = reverse('site:chat_chatmessage_changelist')
    if getattr(obj, 'is_chat', None):
        value = mark_safe(chat_link_str.format(
            url, content_type.id, obj.pk, view_chat_str, chat_icon))
    if getattr(obj, 'is_unread_chat', None):
        value = mark_safe(chat_link_str.format(
            url, content_type.id, obj.pk, view_chat_str, chat_red_icon))
    return value

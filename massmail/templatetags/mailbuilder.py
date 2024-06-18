from pathlib import Path
from email.mime.image import MIMEImage
from urllib.parse import quote
from uuid import uuid4
from django.template import Library
from django.conf import settings

register = Library()


@register.simple_tag(takes_context=True)
def cid_static(context, file_name):
    """
    Embed a file from static files.
    """
    file_path = settings.STATIC_ROOT / (file_name + "")
    file_obj = open(file_path, 'rb')
    return _embed_cid(
        context,
        file_obj,
        file_name,
        settings.STATIC_URL
    )


@register.simple_tag(takes_context=True)
def cid_media(context, file_name):
    """
    Embed a file from a media files
    """
    file_path = settings.MEDIA_ROOT / (file_name + "")
    file_obj = open(file_path, 'rb')

    return _embed_cid(
        context,
        file_obj,
        file_name,
        settings.MEDIA_URL
    )


def _embed_cid(context, file_obj, file_name, url):
    """
    Generates a CID URI, and stores the MIME attachment
    in the context.request_context
    """
    cid = uuid4()
    if 'cid' not in context:
        context['cid'] = []
    img = MIMEImage(file_obj.read(), name=file_name)
    file_obj.close()
    img.add_header(
        'Content-ID',
        '<{}>'.format(quote(str(cid)))
    )
    context['cid'].append(img)
    if context.get('preview', False):
        return Path(url) / (file_name + "")
    return 'cid:{}'.format(cid)

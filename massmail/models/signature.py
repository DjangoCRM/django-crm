from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from common.models import Base1

content_help_text = mark_safe(_(
    """
    Use HTML. To specify the address of the embedded image, use {% cid_media ‘path/to/pic.png' %}.<br>
    You can embed files uploaded to the CPM server in the ‘media/pics/’ folder.
    """
))


class Signature(Base1):
    class Meta:
        verbose_name = _('Signature')
        verbose_name_plural = _('Signatures')

    HTML = 'HTML'
    PLAIN_TEXT = 'Plain text'
    TYPE_CHOICES = (
        ('HTML', 'HTML'),
        ('Plain text', 'Plain text'),
    )
    name = models.CharField(
        max_length=100, null=False, blank=False,
        help_text=_("The name of the signature.")
    )
    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default='HTML',
    )
    content = models.TextField(
        help_text=content_help_text
    )
    default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} - {self.type} ({self.owner})'

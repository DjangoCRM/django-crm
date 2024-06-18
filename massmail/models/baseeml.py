from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import Base1
from massmail.models import Signature


class BaseEml(Base1):
    class Meta:
        abstract = True

    subject = models.CharField(
        max_length=250, null=False, blank=False,
        help_text=_("The subject of the message. You can use {{first_name}},"
                    " {{last_name}}, {{first_middle_name}} or {{full_name}}"),
        verbose_name=_("Subject")
    )
    content = models.TextField()
    signature = models.ForeignKey(
        Signature, blank=True, null=True, on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_owner_signature_related",
        verbose_name=_("Choose signature"),
        help_text=_("Sender's signature.")
    )
    prev_corr = models.TextField(
        blank=True, default='',
        verbose_name=_("Previous correspondence"),
        help_text=_("Previous correspondence. Will be added after signature")
    )
    is_html = models.BooleanField(default=True)

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.conf import settings

from common.models import StageBase
from .contact import Contact


class Base(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=70, null=False, blank=False)
    department = models.ForeignKey(
        'auth.Group',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return gettext(self.name)


class ClientType(Base):
    class Meta:
        verbose_name = _('Type of Clients')
        verbose_name_plural = _('Types of Clients')


class Industry(Base):
    class Meta:
        verbose_name = _('Industry of Clients')
        verbose_name_plural = _('Industries of Clients')


class Stage(StageBase):
    """Deal stage"""

    second_default = models.BooleanField(
        default=False,
        verbose_name=_("Second default"),
        help_text=_("Will be selected next after the default stage.")
    )
    success_stage = models.BooleanField(
        default=False,
        verbose_name=_("success stage"),
    )
    conditional_success_stage = models.BooleanField(
        default=False,
        verbose_name=_("conditional success stage"),
        help_text=_("For example, receiving the first payment")
    )
    goods_shipped = models.BooleanField(
        default=False,
        verbose_name=_("goods shipped"),
        help_text=_("Have the goods been shipped at this stage already?")
    )


class LeadSource(Base):
    class Meta:
        verbose_name = _('Lead Source')
        verbose_name_plural = _('Lead Sources')

    department = models.ForeignKey(
        'common.Department',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    email = models.EmailField(blank=True, default='')
    uuid = models.UUIDField(default=uuid.uuid4)
    form_template = models.CharField(
        max_length=70, default='', null=False, blank=True,
        verbose_name=_("form template name"),
        help_text=_("The name of the html template file if needed.")
    )
    success_template = models.CharField(
        max_length=70, default='', null=False, blank=True,
        verbose_name=_("success page template name"),
        help_text=_("The name of the html template file if needed.")
    )
    sla_hours = models.PositiveSmallIntegerField(
        blank=True, null=True,
        verbose_name=_("SLA hours"),
        help_text=_("Override default first-response SLA hours for this source.")
    )


class CallLog(models.Model):
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='call_logs'
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='call_logs'
    )
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    number = models.CharField(max_length=50)
    duration = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    timestamp = models.DateTimeField(auto_now_add=True)
    voip_call_id = models.CharField(max_length=255, null=True, blank=True, unique=True, help_text="ID from VoIP provider")

    def __str__(self):
        return f"{self.get_direction_display()} call with {self.number} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']


class ClosingReason(Base):
    name = models.CharField(max_length=70, null=False, blank=False)
    index_number = models.SmallIntegerField(
        null=False, blank=False,
        help_text=_("Reason rating. \
        The indices of other instances will be sorted automatically.")
    )
    success_reason = models.BooleanField(
        default=False,
        verbose_name=_("success reason"),
    )

    class Meta:
        ordering = ['index_number']
        # unique_together=('index_number', 'department')
        verbose_name = _('Closing reason')
        verbose_name_plural = _('Closing reasons')

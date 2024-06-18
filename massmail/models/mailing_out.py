from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from common.models import Base1
from massmail.models import EmlMessage


class MailingOut(Base1):

    class Meta:
        verbose_name = _('Mailing Out')
        verbose_name_plural = _('Mailing Outs')

    STATUS_CHOICES = (
        ('A', _('Active')),
        ('E', _('Active but Error')),
        ('P', _('Paused')),
        ('I', _('Interrupted')),
        ('D', _('Done')),
    )
    name = models.CharField(
        max_length=100, null=False, blank=False,
        verbose_name=_("Name"),
        help_text=_("The name of the message.")
    )
    message = models.ForeignKey(
        EmlMessage, blank=False, null=True,
        on_delete=models.CASCADE,
        related_name="mailing_outs",
        verbose_name=_("Message"),
    )
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default='P',
        verbose_name=_("Status"),
    )
    recipients_number = models.PositiveIntegerField(
        verbose_name=_("Recipients"),
        help_text=_("Number of recipients")
    )
    recipient_ids = models.TextField()
    successful_ids = models.TextField(blank=True, default='')
    failed_ids = models.TextField(blank=True, default='')

    content_type = models.ForeignKey(
        ContentType, blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name="content_types",
        verbose_name=_("Recipients type"),
    )
    report = models.TextField(
        blank=True, default='',
        verbose_name=_("Report"),
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Creation date")
    )
    today_count = models.PositiveIntegerField(default=0, blank=True)
    sending_date = models.DateField(blank=True, null=True)

    def get_successful_ids(self):
        return self.get_ids(self.successful_ids)

    def get_failed_ids(self):
        return self.get_ids(self.failed_ids)

    def get_recipient_ids(self):
        return self.get_ids(self.recipient_ids)

    @staticmethod
    def get_ids(field):
        if field:
            return [int(r_id) for r_id in field.split(',')]
        return []

    def remove_recipient_ids(self, recipient_id):
        recipient_ids = self.get_recipient_ids()
        recipient_ids.remove(recipient_id)
        self.recipient_ids = ",".join(map(str, recipient_ids))

    def move_to_successful_ids(self, recipient_id):
        self.remove_recipient_ids(recipient_id)
        successful_ids = self.get_successful_ids()
        successful_ids.append(recipient_id)
        self.successful_ids = ",".join(map(str, successful_ids))
        self.save()

    def move_to_failed_ids(self, recipient_id):
        self.remove_recipient_ids(recipient_id)
        failed_ids = self.get_failed_ids()
        failed_ids.append(recipient_id)
        self.failed_ids = ",".join(map(str, failed_ids))
        self.save()

    def move_to_recipient_ids(self):
        recipient_ids = self.get_recipient_ids()
        failed_ids = self.get_failed_ids()
        recipient_ids.extend(failed_ids)
        self.recipient_ids = ",".join(map(str, recipient_ids))
        self.failed_ids = ''
        self.save()

    def __str__(self):
        return self.name

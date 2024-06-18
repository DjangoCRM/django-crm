from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse

from massmail.models.baseeml import BaseEml


class CrmEmail(BaseEml):
    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails in CRM")

    to = models.TextField(
        null=True, blank=False,
        verbose_name=_("To"),
        help_text=_("You can specify multiple addresses, separated by commas")
    )
    from_field = models.CharField(
        max_length=200, null=True, blank=True,
        verbose_name=_("From"),
        help_text=_("The Email address of sender")
    )
    cc = models.TextField(
        null=True, blank=True,
        help_text=_("You can specify multiple addresses, separated by commas")
    )
    bcc = models.TextField(
        null=True, blank=True,
        help_text=_("You can specify multiple addresses, separated by commas")
    )   
    sent = models.BooleanField(default=False)
    incoming = models.BooleanField(default=False)
    trash = models.BooleanField(default=False)
    inquiry = models.BooleanField(default=False)
    read_receipt = models.BooleanField(
        default=False,
        verbose_name=_("Request a read receipt"),
        help_text=_("Not supported by all mail services.")
    )
    deal = models.ForeignKey(
        'Deal', blank=True, null=True, on_delete=models.CASCADE,
        related_name="deal_emails",
        verbose_name=_("Deal")
    )
    lead = models.ForeignKey(
        'Lead', blank=True, null=True, on_delete=models.CASCADE,
        related_name="lead_emails",
        verbose_name=_("Lead")
    )
    contact = models.ForeignKey(
        'Contact', blank=True, null=True, on_delete=models.CASCADE,
        related_name="contact_emails",
        verbose_name=_("Contact")
    )
    company = models.ForeignKey(
        'Company', blank=True, null=True, on_delete=models.CASCADE,
        related_name="company_emails",
        verbose_name=_("Company")
    )
    request = models.ForeignKey(
        'Request', blank=True, null=True, on_delete=models.CASCADE,
        related_name="request_emails",
        verbose_name=_("Request")
    )
    uid = models.PositiveIntegerField(blank=True, null=True, )
    imap_host = models.CharField(
        max_length=100, null=False, blank=True,
        default='',
    )
    email_host_user = models.CharField(
        max_length=100, null=False, blank=True,
        default='',
    )
    ticket = models.CharField(
        max_length=16, default='', blank=True
    )
    message_id = models.CharField(
        max_length=200, null=False, blank=True,
        default='',
    )
    files = GenericRelation('common.TheFile')

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse(f'site:crm_{self._meta.model_name}_change', args=[str(self.id)])
    
    def save(self, *args, **kwargs):
        if self.contact and not self.company:
            self.company_id = self.contact.company_id
        super().save(*args, **kwargs)

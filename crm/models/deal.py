from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from common.models import Base1


class Deal(Base1):
    class Meta:
        verbose_name = _("Deal")
        verbose_name_plural = _("Deals")

    name = models.CharField(
        max_length=250, null=False, blank=False,
        verbose_name=_("Name"),
        help_text=_("Deal name")
    )
    next_step = models.CharField(
        max_length=250,
        verbose_name=_("Next step"),
        help_text=_(
            "Describe briefly what needs to be done in the next step."
        )
    )
    next_step_date = models.DateField(
        verbose_name=_("Step date"),
        help_text=_("Date to which the next step should be taken.")
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Description"),
    )
    workflow = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Workflow"),
    )
    stage = models.ForeignKey(
        'Stage',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Stage")
    )
    stages_dates = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Dates of the stages"),
        help_text=_("Dates of passing the stages")
    )
    closing_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Date of deal closing")
    )
    win_closing_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Date of won deal closing")
    )
    amount = models.DecimalField(
        blank=True,
        null=True,
        default=0,
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Amount"),
        help_text=_("Total deal amount without VAT")
    )
    currency = models.ForeignKey(
        'Currency',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Currency")
    )
    closing_reason = models.ForeignKey(
        'ClosingReason',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Closing reason")
    )
    probability = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Probability (%)")
    )
    ticket = models.CharField(
        max_length=16,
        default='',
        unique=True
    )
    city = models.ForeignKey(
        'City', 
        blank=True, 
        null=True,
        verbose_name=_("City"),
        on_delete=models.SET_NULL
    )     
    country = models.ForeignKey(
        'Country',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("country"),
        help_text=_("Country")
    )
    lead = models.ForeignKey(
        'Lead',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Lead")
    )
    contact = models.ForeignKey(
        'Contact',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Contact")
    )
    # Redundant key is required by business logic
    request = models.ForeignKey(
        'Request',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Request"),
        related_name="deals",
    )
    company = models.ForeignKey(
        'Company',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="deals",
        verbose_name=_("Company of contact")
    )
    partner_contact = models.ForeignKey(
        'Contact',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Partner contact"),
        related_name="partner_contacts",
        help_text=_(
            "Contact person of dealer or distribution company"
        )
    )
    relevant = models.BooleanField(
        default=True,
        verbose_name=_("Relevant"),
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
    )
    important = models.BooleanField(
        default=False,
        verbose_name=_("Important"),
    )
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        verbose_name=_("Tags")
    )
    is_new = models.BooleanField(
        default=True,
    )
    remind_me = models.BooleanField(
        default=False,
        verbose_name=_("Remind me.")
    )
    co_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Co-owner"),
        related_name="%(app_label)s_%(class)s_co_owner_related",
    )
    files = GenericRelation('common.TheFile')

    def change_stage_data(self, date):
        data = f'{date} - {self.stage}\n'
        self.stages_dates = self.stages_dates + data

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('site:crm_deal_change', args=(self.id,))

    def next_step_name(self):
        if self.is_new:
            return mark_safe(f'<b>{self.next_step}<b>')
        return self.next_step

    next_step_name.short_description = _('Next step')

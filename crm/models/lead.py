from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import Base1
from common.utils.helpers import token_default
from crm.models.base_contact import BaseContact
from crm.utils.helpers import delete_rel_mc


class Lead(BaseContact, Base1):
    class Meta:
        verbose_name = _("Lead")
        verbose_name_plural = _("Leads")

    disqualified = models.BooleanField(
        default=False,
        verbose_name=_("Disqualified"),
    )
    address = models.TextField(
        blank=True, default='',
        verbose_name=_("Address"),
    )
    description = models.TextField(
        blank=True, default='',
        verbose_name=_("Description"),
    )
    lead_source = models.ForeignKey(
        'LeadSource', blank=True,
        null=True, on_delete=models.SET_NULL,
        verbose_name=_("Lead Source"),
        help_text=_("Lead Source")
    )
    company_name = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("Company name"),
    )
    website = models.URLField(
        max_length=200, blank=True, default=''
    )

    company_phone = models.CharField(
        max_length=20, blank=True, default='',
        verbose_name=_("Company phone"),
    )
    company_address = models.TextField(
        blank=True, default='',
        verbose_name=_("Company address"),
    )
    company_email = models.EmailField(
        blank=True, default='',
        verbose_name=_("Company email"),
    )
    type = models.ForeignKey(
        'ClientType', 
        blank=True, 
        null=True, 
        on_delete=models.SET_NULL,
        verbose_name=_("Type of company")
    )
    industry = models.ManyToManyField(
        'Industry', 
        blank=True,
        verbose_name=_("Industry of company")
    )
    tags = models.ManyToManyField(
        'Tag', blank=True,
        verbose_name=_("Tags"),
    )
    token = models.CharField(
        max_length=11, 
        default=token_default,
        unique=True,
    )
    contact = models.ForeignKey(
        'Contact', blank=True, null=True, on_delete=models.CASCADE,
        verbose_name=_("Contact")
    )
    company = models.ForeignKey(
        'Company', blank=True, null=True, on_delete=models.CASCADE,
        verbose_name=_("Company of contact")
    )
    
    def delete(self, *args, **kwargs):
        delete_rel_mc(self)
        super().delete(*args, **kwargs)

    def __str__(self):
        if self.company_name:
            return f"{self.full_name}, {self.company_name}," \
                   f" {self.country}"
        return self.full_name

    @property
    def full_name(self):
        full_name = ' '.join(filter(
            None, 
            (self.first_name, self.middle_name, self.last_name)
        ))
        if self.disqualified:
            full_name = f"({_('Disqualified')}) {full_name}"
        return full_name

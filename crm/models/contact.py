from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from common.models import Base1
from common.utils.helpers import token_default
from crm.models.base_contact import BaseContact
from crm.utils.helpers import delete_rel_mc


class Contact(BaseContact, Base1):
    class Meta:
        verbose_name = _("Contact person")
        verbose_name_plural = _("Contact persons")

    company = models.ForeignKey(
        'Company', blank=False,
        null=False, on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name=_("Company of contact")
    )
    address = models.TextField(blank=True, default='')

    description = models.TextField(blank=True, default='')

    lead_source = models.ForeignKey(
        'LeadSource', blank=True, null=True,
        on_delete=models.SET_NULL, help_text=_("Lead Source")
    )
    tags = models.ManyToManyField(
        'Tag', blank=True,
        verbose_name=_("Tags")
    )
    token = models.CharField(
        max_length=11, 
        default=token_default,
        unique=True,
    )

    @property
    def company_country(self):
        return self.company.country

    def delete(self, *args, **kwargs):
        delete_rel_mc(self)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.company}, {self.country}"
    
    def get_absolute_url(self):  
        return reverse('admin:crm_contact_change', args=(self.id,))

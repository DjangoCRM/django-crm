from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from common.models import Base1
from crm.models.base_contact import BaseContact
from crm.models.base_contact import BaseCounterparty


class Contact(BaseCounterparty, BaseContact, Base1):
    class Meta:
        verbose_name = _("Contact person")
        verbose_name_plural = _("Contact persons")

    company = models.ForeignKey(
        'Company', blank=False,
        null=False, on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name=_("Company of contact")
    )

    @property
    def company_country(self):
        return self.company.country

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.company}, {self.country}"
    
    def get_absolute_url(self):  
        return reverse('admin:crm_contact_change', args=(self.id,))

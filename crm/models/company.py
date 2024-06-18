from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from common.models import Base1
from common.utils.helpers import token_default
from crm.utils.helpers import delete_rel_mc


class Company(Base1):
    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        unique_together = (('full_name', 'country'),)

    full_name = models.CharField(
        max_length=200, 
        null=False, 
        blank=False,
        verbose_name=_("Company name")
    )
    alternative_names = models.CharField(
        max_length=100,
        default='',
        blank=True,
        verbose_name=_("Alternative names"),
        help_text=_("Separate them with commas.")
    )
    website = models.CharField(
        max_length=200, 
        blank=True, 
        default='',
        verbose_name=_("Website")
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
    )
    phone = models.CharField(
        max_length=100, 
        blank=True, 
        default='',
        verbose_name=_("Phone")
    )
    city_name = models.CharField(
        max_length=100, 
        blank=True, 
        default='',
        verbose_name=_("City name")
    )
    city = models.ForeignKey(
        'City', 
        blank=True, 
        null=True,
        verbose_name=_("City"),
        on_delete=models.SET_NULL
    )    
    address = models.TextField(
        blank=True, default='',
        verbose_name=_("Address")
    )
    email = models.CharField(
        max_length=200, 
        null=False, 
        blank=False,
        verbose_name="Email",
        help_text=_("Use comma to separate Emails.")
    )
    registration_number = models.CharField(
        max_length=30, 
        default='', 
        blank=True,
        verbose_name=_("Registration number"),
        help_text=_("Registration number of Company")
    )
    description = models.TextField(
        blank=True, 
        default='',
        verbose_name=_("Description"),
    )
    lead_source = models.ForeignKey(
        'LeadSource', 
        blank=True, 
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Lead Source"),
        help_text=_("Lead Source")
    )
    was_in_touch = models.DateField(
        blank=True, 
        null=True,
        verbose_name=_("Last contact date"),
        help_text=_("Last contact date")
    )
    country = models.ForeignKey(
        'Country', 
        blank=True, 
        null=True, 
        on_delete=models.SET_NULL,
        verbose_name=_("country"),
        help_text=_("Company Country")
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
        'Tag', 
        blank=True,
        verbose_name=_("Tags")
    )
    token = models.CharField(
        max_length=11, 
        default=token_default,
        unique=True,
    )
    files = GenericRelation('common.TheFile')

    def delete(self, *args, **kwargs):
        delete_rel_mc(self)
        super().delete(*args, **kwargs)

    def get_absolute_url(self):  
        return reverse('admin:crm_company_change', args=(self.id,))

    def __str__(self):
        return self.full_name

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from common.utils.helpers import get_today
from common.utils.helpers import token_default
from massmail.models import MassContact


class BaseContact(models.Model):
    class Meta:
        abstract = True

    first_name = models.CharField(
        max_length=100, null=False, blank=False,
        help_text=_("The name of the contact person (one word)."),
        verbose_name=_("First name"),
    )
    middle_name = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name=_("Middle name"),
        help_text=_("The middle name of the contact person.")
    )
    last_name = models.CharField(
        max_length=100, blank=True, default='',
        help_text=_("The last name of the contact person (one word)."),
        verbose_name=_("Last name"),
    )
    title = models.CharField(
        max_length=100, null=True, blank=True,
        help_text=_("The title (position) of the contact person."),
        verbose_name=_("Title / Position"),
    )
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    sex = models.CharField(
        null=True, blank=True,
        max_length=1, choices=SEX_CHOICES, default='M',
        verbose_name=_("Sex"),
    )
    birth_date = models.DateField(
        blank=True, null=True,
        verbose_name=_("Date of Birth")
    )
    secondary_email = models.EmailField(
        blank=True, default='',
        verbose_name=_("Secondary email")
    )
    phone = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name=_("Phone")
    )
    other_phone = models.CharField(max_length=100, blank=True, default='')

    mobile = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name=_("Mobile phone")
    )

    city_name = models.CharField(
        max_length=50, blank=True, default='',
        verbose_name=_("City")
    )
    city = models.ForeignKey(
        'City', blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Company city"),
        help_text=_("Object of City in database")
    )
    country = models.ForeignKey(
        'Country', blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Country"),
    )

    def was_in_touch_today(self):
        date = get_today()
        self.was_in_touch = date
        self.save()

    @property
    def full_name(self):
        return ' '.join(filter(
            None, 
            (self.first_name, self.middle_name, self.last_name)
        ))

    @property
    def first_middle_name(self):
        return ' '.join(filter(
            None, 
            (self.first_name, self.middle_name)
        ))


class BaseCounterparty(models.Model):
    """
    Common fields for models: Company, Contact, Lead
    """
    class Meta:
        abstract = True

    address = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Address")
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Description")
    )
    disqualified = models.BooleanField(
        default=False,
        verbose_name=_("Disqualified"),
    )
    email = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        verbose_name="Email",
        help_text=_("Use comma to separate Emails.")
    )
    lead_source = models.ForeignKey(
        'LeadSource',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Lead Source")
    )
    massmail = models.BooleanField(
        default=True,
        verbose_name=_("Mass mailing"),
        help_text=_("Mailing list recipient.")
    )
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        verbose_name=_("Tags")
    )
    token = models.CharField(
        max_length=11,
        default=token_default,
        unique=True
    )
    was_in_touch = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Last contact date")
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Assigned to"),
        related_name="%(app_label)s_%(class)s_owner_related",
    )

    def delete(self, *args, **kwargs):
        content_type = ContentType.objects.get_for_model(self)
        try:
            MassContact.objects.get(
                content_type=content_type,
                object_id=self.id,
            ).delete()
        except MassContact.DoesNotExist:
            pass
        super().delete(*args, **kwargs)

    def get_crm_url(self) -> str:
        """Returns the URL of an object on the CRM site"""
        return reverse(f'site:crm_{self._meta.model_name}_change', args=(self.id,))

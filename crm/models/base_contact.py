from django.db import models
from django.utils.translation import gettext_lazy as _
from common.utils.helpers import get_today


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
    was_in_touch = models.DateField(
        blank=True, null=True,
        verbose_name=_("Last contact date")
    )
    email = models.CharField(
        max_length=200, null=False, blank=False,
        verbose_name="Email",
        help_text=_("Use comma to separate Emails.")
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

    skype = models.CharField(max_length=50, blank=True, default='')

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
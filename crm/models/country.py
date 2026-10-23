from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

warning_str = _("has already been assigned to the city")


class BaseModel(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(
        max_length=40,
        verbose_name=_("Name")
    )
    alternative_names = models.CharField(
        max_length=100,
        default='',
        blank=True,
        verbose_name=_("Alternative names"),
        help_text=_("Separate them with commas.")
    )

    def __str__(self):
        return self.name


class BaseRegion(BaseModel):
    """
    Geographical regions according to the UN 
    'Standard Country or Area Codes for Statistical Use' (M49)
    https://unstats.un.org/unsd/methodology/m49/
    """

    class Meta:
        abstract = True

    name = models.CharField(
        max_length=40,
        verbose_name=_("Name")
    )
    alternative_names = None


class ContinentalRegion(BaseRegion):
    class Meta:
        verbose_name = _('Continental region')
        verbose_name_plural = _('Continental regions')


class SubRegion(BaseRegion):
    class Meta:
        verbose_name = _('Subregion')
        verbose_name_plural = _('Subregions')

    continental_region = models.ForeignKey(
        "ContinentalRegion",
        on_delete=models.CASCADE,
        verbose_name=_("Continental region")
    )


class IntermediaryRegion(BaseRegion):
    class Meta:
        verbose_name = _('Intermediary region')
        verbose_name_plural = _('Intermediary regions')

    subregion = models.ForeignKey(
        "SubRegion",
        on_delete=models.CASCADE,
        verbose_name=_("Subregion")
    )


class Country(BaseModel):
    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    url_name = models.SlugField(
        max_length=50,
        null=False,
        blank=False
    )
    subregion = models.ForeignKey(
        "SubRegion",
        blank=False, null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Subregion")
    )
    intermediary_region = models.ForeignKey(
        "IntermediaryRegion",
        blank=True, null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Intermediary region")
    )
    owner = models.ForeignKey(
        "auth.User", blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Owner"),
        related_name="%(app_label)s_%(class)s_owner_related",
    )
    iso_code = models.CharField(
        max_length=2, blank=False, default='',
        verbose_name=_("ISO code"),
        help_text=_("ISO 3166-1 alpha-2 code")
    )
    phone_code = models.CharField(
        max_length=4,
        blank=False,
        default='',
        verbose_name=_("Phone code")
    )

    @property
    def flag_and_name(self):
        return mark_safe(f'<span class="fi fi-{self.iso_code}"></span> {self.name}')


class City(BaseModel):
    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")

    country = models.ForeignKey(
        "Country",
        on_delete=models.CASCADE,
        verbose_name=_("Country")
    )

    def clean(self):
        super().clean_fields()
        if self.country:
            self.cities = City.objects.all()
            if self.id:
                self.cities = self.cities.exclude(id=self.id)
            self.validate_name(self.name, 'name')
            if self.alternative_names:
                alternative_names = self.alternative_names.split(",")
                for name in alternative_names:
                    if name:
                        self.validate_name(name.strip(), 'alternative_names')

    def validate_name(self, name: str, field: str) -> None:
        city = self.cities.filter(
            Q(name__iexact=name) |
            Q(alternative_names__icontains=name),
            country=self.country
        ).first()
        if city:
            raise ValidationError({
                field: f'"{name}" - {warning_str} "{city.name}" ID:{city.id}'
            })

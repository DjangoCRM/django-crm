from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
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


class Country(BaseModel):
    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    url_name = models.SlugField(
        max_length=50,
        null=False,
        blank=False
    )


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
            self.validate_name(self.name, 'name')
            if self.alternative_names:
                alternative_names = self.alternative_names.split(",")
                for name in alternative_names:
                    if name:
                        self.validate_name(name.strip(), 'alternative_names')

    def validate_name(self, name: str, field: str) -> None:
        cities = City.objects.all()
        if self.id:
            cities = cities.exclude(id=self.id)
        city = cities.filter(
            Q(name__iexact=name) |
            Q(alternative_names__icontains=name),
            country=self.country
        ).first()
        if city:
            raise ValidationError({
                field: f'"{name}" - {warning_str} "{city.name}" ID:{city.id}'
            })

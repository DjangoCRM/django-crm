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
        super().clean()

        if not self.country or not self.name:
            return

        name_norm = self.name.strip().lower()

        alt_list = [
            alt.strip().lower()
            for alt in self.alternative_names.split(",")
            if alt.strip()
        ]

        qs = City.objects.filter(country=self.country)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        for city in qs:
            city_name_norm = city.name.strip().lower()
            city_alt_list = [
                alt.strip().lower()
                for alt in city.alternative_names.split(",")
                if alt.strip()
            ]

            # Primary name conflict
            if city_name_norm == name_norm:
                raise ValidationError({
                    "name": f'"{self.name}" - {warning_str} "{city.name}" ID:{city.id}'
                })

            # Primary name vs alternative names
            if name_norm in city_alt_list:
                raise ValidationError({
                    "name": f'"{self.name}" - {warning_str} "{city.name}" ID:{city.id}'
                })
            # Alternative name conflicts
            for alt in alt_list:
                if alt == city_name_norm or alt in city_alt_list:
                    raise ValidationError({
                        "alternative_names":
                            f'"{alt}" - {warning_str} "{city.name}" ID:{city.id}'
                    })


from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext


class Resolution(models.Model):
    class Meta:
        ordering = ["index_number"]
        verbose_name = _("Resolution")
        verbose_name_plural = _("Resolutions")

    name = models.CharField(
        max_length=70, null=False, blank=False, verbose_name=_("Name")
    )
    index_number = models.SmallIntegerField(null=False, blank=False, default=1)

    def __str__(self):
        return gettext(self.name)

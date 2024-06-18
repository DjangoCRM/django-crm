from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    name = models.CharField(
        max_length=70, default="", verbose_name=_("Tag name")
    )
    for_content = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Tag for"),
        related_name="%(app_label)s_%(class)s_content_related",
        limit_choices_to={"model__in": ("memo", "project", "task")},
    )

    def __str__(self):
        return self.name

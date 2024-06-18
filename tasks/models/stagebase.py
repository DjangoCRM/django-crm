from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext


class StageBase(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=70, null=False, blank=False)

    default = models.BooleanField(
        default=False,
        verbose_name=_("Default"),
        help_text=_("Will be selected by default when creating a new task"),
    )
    done = models.BooleanField(
        default=False,
        verbose_name=_("Done"),
        help_text=_('Mark if this stage is "done"'),
    )
    in_progress = models.BooleanField(
        default=False,
        verbose_name=_("In progress"),
        help_text=_('Mark if this stage is "in progress"'),
    )
    index_number = models.SmallIntegerField(
        null=False,
        blank=False,
        default=1,
        help_text=_(
            "The sequence number of the stage. \
        The indices of other instances will be sorted automatically."
        ),
    )

    def __str__(self):
        return gettext(self.name)

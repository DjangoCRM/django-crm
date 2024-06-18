from django.db import models
from django.utils.translation import gettext_lazy as _
from tasks.models.stagebase import StageBase


class TaskStage(StageBase):
    class Meta:
        ordering = ["index_number"]
        verbose_name = _("Task stage")
        verbose_name_plural = _("Task stages")

    active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Is the task active at this stage?"),
    )

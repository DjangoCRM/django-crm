from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from tasks.models.taskbase import TaskBase


class Project(TaskBase):
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    stage = models.ForeignKey(
        "ProjectStage",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Stage"),
    )

    def get_absolute_url(self):
        return reverse("site:tasks_project_change", args=(self.id,))

    def save(self, *args, **kwargs):
        if self.stage:
            self.active = self.stage.active
        super().save(*args, **kwargs)

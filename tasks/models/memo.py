from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from common.models import Base
from common.utils.email_to_participants import email_to_participants
from common.utils.helpers import compose_subject


class Memo(Base):
    class Meta:
        verbose_name = _("Memo")
        verbose_name_plural = _("Memos")

    PENDING = 'pen'
    POSTPONED = 'pos'
    REVIEWED = 'rev'
    STATE_CHOICES = [
        (PENDING, _('pending')),
        (POSTPONED, _('postponed')),
        (REVIEWED, _('reviewed')),
    ]

    name = models.CharField(
        max_length=250, default="",
        blank=False, verbose_name=_("Name")
    )
    to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_to_whom_related",
        verbose_name=_("to whom"),
    )
    task = models.ForeignKey(
        "Task",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_task_related",
        verbose_name=_("Task"),
    )
    resolution = models.ForeignKey(
        "Resolution",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_resolution_related",
        verbose_name=_("For what"),
    )
    project = models.ForeignKey(
        "Project",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_project_related",
        verbose_name=_("Project"),
    )
    deal = models.ForeignKey(
        "crm.Deal",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
        verbose_name=_("Deal"),
    )
    description = models.TextField(
        blank=True, default="", verbose_name=_("Description")
    )
    note = models.TextField(
        blank=True, default="",
        verbose_name=_("Сonclusion")
    )
    draft = models.BooleanField(
        default=False,
        verbose_name=_("Draft"),
        help_text=_("Available only to the owner."),
    )
    notified = models.BooleanField(
        default=False,
        verbose_name=_("Notified"),
        help_text=_("The recipient and subscribers are notified."),
    )
    tags = models.ManyToManyField(
        "Tag",
        blank=True,
        verbose_name=_("Tags")
    )
    review_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Review date")
    )
    stage = models.CharField(
        max_length=3,
        choices=STATE_CHOICES,
        blank=False,
        default=PENDING,
        verbose_name=_("Stage")
    )
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        verbose_name=_("subscribers"),
        related_name="%(app_label)s_%(class)s_subscribers_related",
    )
    notified_subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        verbose_name=_("Notified subscribers"),
        related_name="%(app_label)s_%(class)s_notified_subscribers_related",
    )
    files = GenericRelation("common.TheFile")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("site:tasks_memo_change", args=(self.id,))

    def send_review_notification(self) -> None:
        """Send review notification to memo owner."""
        message = _("The office memo has been reviewed")
        subject = compose_subject(self, message)
        participants = [self.owner.email]
        subscribers = self.subscribers.values_list('email', flat=True)  # NOQA
        if subscribers:
            participants.extend([*subscribers])
        email_to_participants(self, subject, participants)

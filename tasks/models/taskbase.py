from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import IntegrityError
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import Base
from common.utils.helpers import get_delta_date
from common.utils.helpers import token_default


class TaskBase(Base):
    class Meta:
        abstract = True

    LOW = 1
    MIDDLE = 2
    HIGH = 3
    PRIORITY_CHOICES = [
        (LOW, _("Low")),
        (MIDDLE, _("Middle")),
        (HIGH, _("High")),
    ]

    priority = models.SmallIntegerField(
        null=False, default=2, choices=PRIORITY_CHOICES, verbose_name=_("Priority")
    )
    name = models.CharField(
        max_length=250,
        default="",
        blank=False,
        verbose_name=_("Name"),
        help_text=_("Short title"),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
    )
    note = models.TextField(blank=True, default="", verbose_name=_("Note"))
    due_date = models.DateField(blank=True, null=True, verbose_name=_("Due date"))
    start_date = models.DateField(blank=True, null=True, verbose_name=_("Start date"))
    closing_date = models.DateField(
        blank=True, null=True, verbose_name=_("Date of task closing")
    )
    responsible = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        verbose_name=_("Responsible"),
        related_name="%(app_label)s_%(class)s_responsible_related",
    )
    notified_responsible = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        verbose_name=_("Notified responsible"),
        related_name="%(app_label)s_%(class)s_notified_responsible_related",
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
    workflow = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Workflow"),
    )
    next_step = models.CharField(
        max_length=250,
        verbose_name=_("Next step"),
        help_text=_("Describe briefly what needs to be done in the next step."),
    )
    next_step_date = models.DateField(
        verbose_name=_("Step date"),
        help_text=_("Date to which the next step should be taken."),
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
    )
    remind_me = models.BooleanField(
        default=False,
        verbose_name=_("Remind me.")
    )
    co_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Co-owner"),
        related_name="%(app_label)s_%(class)s_co_owner_related",
    )
    tags = models.ManyToManyField("Tag", blank=True, verbose_name=_("Tags"))
    token = models.CharField(
        max_length=11, 
        default=token_default,
        unique=True,
    )
    files = GenericRelation("common.TheFile")

    def save(self, *args, **kwargs):
        if not self.next_step_date:
            self.next_step_date = get_delta_date(1)
        try:
            super().save(*args, **kwargs)
        except IntegrityError as err:
            if "Duplicate entry" not in str(err):
                raise err
        
    def __str__(self):
        return self.name

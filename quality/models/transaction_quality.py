from django.db import models
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from common.models import Base2


class TransactionQualitySignal(Base2):
    class Meta:
        verbose_name = _("Transaction-Quality Signal")
        verbose_name_plural = _("Transaction-Quality Signals")

    weight = models.SmallIntegerField(
        verbose_name=_("Weight (%)"),
        help_text=_("A positive or negative integer reflecting the change in transaction quality.")
    )
    notes = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Notes")
    )

    def __str__(self):
        return f"{gettext(self.name)}"


class TransactionQualityEvent(models.Model):
    class Meta:
        verbose_name = _("Transaction-Quality Event")
        verbose_name_plural = _("Transaction-Quality Events")

    signal = models.ForeignKey(
        "TransactionQualitySignal",
        on_delete=models.CASCADE,
        verbose_name=_("Signal")
    )
    weight = models.SmallIntegerField(
        verbose_name=_("Weight (%)"),
        help_text=_("A positive or negative integer reflecting the change in transaction quality.")
    )
    deal = models.ForeignKey(
        "crm.Deal",
        on_delete=models.CASCADE,
        verbose_name=_("Deal")
    )
    creation_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Creation date")
    )
    details = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Details")
    )

    def __str__(self):
        return f"{self.signal}"

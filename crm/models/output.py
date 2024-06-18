from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from .payment import BasePayment


class Output(BasePayment):
    class Meta:
        verbose_name = _("Output")
        verbose_name_plural = _("Outputs")

    deal = models.ForeignKey(
        'crm.Deal',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        'crm.Product',
        on_delete=models.CASCADE,
        verbose_name=_("Product")
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_("Quantity")
    )
    shipping_date = models.DateField(
        blank=True, null=True,
        verbose_name=_("Shipping date"),
        help_text=_("Shipment date as per contract")
    )
    planned_shipping_date = models.DateField(
        blank=True, null=True,
        verbose_name=_("Planned shipping date"),
    )
    actual_shipping_date = models.DateField(
        blank=True, null=True,
        verbose_name=_("Actual shipping date"),
        help_text=_("Date when the product was shipped")
    )
    product_is_shipped = models.BooleanField(
        default=False,
        verbose_name=_("Shipped"),
        help_text=_("Product is shipped")
    )
    serial_number = models.CharField(
        max_length=50, default='', null=False, blank=True,
        verbose_name=_("serial number"),
    )

    @property
    def pcs(self):
        return gettext('pcs')

    def __str__(self):
        return f"{self.product} - {self.quantity}{self.pcs}"


class Shipment(Output):
    class Meta:
        proxy = True
        verbose_name = _('Shipment')
        verbose_name_plural = _('Shipments')

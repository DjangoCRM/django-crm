from datetime import date
from django.apps import apps
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from crm.utils.helpers import NO_DEAL_AMOUNT_STR



class Currency(models.Model):
    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    name = models.CharField(
        max_length=3, null=False, blank=False,
        help_text=_("Alphabetic Code for the Representation of Currencies.")
    )
    rate_to_state_currency = models.DecimalField(
        max_digits=13, decimal_places=8,
        default=1,
        verbose_name=_("Rate to state currency"),
        help_text=_("Exchange rate against the state currency.")
    )
    rate_to_marketing_currency = models.DecimalField(
        max_digits=13, decimal_places=8,
        default=1,
        verbose_name=_("Rate to marketing currency"),
        help_text=_("Exchange rate against the state currency.")
    )
    is_state_currency = models.BooleanField(
        default=False,
        verbose_name=_("Is it the state currency?"),
    )
    is_marketing_currency = models.BooleanField(
        default=False,
        verbose_name=_("Is it the marketing currency?"),
    )
    auto_update = models.BooleanField(
        default=True,
        verbose_name=_("This currency is subject to automatic updating."),
    )
    update_date = models.DateTimeField(
        auto_now=True, null=True, blank=False,
        verbose_name=_("Update date")
    )

    def save(self, *args, **kwargs):
        if self.is_state_currency:
            self.is_state_currency = 1.0
        if self.is_marketing_currency:
            self.rate_to_marketing_currency = 1.0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BasePayment(models.Model):
    class Meta:
        abstract = True

    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0,
        verbose_name=_("Amount"),
        help_text=_("without VAT")
    )
    currency = models.ForeignKey(
        'Currency',
        null=True, blank=False,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Currency"),
    )

    def clean(self):
        if not self.currency:
            msg = _("Please specify a currency.")
            raise ValidationError({
                NON_FIELD_ERRORS: msg,
                'currency': msg,
            })
        super().clean()


class Payment(BasePayment):
    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

    RECEIVED = 'r'
    GUARANTEED = 'g'
    HIGH_PROBABILITY = 'h'
    LOW_PROBABILITY = 'l'
    STATUS_CHOICES = [
        (RECEIVED, _('received')),
        (GUARANTEED, _('guaranteed')),
        (HIGH_PROBABILITY, _('high probability')),
        (LOW_PROBABILITY, _('low probability'))
    ]

    deal = models.ForeignKey(
        'crm.Deal',
        on_delete=models.CASCADE,
    )
    payment_date = models.DateField(
        default=date.today,
        verbose_name=_("Payment date")
    )
    status = models.CharField(
        max_length=1,
        default='r',
        choices=STATUS_CHOICES,
        verbose_name=_("Payment status")
    )
    contract_number = models.CharField(
        max_length=40, default='', null=False, blank=True,
        verbose_name=_("contract number"),
    )
    invoice_number = models.CharField(
        max_length=40, default='', null=False, blank=True,
        verbose_name=_("invoice number"),
    )
    order_number = models.CharField(
        max_length=40, default='', null=False, blank=True,
        verbose_name=_("order number"),
    )
    through_representation = models.BooleanField(
        default=False,
        verbose_name=_("Payment through representative office")
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == Payment.RECEIVED:
            rate_model = apps.get_model('crm', 'Rate')
            if not rate_model.objects.filter(
                    currency=self.currency, payment_date=self.payment_date
            ).exists():
                currency = self.currency
                currency.refresh_from_db()
                rate = rate_model(
                    currency=currency,
                    payment_date=self.payment_date,
                    rate_to_state_currency=currency.rate_to_state_currency,
                    rate_to_marketing_currency=currency.rate_to_marketing_currency,
                    rate_type=rate_model.APPROXIMATE
                )
                rate.save()

    def get_share(self):
        value = f'<span style="color: var(--error-fg);">{NO_DEAL_AMOUNT_STR}</span>'
        description = _('Payment share')        
        if self.deal and self.deal.amount:
            value = f"{round(100 * self.amount / self.deal.amount, 1)} %"
        return f"{description}: {value}"     

    def __str__(self):
        payment_date = date_format(
            self.payment_date,
            format='SHORT_DATE_FORMAT',
            use_l10n=True
        )
        return mark_safe(
            f'{self.amount} {self.currency}, ' \
            f'{(self.get_status_display())} {payment_date}. ' \
            f'{self.get_share()}'
        )


class Rate(models.Model):
    class Meta:
        verbose_name = _("Currency rate")
        verbose_name_plural = _("Currency rates")

    APPROXIMATE = 'A'
    OFFICIAL = 'O'
    RATE_TYPE = [
        (APPROXIMATE, _("approximate currency rate")),
        (OFFICIAL, _("official currency rate")),

    ]
    currency = models.ForeignKey(
        'crm.Currency',
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related"
    )
    payment_date = models.DateField(
        default=date.today,
        verbose_name=_("Currency rate date")
    )
    rate_to_state_currency = models.DecimalField(
        max_digits=13, decimal_places=8,
        verbose_name=_("Rate to state currency"),
        help_text=_("Exchange rate against the state currency.")
    )
    rate_to_marketing_currency = models.DecimalField(
        max_digits=13, decimal_places=8,
        verbose_name=_("Rate to marketing currency"),
        help_text=_("Exchange rate against the state currency.")
    )
    rate_type = models.CharField(
        max_length=1,
        choices=RATE_TYPE,
        default=APPROXIMATE,
        verbose_name=_("Exchange rate type")
    )

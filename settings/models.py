from django.db import models
from django.utils.translation import gettext_lazy as _


class BannedCompanyName(models.Model):
    class Meta:
        verbose_name = _("Banned company name")
        verbose_name_plural = _("Banned company names")

    name = models.CharField(
        max_length=50,  unique=True,
        null=False, blank=False,
        verbose_name=_("Name")
    )

    def __str__(self):
        return self.name


class PublicEmailDomain(models.Model):
    class Meta:
        verbose_name = _('Public email domain')
        verbose_name_plural = _('Public email domains')

    domain = models.CharField(
        max_length=20, unique=True,
        null=False, blank=False,
        verbose_name=_("Domain")
    )

    def save(self, *args, **kwargs):
        self.domain = self.domain.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.domain


class Reminders(models.Model):
    class Meta:
        verbose_name = _('Reminder settings')
        verbose_name_plural = _('Reminder settings')

    check_interval = models.PositiveBigIntegerField(
        null=False, blank=False,
        default='300',
        verbose_name=_("Check interval"),
        help_text=_(
            "Specify the interval in seconds to check if it's time for a reminder."
        )
    )


class StopPhrase(models.Model):
    class Meta:
        verbose_name = _('Stop Phrase')
        verbose_name_plural = _('Stop Phrases')

    phrase = models.CharField(
        max_length=100,  unique=True,
        null=False, blank=False,
        verbose_name=_("Phrase")
    )
    last_occurrence_date = models.DateField(
        auto_now=True,
        verbose_name=_("Last occurrence date"),
        help_text=_("Date of last occurrence of the phrase")
    )

    def hit(self):
        self.save()

    def __str__(self):
        return self.phrase

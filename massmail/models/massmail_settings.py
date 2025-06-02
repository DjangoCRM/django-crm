# massmail/models/massmail_settings.py

from django.db import models

class MassmailSettings(models.Model):
    mailing = models.BooleanField(
        default=True,
        help_text="Allow mailing (formerly MAILING)."
    )
    emails_per_day = models.PositiveIntegerField(
        default=94,
        help_text="Maximum emails/day (formerly EMAILS_PER_DAY)."
    )
    use_business_time = models.BooleanField(
        default=False,
        help_text="Send only during business hours (formerly USE_BUSINESS_TIME)."
    )
    business_time_start = models.TimeField(
        default="08:30",
        help_text="Business hours start (formerly BUSINESS_TIME_START)."
    )
    business_time_end = models.TimeField(
        default="17:30",
        help_text="Business hours end (formerly BUSINESS_TIME_END)."
    )
    unsubscribe_url = models.URLField(
        max_length=500,
        default="https://www.example.com/unsubscribe",
        help_text="Unsubscribe redirect (formerly UNSUBSCRIBE_URL)."
    )

    class Meta:
        verbose_name = "Massmail Settings"
        verbose_name_plural = "Massmail Settings"

    def __str__(self):
        return "Massmail Settings (singleton)"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
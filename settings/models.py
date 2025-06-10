from django.db import models
from django.utils.translation import gettext_lazy as _


class BannedCompanyName(models.Model):
    """
    Model representing a banned company name.

    This model is used to store company names that block the automatic generation
    of commercial requests from spam messages.
    Each name is unique and cannot be null or blank.

    Attributes:
        name (str): The name of the banned company, stored as a unique string
            with a maximum length of 50 characters.
    """
    class Meta:
        verbose_name = _("Banned company name")
        verbose_name_plural = _("Banned company names")

    name = models.CharField(
        max_length=50, unique=True,
        null=False, blank=False,
        verbose_name=_("Name")
    )

    def __str__(self):
        """
        Returns the string representation of the banned company name.
        """
        return self.name


class MassmailSettings(models.Model):
    """
    Model for mass mailing settings.
    """

    class Meta:
        verbose_name = _("Massmail Settings")
        verbose_name_plural = _("Massmail Settings")

    emails_per_day = models.PositiveIntegerField(
        default=94,
        help_text="Daily message limit for email accounts."
    )
    use_business_time = models.BooleanField(
        default=False,
        help_text="Send only during business hours."
    )
    business_time_start = models.TimeField(
        default="08:30",
        help_text="Start of working hours."
    )
    business_time_end = models.TimeField(
        default="17:30",
        help_text="End of working hours."
    )
    unsubscribe_url = models.URLField(
        default="https://www.example.com/unsubscribe",
        help_text='"Unsubscribed successfully" page."'
    )

    def __str__(self):
        return "Settings"


class PublicEmailDomain(models.Model):
    """
    Model representing a public email domain list.

    This model is used to store public domains to identify them in messages
    and prevent company identification by email domain.
    Each domain is unique and stored in the lowercase.

    Attributes:
        domain (str): The email domain, stored as a unique string with a
            maximum length of 20 characters.
    """
    class Meta:
        verbose_name = _('Public email domain')
        verbose_name_plural = _('Public email domains')

    domain = models.CharField(
        max_length=20, unique=True,
        null=False, blank=False,
        verbose_name=_("Domain")
    )

    def save(self, *args, **kwargs):
        """
        Overrides the save method to ensure the domain is stored in lowercase.
        """
        self.domain = self.domain.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns the string representation of the public email domain.
        """
        return self.domain


class Reminders(models.Model):
    """
    Model for storing reminder settings.

    This model is used to configure the interval at which reminders are checked.

    Attributes:
        check_interval (int): The interval in seconds to check for reminders,
            stored as a positive integer. Defaults to 300 seconds.
    """
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

    def __str__(self):
        """
        Returns a string representation of the reminder settings.
        """
        return "Settings"


class StopPhrase(models.Model):
    """
    Model representing a stop phrase.

    This model is used to store phrases that block the automatic generation
    of commercial requests from spam messages. It also tracks the last
    occurrence date of each phrase.

    Attributes:
        phrase (str): The stop phrase, stored as a unique string with a
            maximum length of 100 characters.
        last_occurrence_date (date): The date when the phrase was most recently
            encountered, updated automatically whenever the record is saved.
    """
    class Meta:
        verbose_name = _('Stop Phrase')
        verbose_name_plural = _('Stop Phrases')

    phrase = models.CharField(
        max_length=100, unique=True,
        null=False, blank=False,
        verbose_name=_("Phrase")
    )
    last_occurrence_date = models.DateField(
        auto_now=True,
        verbose_name=_("Last occurrence date"),
        help_text=_("Date of last occurrence of the phrase")
    )

    def hit(self):
        """
        Updates the last occurrence date of the stop phrase to the current date.
        """
        self.save()

    def __str__(self):
        """
        Returns the string representation of the stop phrase.
        """
        return self.phrase

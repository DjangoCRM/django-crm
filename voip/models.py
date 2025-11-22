from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def _ami_default(key, fallback):
    return settings.ASTERISK_AMI.get(key, fallback) if hasattr(settings, 'ASTERISK_AMI') else fallback


def ami_host_default():
    return _ami_default('HOST', '127.0.0.1')


def ami_port_default():
    return _ami_default('PORT', 5038)


def ami_username_default():
    return _ami_default('USERNAME', '')


def ami_secret_default():
    return _ami_default('SECRET', '')


def ami_ssl_default():
    return _ami_default('USE_SSL', False)


def ami_connect_timeout_default():
    return _ami_default('CONNECT_TIMEOUT', 5)


def ami_reconnect_delay_default():
    return _ami_default('RECONNECT_DELAY', 5)


def incoming_enabled_default():
    return getattr(settings, 'VOIP_INCOMING_CALL_ENABLED', True)


def incoming_poll_default():
    return getattr(settings, 'VOIP_INCOMING_POLL_INTERVAL_MS', 4000)


def incoming_ttl_default():
    return getattr(settings, 'VOIP_INCOMING_POPUP_TTL_MS', 20000)


class Connection(models.Model):

    TYPE_CHOICES = [
        ('pbx', _('PBX extension')),
        ('sip', _('SIP connection')),
        ('voip', _('Virtual phone number')),
    ]
    PROVIDER_CHOICES = (
        (backend['PROVIDER'], backend['PROVIDER']) 
        for backend in settings.VOIP
    )   
     
    type = models.CharField(
        max_length=4, default='pbx', blank=False,
        choices=TYPE_CHOICES,
        verbose_name=_("Type"),
    )
    active = models.BooleanField(
        default=False,
        verbose_name=_("Active"),
    )    
    number = models.CharField(
        max_length=30, null=False, blank=False,
        verbose_name=_("Number"),
    )
    callerid = models.CharField(
        max_length=30, null=False, blank=False,
        verbose_name=_("Caller ID"),
        help_text=_(
            'Specify the number to be displayed as \
            your phone number when you call'
        )
    )
    provider = models.CharField(
        max_length=100, null=False, blank=False,
        choices=PROVIDER_CHOICES,
        verbose_name=_("Provider"),
        help_text=_('Specify VoIP service provider')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        blank=True, null=True, 
        on_delete=models.CASCADE,
        verbose_name=_("Owner"),
        related_name="%(app_label)s_%(class)s_owner_related",
    )


class VoipSettings(models.Model):
    class Meta:
        verbose_name = _("VoIP settings")
        verbose_name_plural = _("VoIP settings")

    ami_host = models.CharField(
        max_length=128,
        default=ami_host_default,
        verbose_name=_("AMI host"),
    )
    ami_port = models.PositiveIntegerField(
        default=ami_port_default,
        verbose_name=_("AMI port"),
    )
    ami_username = models.CharField(
        max_length=128,
        default=ami_username_default,
        verbose_name=_("AMI username"),
    )
    ami_secret = models.CharField(
        max_length=255,
        blank=True,
        default=ami_secret_default,
        verbose_name=_("AMI secret"),
        help_text=_("Stored in plain text in DB; restrict admin access."),
    )
    ami_use_ssl = models.BooleanField(
        default=ami_ssl_default,
        verbose_name=_("AMI over SSL"),
    )
    ami_connect_timeout = models.PositiveIntegerField(
        default=ami_connect_timeout_default,
        verbose_name=_("AMI connect timeout, seconds"),
    )
    ami_reconnect_delay = models.PositiveIntegerField(
        default=ami_reconnect_delay_default,
        verbose_name=_("AMI reconnect delay, seconds"),
    )

    incoming_enabled = models.BooleanField(
        default=incoming_enabled_default,
        verbose_name=_("Show incoming pop-ups"),
    )
    incoming_poll_interval_ms = models.PositiveIntegerField(
        default=incoming_poll_default,
        verbose_name=_("Polling interval, ms"),
    )
    incoming_popup_ttl_ms = models.PositiveIntegerField(
        default=incoming_ttl_default,
        verbose_name=_("Popup duration, ms"),
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Use static string to avoid lazy proxy issues in admin log entries
        return "VoIP settings"

    @classmethod
    def get_solo(cls):
        obj = cls.objects.first()
        if obj:
            return obj
        return cls.objects.create()

    @property
    def ami_config(self):
        return {
            'HOST': self.ami_host,
            'PORT': self.ami_port,
            'USERNAME': self.ami_username,
            'SECRET': self.ami_secret,
            'USE_SSL': self.ami_use_ssl,
            'CONNECT_TIMEOUT': self.ami_connect_timeout,
            'RECONNECT_DELAY': self.ami_reconnect_delay,
        }

    @property
    def incoming_ui_config(self):
        return {
            'enabled': self.incoming_enabled,
            'poll_interval_ms': self.incoming_poll_interval_ms,
            'popup_ttl_ms': self.incoming_popup_ttl_ms,
        }


class IncomingCall(models.Model):
    class Meta:
        ordering = ('-created_at',)
        verbose_name = _("Incoming call")
        verbose_name_plural = _("Incoming calls")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='voip_incoming_calls',
        verbose_name=_("User"),
    )
    caller_id = models.CharField(
        max_length=64,
        verbose_name=_("Caller ID"),
    )
    client_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_("Client name"),
    )
    client_type = models.CharField(
        max_length=32,
        blank=True,
        default='',
        verbose_name=_("Object type"),
    )
    client_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Object ID"),
    )
    client_url = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_("Object URL"),
    )
    is_consumed = models.BooleanField(
        default=False,
        verbose_name=_("Shown to user"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )
    raw_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Payload"),
    )

    def __str__(self):
        return f"{self.caller_id} -> {self.user}"

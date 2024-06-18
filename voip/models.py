from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


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

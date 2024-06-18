from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


from common.models import Base1
from massmail.models.eml_accounts_queue import EmlAccountsQueue


class EmailAccount(Base1):
    class Meta:
        verbose_name = _('Email Account')
        verbose_name_plural = _('Email Accounts')

    name = models.CharField(
        max_length=100, null=False, blank=False,
        help_text=_("The name of the Email Account. For example Gmail")
    )
    main = models.BooleanField(
        default=False,
        help_text=_("Use this account for regular business correspondence.")
    )
    massmail = models.BooleanField(
        default=True,
        help_text=_("Allow to use this account for massmail.")
    )
    do_import = models.BooleanField(
        default=False,
        help_text=_("Import emails from this account.")
    )
    email_host = models.CharField(
        max_length=100, null=False, blank=False,
        help_text="The SMTP host."
    )
    imap_host = models.CharField(
        max_length=100, default='', blank=True,
        help_text=_("The IMAP host")
    )
    email_host_user = models.CharField(
        max_length=100, null=False, blank=False,
        help_text=_("The username to use to authenticate to the SMTP server.")
    )
    email_host_password = models.CharField(
        max_length=100, null=False, blank=False,
        help_text=_("The auth_password to use to authenticate to the SMTP server.")
    )
    email_app_password = models.CharField(
        max_length=100, default='', null=False, blank=True,
        help_text=_("The application password to use to authenticate to the SMTP server.")
    )
    email_port = models.SmallIntegerField(
        null=False, blank=False, default=25,
        help_text=_("Port to use for the SMTP server")
    )
    from_email = models.CharField(
        max_length=100, null=False, blank=False,
        help_text=_("The from_email field.")
    )
    email_use_tls = models.BooleanField(default=False)

    email_use_ssl = models.BooleanField(default=False)

    email_imail_ssl_certfile = models.CharField(
        max_length=200, default='', blank=True,
        help_text=_("If EMAIL_USE_SSL or EMAIL_USE_TLS is True, you can optionally specify \
        the path to a PEM-formatted certificate chain file to use for the SSL connection.")
    )
    email_imail_ssl_keyfile = models.CharField(
        max_length=200, default='', blank=True,
        help_text=_("If EMAIL_USE_SSL or EMAIL_USE_TLS is True, you can optionally specify \
        the path to a PEM-formatted private key file to use for the SSL connection.")
    )
    # OAuth 2.0
    refresh_token = models.CharField(
        max_length=200, default='', blank=True,
        help_text=_("OAuth 2.0 token for obtaining an access token.")
    )    

    report = models.TextField(blank=True, default='')

    creation_date = models.DateTimeField(auto_now_add=True)

    update_date = models.DateTimeField(auto_now=True)

    today_date = models.DateField(null=True, blank=True)

    today_count = models.PositiveIntegerField(default=0, blank=True)

    start_incoming_uid = models.PositiveIntegerField(default=1, blank=True)

    start_sent_uid = models.PositiveIntegerField(default=1, blank=True)

    inbox_uidvalidity = models.PositiveIntegerField(default=0)

    inbox_uidnext = models.PositiveIntegerField(default=0)

    sent_uidvalidity = models.PositiveIntegerField(default=0)

    sent_uidnext = models.PositiveIntegerField(default=0)

    last_import_dt = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("DateTime of last import")
    )
    co_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_("Co-owner"),
        related_name="%(app_label)s_%(class)s_co_owner_related",
    )    

    def clean(self):
        data = dict()
        if self.do_import and not self.imap_host:
            data['imap_host'] = _("Specify the imap host")
        if data:
            raise ValidationError(data)
        super().clean()

    def delete(self, *args, **kwargs):
        try:
            queue_obj = EmlAccountsQueue.objects.get(owner=self.owner)
            queue_obj.remove_id(self.pk)
        except ObjectDoesNotExist:
            pass
        super(EmailAccount, self).delete(*args, **kwargs)

    def __str__(self):
        return "%s (%s)" % (self.name, self.email_host_user)

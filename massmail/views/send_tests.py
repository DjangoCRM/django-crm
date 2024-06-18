from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.utils.translation import gettext as _
from smtplib import SMTPRecipientsRefused
from massmail.utils.email_creators import create_test_email
from massmail.models import EmailAccount, EmlMessage

NEED_TWO_EML_ACCOUNTS = 'To send a test message you need to register at least two email accounts.'


def send_test(request, message_id):
    mg = EmlMessage.objects.get(id=message_id)
    eas = EmailAccount.objects.filter(owner=mg.owner, massmail=True)
    if eas.count() < 2:
        messages.error(
            request, 
            _(NEED_TWO_EML_ACCOUNTS)
        )
        return HttpResponseRedirect(
            reverse('site:massmail_emlmessage_change', args=(message_id,))
        )
    ea_list = list(eas) 
    site = Site.objects.get_current()
    extra_context = {
        'first_name': '%s' % request.user.username,
        'unsubscribe_url': site.domain
    }
    for ea in ea_list[1:]:
        msg = create_test_email(
            request,
            message_id,
            ea_list[0],
            to=[ea.email_host_user],
            extra_context=extra_context,
            force_multipart=True,
            inline_images=True
        )
        try:
            msg.send(fail_silently=False) 
        except SMTPRecipientsRefused as e:
            messages.error(request, f'Massmail: {e}')

    email_accounts = ', '.join([ea.email_host_user for ea in ea_list[1:]])
    messages.success(
        request, 
        _(f'The Email test has been sent to {email_accounts}')
    )
    return HttpResponseRedirect(
        reverse('site:massmail_emlmessage_change', args=(message_id,))
    )

from django.contrib import messages
from massmail.models import MailingOut
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _


def send_failed_recipients(request, object_id):
    mo = MailingOut.objects.get(id=object_id)
    mo.status = 'A'
    mo.move_to_recipient_ids()
    messages.success(
            request, 
            _('Failed recipients has been returned to the massmail successfully.')
    )    
    return HttpResponseRedirect(reverse('site:massmail_mailingout_changelist'))      
    
    
    
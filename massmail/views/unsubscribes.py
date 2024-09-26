from django.conf import settings
from django.http import HttpResponseRedirect

from massmail.models import MassContact


def unsubscribe(request, recipient_uuid) -> HttpResponseRedirect:
    try:
        mc = MassContact.objects.get(
            uuid=recipient_uuid
        )
    except MassContact.DoesNotExist:
        return HttpResponseRedirect(settings.UNSUBSCRIBE_URL)

    mc.massmail=False
    mc.save(update_fields=['massmail'])
    counterparty = mc.content_object
    counterparty.massmail = False
    counterparty.save(update_fields=['massmail'])

    return HttpResponseRedirect(settings.UNSUBSCRIBE_URL)

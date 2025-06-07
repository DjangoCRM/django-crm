from django.http import HttpResponseRedirect

from massmail.models import MassContact
from settings.models import MassmailSettings


def unsubscribe(request, recipient_uuid) -> HttpResponseRedirect:
    """Unsubscribe a recipient from mass mailings."""

    massmail_settings = MassmailSettings.objects.get(id=1)
    try:
        mc = MassContact.objects.get(
            uuid=recipient_uuid
        )
    except MassContact.DoesNotExist:
        return HttpResponseRedirect(massmail_settings.unsubscribe_url)

    mc.massmail=False
    mc.save(update_fields=['massmail'])
    counterparty = mc.content_object
    counterparty.massmail = False
    counterparty.save(update_fields=['massmail'])

    return HttpResponseRedirect(massmail_settings.unsubscribe_url)

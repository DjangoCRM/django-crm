from massmail.models import MassContact
from django.http import HttpResponseRedirect
from django.conf import settings


def unsubscribe(request, recipient_uuid):
    MassContact.objects.filter(
        uuid=recipient_uuid
    ).update(massmail=False)
    return HttpResponseRedirect(settings.UNSUBSCRIBE_URL)

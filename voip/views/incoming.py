from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.timezone import localtime
from django.views import View

from voip.models import IncomingCall


class IncomingCallPollView(LoginRequiredMixin, View):
    """Return the latest unconsumed incoming call for the current user."""

    def get(self, request):
        call = IncomingCall.objects.filter(
            user=request.user,
            is_consumed=False
        ).order_by('-created_at').first()

        if not call:
            return JsonResponse({'incoming_call': None})

        call.is_consumed = True
        call.save(update_fields=['is_consumed'])

        payload = {
            'id': call.id,
            'caller_id': call.caller_id,
            'client_name': call.client_name,
            'client_type': call.client_type,
            'client_id': call.client_id,
            'client_url': call.client_url,
            'created_at': localtime(call.created_at).isoformat(),
        }
        return JsonResponse({'incoming_call': payload})

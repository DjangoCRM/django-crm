from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from voip.models import VoipSettings


class VoipStatusView(APIView):
    permission_classes = [IsAuthenticated]
    """Return VoIP status and configuration for the current user."""

    def get(self, request):
        try:
            # Check if there are any VoIP settings configured (global settings)
            voip_settings = VoipSettings.objects.first()

            # Check for any pending incoming calls for current user
            from voip.models import IncomingCall
            pending_calls = IncomingCall.objects.filter(
                user=request.user,
                is_consumed=False
            ).exists()

            # Return status based on configuration
            status_data = {
                'status': 'enabled' if voip_settings else 'disabled',
                'configured': bool(voip_settings),
                'user_id': request.user.id,
                'username': request.user.username,
                'has_incoming_calls': pending_calls,
                'voip_server_configured': bool(voip_settings and voip_settings.ami_host)
            }

            return Response(status_data)

        except Exception as e:
            return Response({
                'status': 'error',
                'configured': False,
                'message': f'Error retrieving VoIP status: {str(e)}',
                'user_id': request.user.id
            }, status=500)
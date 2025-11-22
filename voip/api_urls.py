from django.urls import path
from voip.views.status import VoipStatusView

app_name = 'voip_api'

urlpatterns = [
    path('status/',
         VoipStatusView.as_view(),
         name='voip_status'
         ),
]
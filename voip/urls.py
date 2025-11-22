# from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from voip.views.callback import ConnectionView
from voip.views.incoming import IncomingCallPollView
from voip.views.jssip import JsSipClientView
from voip.views.voipwebhook import VoIPWebHook

app_name = 'voip'


urlpatterns = [
    path('get-callback/',
         ConnectionView.as_view(),
         name='get_callback'
         ),    
    path('zd/',
         VoIPWebHook.as_view(),
         name='voip-zadarma-pbx-notification'
         ),
    path('api/incoming-call/',
         IncomingCallPollView.as_view(),
         name='voip_incoming_call_poll'
         ),
    path('client/',
         JsSipClientView.as_view(),
         name='voip_jssip_client'
         ),
]

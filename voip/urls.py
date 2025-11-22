# from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from voip.views.callback import ConnectionView
from voip.views.incoming import IncomingCallPollView
from voip.views.jssip import JsSipClientView
from voip.views.voipwebhook import VoIPWebHook
from voip.views.onlinepbx_webhook import OnlinePBXWebHook
from voip.views.onlinepbx_api import OnlinePBXAuthView, OnlinePBXCallView

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
     path('obx/',
          OnlinePBXWebHook.as_view(),
          name='voip-onlinepbx-webhook'
          ),
    path('client/',
         JsSipClientView.as_view(),
         name='voip_jssip_client'
         ),
     # OnlinePBX management endpoints
     path('obx/auth/',
          OnlinePBXAuthView.as_view(),
          name='voip-onlinepbx-auth'
          ),
     path('obx/call/',
          OnlinePBXCallView.as_view(),
          name='voip-onlinepbx-call'
          ),
]

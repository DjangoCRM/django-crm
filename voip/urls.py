# from django.contrib.auth.decorators import login_required
# from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from voip.views.callback import ConnectionView
from voip.views.voipwebhook import VoIPWebHook


urlpatterns = [
    path('get-callback/',
         ConnectionView.as_view(),
         name='get_callback'
         ),    
    path('zd/',
         VoIPWebHook.as_view(),
         name='voip-zadarma-pbx-notification'
         ),
]

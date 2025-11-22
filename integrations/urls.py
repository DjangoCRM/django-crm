from django.urls import path
from .views import TelegramWebhookView, InstagramWebhookView

from .views_sms import SendSMSView

urlpatterns = [
    path('telegram/webhook/<str:secret>/', TelegramWebhookView.as_view(), name='telegram-webhook'),
    path('instagram/webhook/', InstagramWebhookView.as_view(), name='instagram-webhook'),
    path('sms/send/', SendSMSView.as_view(), name='send-sms'),
]

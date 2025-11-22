from django.urls import path
from .views import TelegramWebhookView, InstagramWebhookView

urlpatterns = [
    path('telegram/webhook/<str:secret>/', TelegramWebhookView.as_view(), name='telegram-webhook'),
    path('instagram/webhook/', InstagramWebhookView.as_view(), name='instagram-webhook'),
]

from django.urls import path

from .views import WebhookReceiver, test_webhook_decorator_view

urlpatterns = [
    path("receiver/", WebhookReceiver.as_view(), name="webhook-receiver"),
    path("trigger/", test_webhook_decorator_view, name="test-webhook-decorator"),
]

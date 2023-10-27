import json

from django.contrib.auth import get_user_model

from rest_framework import views
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from .utils import WebhookHandler
from .decorators import emit_webhook

User = get_user_model()


class WebhookReceiver(views.APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        print("here===========")
        secret = "ff203910-eef6-4f11-ad94-126ec7e1ee12"
        request_signature = request.headers.get("X-Signature")
        signature = WebhookHandler.header_signature(secret, json.dumps(request.data))
        if request_signature == signature:
            print(request.data)
        return Response({"message": "done"})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def test_webhook_decorator_view(request, *args, **kwargs):
    test_webhook_decorator()
    return Response({"message": "done"})


@emit_webhook
def test_webhook_decorator(*args, **kwargs):
    event = "test.hook"
    user = User.objects.get(id=1)
    data = {"test": "test_event_data"}
    return event, user, data

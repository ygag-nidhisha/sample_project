import json, logging

from django.contrib.auth import get_user_model

from rest_framework import views
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from .tasks import TriggerWebhook
from .decorators import emit_webhook

User = get_user_model()
# get logger instance
logger = logging.getLogger(__name__)


class WebhookReceiver(views.APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        print("here===========")
        print(request.data)
        secret = "ff203910-eef6-4f11-ad94-126ec7e1ee12"
        request_signature = request.headers.get("X-Signature")
        signature = TriggerWebhook.header_signature(secret, json.dumps(request.data))
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
    logger.info("test webhook function initiated")
    event = "test.hook"
    # user = User.objects.get(id=1)
    user = None
    data = {"test": "test_event_data"}
    return event, user, data, True

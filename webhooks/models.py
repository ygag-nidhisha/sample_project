import uuid

from django.db import models
from django.contrib.auth import get_user_model

from webhooks.settings import webhook_settings

User = get_user_model()


class AbstractDateModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Webhook(AbstractDateModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="webhook_owner"
    )
    url = models.URLField(max_length=2048, unique=True)
    secret = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.BooleanField(default=False)

    class Meta:
        unique_together = ["user", "url"]


class WebhookEvents(AbstractDateModel):
    EVENT_CHOICES = [(e, e) for e in webhook_settings.WEBHOOK_EVENTS]

    event = models.CharField(max_length=200, choices=EVENT_CHOICES)
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE)

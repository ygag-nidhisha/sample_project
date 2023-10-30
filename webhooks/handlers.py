import logging

from celery import group
from django.contrib.auth import get_user_model
from django.db.models.base import ModelBase
from django.forms.models import model_to_dict
from django.core.exceptions import ImproperlyConfigured

from .settings import webhook_settings
from .tasks import trigger_webhook
from .utils import get_webhook, chunks

User = get_user_model()
# Get an instance of a logger
logger = logging.getLogger(__name__)


# The `WebhookHandler` class is responsible for validating and sending webhooks for specific events
# related to a model.
class WebhookHandler:
    @staticmethod
    def validate_event_key(event):
        """
        The function `validate_event_key` checks if an event is available in a list of webhook events
        and raises an exception if it is not.

        :param event: The `event` parameter is a string representing an event
        :return: the event parameter after validating it.
        """
        if event and event not in webhook_settings.WEBHOOK_EVENTS:
            raise ImproperlyConfigured(f"{event} not available in WEBHOOK_EVENTS")
        return event

    def get_event(self, instance, method):
        """
        The function `get_event` retrieves the event name based on the instance, method, and event
        mapping.

        :param instance: The `instance` parameter refers to an instance of a model class. It represents
        a specific object or record in the database
        :param method: The `method` parameter is a string that represents the method or action that is
        being performed on the instance. It could be a CRUD operation like "create", "update", "delete",
        or any other custom action
        :return: The method is returning the event name that matches the given instance and method.
        """
        event_mapping = webhook_settings.WEBHOOK_EVENT_MAPPING
        model_path = f"{instance.__class__.__module__}.{instance.__class__.__name__}"
        event_name = None
        for event, data in event_mapping.items():
            if data.get("model_path") == model_path and data.get("method") == method:
                event_name = event
                break
        return self.validate_event_key(event_name)

    def get_user(self):
        return User.objects.get(id=1)

    def send_model_webhook(self, instance: ModelBase, method: str) -> None:
        """
        The function `send_model_webhook` sends a webhook with event data and user information, based on
        the provided instance and method.

        :param instance: The `instance` parameter is an instance of a model class. It represents a
        specific object or record in the database
        :type instance: ModelBase
        :param method: The "method" parameter in the "send_model_webhook" function is a string that
        represents the method or action being performed on the model instance. It is used to determine
        the event that will be triggered for the webhook
        :type method: str
        """
        event = self.get_event(instance, method)
        if event:
            send_to_all = False
            try:
                user = getattr(instance, instance.__class__.OWNER_FIELD)
            except AttributeError:
                if event in webhook_settings.WEBHOOK_SEND_TO_ALL_EVENTS:
                    send_to_all = True
                user = None
            self.send_webhook(event, user, model_to_dict(instance), send_to_all)
        else:
            logger.debug("No event specified")

    def send_webhook(self, event, user, data, send_to_all):
        if event and (user or send_to_all):
            single_obj = False
            filter_context = {}
            filter_context["webhookevents__event"] = event
            if user and not send_to_all:
                filter_context["user"] = user
                single_obj = True
            webhooks = get_webhook(filter_context=filter_context)
            if single_obj:
                webhooks = webhooks.last()
                webhooks = [webhooks.id] if webhooks else []
            else:
                webhooks = webhooks.values_list("id", flat=True)

            if webhooks:
                task_group = group(
                    trigger_webhook.s(event, webhook_list, data)
                    for webhook_list in list(chunks(webhooks, 10))
                )
                task_group.apply_async()

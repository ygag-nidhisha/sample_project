import hmac, hashlib, json, requests
from sys import modules
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.db.models.base import ModelBase
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder


from .models import Webhook
from .settings import webhook_settings
from importlib import import_module

User = get_user_model()


def get_webhook_model():
    webhook_model = webhook_settings.WEBHOOK_MODEL
    model = None
    try:
        msg = f"Could not import {webhook_model!r}"
        try:
            module_path, class_name = webhook_model.rsplit(".", 1)
        except ValueError as error:
            raise ValidationError(
                f"{msg}. {webhook_model!r} doesn't look like a module path."
            ) from error

        if module_path not in modules or (
            # Module is not fully initialized.
            getattr(modules[module_path], "__spec__", None) is not None
            and getattr(modules[module_path].__spec__, "_initializing", False) is True
        ):
            try:
                import_module(module_path)
            except ImportError as error:
                raise ValidationError(
                    f"{msg}. {error.__class__.__name__!r}: {error}."
                ) from error

        try:
            model = getattr(modules[module_path], class_name)
        except AttributeError as error:
            raise ValidationError(
                f"{msg}. Module {module_path!r} does not define {class_name!r}."
            ) from error

        if not isinstance(model, ModelBase):
            raise ValidationError(f"{webhook_model!r} is not a django model.")
    except ValidationError as error:
        raise ImproperlyConfigured(
            f"{webhook_model!r} is not a model that can be imported."
        ) from error

    if not issubclass(model, Webhook):
        raise ImproperlyConfigured(
            f"{webhook_model!r} is not a subclass of a {model.__module__}.{model.__name__}."
        )

    return model


class WebhookHandler:
    def get_webhook(self, event, user):
        webhook_model = get_webhook_model()
        webhook = webhook_model.objects.filter(
            user=user, webhookevents__event=event
        ).last()
        return webhook

    def get_event(self, instance, method):
        event_mapping = webhook_settings.WEBHOOK_EVENT_MAPPING
        model_path = f"{instance.__class__.__module__}.{instance.__class__.__name__}"
        event_name = None
        for event, data in event_mapping.items():
            if data.get("model_path") == model_path and data.get("method") == method:
                event_name = event
                break
        return event_name

    def get_user(self):
        return User.objects.get(id=1)

    def send_model_webhook(self, instance: ModelBase, method: str):
        event = self.get_event(instance, method)
        self.trigger_webhook(
            event=event, user=self.get_user(), data=model_to_dict(instance)
        )

    def get_headers(self, webhook, payload):
        headers = {"content-type": "application/json"}
        headers["X-Signature"] = self.header_signature(str(webhook.secret), payload)
        print(headers)
        return headers

    @staticmethod
    def header_signature(secret, payload):
        signature = hmac.new(
            secret.encode("utf-8"), payload.encode("utf-8"), digestmod=hashlib.sha256
        ).hexdigest()
        return signature

    def trigger_webhook(self, event, user, data):
        if event:
            if event not in webhook_settings.WEBHOOK_EVENTS:
                raise ImproperlyConfigured(f"{event} not available in WEBHOOK_EVENTS")
            webhook = self.get_webhook(event, user)
            payload = json.dumps({"event": event, "data": data}, cls=DjangoJSONEncoder)
            if webhook:
                webhook_response = requests.post(
                    url=webhook.url,
                    data=payload,
                    timeout=5,
                    headers=self.get_headers(webhook, payload),
                )
                if webhook_response.status_code // 100 == 2:
                    print("Webhook success")
                else:
                    print("Some error occured")
                    print(webhook_response.content)
            else:
                print(f"{event} not subscribed by this user")
        else:
            print("No event")

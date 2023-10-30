from django.db.models import signals
from django.dispatch import receiver
from django.db.models.base import ModelBase

from .handlers import WebhookHandler


@receiver(signals.post_save, dispatch_uid="webhook_post_save")
def webhook_post_save_receiver(sender: ModelBase, **kwargs) -> None:
    """
    The receiver function `webhook_post_save_receiver` sends a model webhook with the "create/update" method when a model
    instance is created/updated.

    :param sender: The `sender` parameter is the model class that triggered the webhook delete event. It
    is a subclass of `ModelBase`, which is typically the base class for all Django models
    :type sender: ModelBase
    """
    WebhookHandler().send_model_webhook(
        instance=kwargs.get("instance"),
        method="create" if kwargs["created"] else "update",
    )


@receiver(signals.post_delete, dispatch_uid="webhook_post_delete")
def webhook_post_delete_receiver(sender: ModelBase, **kwargs) -> None:
    """
    The receiver function `webhook_post_delete_receiver` sends a model webhook with the "delete" method when a model
    instance is deleted.

    :param sender: The `sender` parameter is the model class that triggered the webhook delete event. It
    is a subclass of `ModelBase`, which is typically the base class for all Django models
    :type sender: ModelBase
    """
    WebhookHandler().send_model_webhook(
        instance=kwargs.get("instance"),
        method="delete",
    )

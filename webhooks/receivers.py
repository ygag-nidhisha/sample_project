from django.db.models import signals
from django.dispatch import receiver
from django.db.models.base import ModelBase

from .utils import WebhookHandler


@receiver(signals.post_save, dispatch_uid="webhook_post_save")
def webhook_post_save_receiver(sender: ModelBase, **kwargs) -> None:
    print(sender)
    # print(sender.__name__)
    # print(kwargs)
    # print("kwargs============")
    # print(kwargs.get("instance").__class__.__name__)
    # print("kwargs============")
    WebhookHandler().send_model_webhook(
        instance=kwargs.get("instance"),
        method="create" if kwargs["created"] else "update",
    )


# @receiver(signals.post_delete, dispatch_uid=webhook_settings.DISPATCH_UID_POST_DELETE)
# def webhook_delete_handler(sender: ModelBase, **kwargs) -> None:
#     kwargs: PostDeleteData
#     webhook_handler(instance=kwargs["instance"], method="DELETE")

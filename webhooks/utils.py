from sys import modules
from importlib import import_module
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.db.models.base import ModelBase

from .models import Webhook
from .settings import webhook_settings

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


def get_webhook(filter_params=[], filter_context={}, order_by="id", single_obj=False):
    """
    The function retrieves webhooks from a webhook model based on specified filter parameters and order.

    :param filter_params: The `filter_params` parameter is a list of filter conditions that you want to
    apply to the query. Each filter condition is a tuple containing the field name, lookup type, and
    value. For example, `filter_params=[('status', 'exact', 'active'), ('created_at', 'gte
    :param filter_context: The `filter_context` parameter is a dictionary that contains the filter
    conditions to be applied to the query. Each key-value pair in the dictionary represents a filter
    condition, where the key is the field name and the value is the value to be matched
    :param order_by: The "order_by" parameter is used to specify the field by which the results should
    be ordered. By default, it is set to "id", which means the results will be ordered by the webhook's
    ID in ascending order. However, you can pass any valid field name of the webhook model to, defaults
    to id (optional)
    :return: a queryset of webhook objects.
    """
    webhook_model = get_webhook_model()
    webhook = webhook_model.objects.filter(*filter_params, **filter_context).order_by(
        order_by
    )
    return webhook


def chunks(input_list, chunk_size):
    """
    The function "chunks" takes an input list and a chunk size, and yields chunks of the input list with
    the specified size.

    :param input_list: The input_list parameter is a list of elements that you want to divide into
    chunks
    :param chunk_size: The chunk_size parameter determines the size of each chunk or sub-list that will
    be created from the input_list. It specifies how many elements should be included in each chunk
    """
    for i in range(0, len(input_list), chunk_size):
        yield input_list[i : i + chunk_size]

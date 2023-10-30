from .handlers import WebhookHandler


def emit_webhook(func):
    """
    The `emit_webhook` function is a decorator that wraps a function and triggers a webhook with the
    event, user ID, and data returned by the wrapped function.

    :param func: The `func` parameter is a function that will be wrapped by the `emit_webhook` decorator
    :return: The function `wrapper` is being returned.
    """

    def wrapper(*args, **kwargs):
        event, user, data, send_to_all = func(*args, **kwargs)
        handler = WebhookHandler()
        event = handler.validate_event_key(event)
        return handler.send_webhook(event, user.id if user else None, data, send_to_all)

    return wrapper

from .utils import WebhookHandler


def emit_webhook(func):
    def wrapper(*args, **kwargs):
        event, user, data = func(*args, **kwargs)
        return WebhookHandler().trigger_webhook(event, user, data)

    return wrapper

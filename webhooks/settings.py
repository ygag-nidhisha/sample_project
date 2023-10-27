from django.conf import settings


DEFAULTS = {
    "WEBHOOK_MODEL": "webhooks.models.Webhook",
    "WEBHOOK_EVENTS": [],
    "WEBHOOK_EVENT_MAPPING": {},
}


class WebhookSettings:
    def __init__(self, user_settings=None, default_settings=None) -> None:
        if user_settings:
            self._user_settings = user_settings
        self.defaults = default_settings or DEFAULTS

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "WEBHOOK_SETTINGS", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        setattr(self, attr, val)
        return val


webhook_settings = WebhookSettings(None, DEFAULTS)

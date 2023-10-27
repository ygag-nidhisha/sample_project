from django.contrib import admin

from .models import Webhook, WebhookEvents


class WebhookEventsInline(admin.TabularInline):
    model = WebhookEvents
    extra = 0
    list_display = ["event"]


class WebhookAdmin(admin.ModelAdmin):
    inlines = [
        WebhookEventsInline,
    ]
    list_display = ["user", "url", "secret"]
    readonly_fields = ["secret"]


admin.site.register(Webhook, WebhookAdmin)

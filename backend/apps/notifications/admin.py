"""Xabarnoma jurnali — texnik boʻlmagan odam ham koʻra oladi (ADR-006)."""

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from apps.notifications.models import NotificationLog

STATUS_COLORS = {
    NotificationLog.Status.SENT: "#16a34a",
    NotificationLog.Status.PENDING: "#f59e0b",
    NotificationLog.Status.FAILED: "#dc2626",
    NotificationLog.Status.ABANDONED: "#94a3b8",
}


@admin.register(NotificationLog)
class NotificationLogAdmin(ModelAdmin):
    list_display = ("created_at", "channel", "template_key", "target", "status_badge", "attempts")
    list_filter = ("status", "channel")
    search_fields = ("template_key", "target", "last_error")
    date_hierarchy = "created_at"
    readonly_fields = (
        "channel",
        "template_key",
        "target",
        "content_type",
        "object_id",
        "status",
        "attempts",
        "last_error",
        "payload",
        "sent_at",
        "next_retry_at",
        "created_at",
    )

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px">{}</span>',
            STATUS_COLORS.get(obj.status, "#64748b"),
            obj.get_status_display(),
        )

    actions = ("resend",)

    @admin.action(description="Qayta yuborish")
    def resend(self, request, queryset):
        from apps.notifications.services.notify import _deliver

        sent = 0
        for log in queryset:
            text = (log.payload or {}).get("text")
            if text and _deliver(log, text):
                sent += 1
        self.message_user(request, f"{sent} ta xabar qayta yuborildi")

    def has_add_permission(self, request):
        return False

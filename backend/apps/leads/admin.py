"""Murojaatlar inbox'i."""

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from apps.leads.models import Lead

STATUS_COLORS = {
    Lead.Status.NEW: "#f59e0b",
    Lead.Status.IN_PROGRESS: "#0e7c86",
    Lead.Status.WON: "#16a34a",
    Lead.Status.LOST: "#94a3b8",
    Lead.Status.SPAM: "#dc2626",
}


@admin.register(Lead)
class LeadAdmin(ModelAdmin):
    list_display = ("created_at_short", "name", "phone_link", "kind", "service", "status_badge")
    list_filter = ("status", "kind", "service")
    search_fields = ("name", "phone", "message")
    date_hierarchy = "created_at"
    autocomplete_fields = ("service",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "consent_given_at",
        "ip_hash",
        "source_page",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "locale",
    )
    actions = ("mark_in_progress", "mark_won", "mark_lost", "mark_spam")

    @admin.display(description="Sana", ordering="created_at")
    def created_at_short(self, obj):
        return obj.created_at.strftime("%d.%m.%Y %H:%M")

    @admin.display(description="Telefon")
    def phone_link(self, obj):
        return format_html('<a href="tel:{}">{}</a>', obj.phone, obj.phone)

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px">{}</span>',
            STATUS_COLORS.get(obj.status, "#64748b"),
            obj.get_status_display(),
        )

    def _set_status(self, request, queryset, status, label):
        updated = queryset.update(status=status)
        self.message_user(request, f"{updated} ta murojaat → {label}")

    @admin.action(description="Ishlanmoqda deb belgilash")
    def mark_in_progress(self, request, queryset):
        self._set_status(request, queryset, Lead.Status.IN_PROGRESS, "ishlanmoqda")

    @admin.action(description="Yutildi deb belgilash")
    def mark_won(self, request, queryset):
        self._set_status(request, queryset, Lead.Status.WON, "yutildi")

    @admin.action(description="Yoʻqotildi deb belgilash")
    def mark_lost(self, request, queryset):
        self._set_status(request, queryset, Lead.Status.LOST, "yoʻqotildi")

    @admin.action(description="Spam deb belgilash")
    def mark_spam(self, request, queryset):
        self._set_status(request, queryset, Lead.Status.SPAM, "spam")

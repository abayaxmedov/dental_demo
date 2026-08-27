"""Core admin: sayt sozlamalari, ish vaqti, counterlar."""

from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from apps.core.models import ClinicSettings, Redirect, StatCounter, WorkingHours


@admin.register(ClinicSettings)
class ClinicSettingsAdmin(TabbedTranslationAdmin, ModelAdmin):
    fieldsets = (
        (
            "Klinika",
            {"fields": ("name", "tagline", "about_short", "legal_entity_name", "license_text")},
        ),
        (
            "Brending",
            {
                "fields": (
                    "logo",
                    "logo_dark",
                    "favicon",
                    "brand_color",
                    "accent_color",
                    "ink_color",
                    "surface_color",
                    "font_pair",
                )
            },
        ),
        (
            "Aloqa",
            {
                "fields": (
                    "phone_primary",
                    "phone_secondary",
                    "email",
                    "telegram_username",
                    "telegram_channel_url",
                    "instagram_url",
                    "facebook_url",
                    "youtube_url",
                )
            },
        ),
        (
            "Manzil va xarita",
            {
                "fields": (
                    "address",
                    "map_lat",
                    "map_lng",
                    "map_zoom",
                    "yandex_maps_url",
                    "two_gis_url",
                )
            },
        ),
        ("Sozlamalar", {"fields": ("prices_visible", "booking_enabled")}),
        (
            "SEO va analytics",
            {
                "classes": ("collapse",),
                "fields": (
                    "default_meta_title",
                    "default_meta_description",
                    "metrika_id",
                    "ga4_id",
                    "yandex_verification",
                    "google_verification",
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        # Singleton — faqat bitta yozuv
        return not ClinicSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(WorkingHours)
class WorkingHoursAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = ("get_weekday_display", "opens", "closes", "is_closed", "note")
    list_editable = ("opens", "closes", "is_closed")
    list_display_links = ("get_weekday_display",)
    ordering = ("weekday",)

    @admin.display(description="Hafta kuni", ordering="weekday")
    def get_weekday_display(self, obj):
        return obj.get_weekday_display()

    def has_add_permission(self, request):
        return WorkingHours.objects.count() < 7


@admin.register(StatCounter)
class StatCounterAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = ("label", "value", "suffix", "order", "is_active")
    list_editable = ("value", "suffix", "order", "is_active")
    ordering = ("order",)


@admin.register(Redirect)
class RedirectAdmin(ModelAdmin):
    list_display = ("old_path", "new_path", "status", "hits", "last_hit_at")
    list_filter = ("status",)
    search_fields = ("old_path", "new_path")
    readonly_fields = ("hits", "last_hit_at")

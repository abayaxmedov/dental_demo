"""Shifokorlar admini."""

from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin, TabularInline

from apps.team.models import Doctor, DoctorSchedule, TimeOff


class DoctorScheduleInline(TabularInline):
    model = DoctorSchedule
    extra = 0
    fields = ("weekday", "start_time", "end_time", "slot_minutes", "break_start", "break_end")


@admin.register(Doctor)
class DoctorAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = (
        "thumb",
        "full_name",
        "specialization",
        "experience_years",
        "is_bookable",
        "is_active",
        "order",
    )
    list_display_links = ("thumb", "full_name")
    list_editable = ("is_bookable", "is_active", "order")
    list_filter = ("is_bookable", "is_active")
    search_fields = ("full_name", "specialization")
    inlines = [DoctorScheduleInline]
    fieldsets = (
        (None, {"fields": ("full_name", "slug", "specialization", "bio")}),
        ("Rasm", {"fields": ("photo", "photo_alt")}),
        (
            "Malaka",
            {"fields": ("experience_years", "education", "certificates", "languages_spoken")},
        ),
        ("Koʻrinish", {"fields": ("is_bookable", "is_active", "order", "telegram_username")}),
        (
            "SEO",
            {"classes": ("collapse",), "fields": ("meta_title", "meta_description", "og_image")},
        ),
    )

    @admin.display(description="")
    def thumb(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:38px;height:38px;border-radius:50%;object-fit:cover">',
                obj.photo.url,
            )
        return format_html(
            '<div style="width:38px;height:38px;border-radius:50%;background:#e2e8f0"></div>'
        )


@admin.register(TimeOff)
class TimeOffAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = ("doctor_or_clinic", "starts_at", "ends_at", "reason")
    list_filter = ("doctor",)
    date_hierarchy = "starts_at"

    @admin.display(description="Kim", ordering="doctor")
    def doctor_or_clinic(self, obj):
        return obj.doctor or "Butun klinika"

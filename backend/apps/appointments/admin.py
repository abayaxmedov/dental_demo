"""
Qabullar admini — registratura xodimining asosiy ish joyi (R-14).
Default koʻrinish: bugungi qabullar.
"""

from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from apps.appointments.models import Appointment, AppointmentStatus, InvalidTransition


class TodayFilter(admin.SimpleListFilter):
    """Registratura uchun eng kerakli filtr — birinchi oʻrinda turadi."""

    title = "Vaqt"
    parameter_name = "when"

    def lookups(self, request, model_admin):
        return (
            ("today", "Bugun"),
            ("tomorrow", "Ertaga"),
            ("week", "Shu hafta"),
            ("past", "Oʻtgan"),
        )

    def queryset(self, request, queryset):
        now = timezone.localtime()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if self.value() == "today":
            return queryset.filter(
                starts_at__gte=start_of_day, starts_at__lt=start_of_day + timezone.timedelta(days=1)
            )
        if self.value() == "tomorrow":
            d = start_of_day + timezone.timedelta(days=1)
            return queryset.filter(starts_at__gte=d, starts_at__lt=d + timezone.timedelta(days=1))
        if self.value() == "week":
            return queryset.filter(
                starts_at__gte=start_of_day, starts_at__lt=start_of_day + timezone.timedelta(days=7)
            )
        if self.value() == "past":
            return queryset.filter(starts_at__lt=now)
        return queryset


STATUS_COLORS = {
    AppointmentStatus.PENDING: "#f59e0b",
    AppointmentStatus.CONFIRMED: "#0e7c86",
    AppointmentStatus.COMPLETED: "#16a34a",
    AppointmentStatus.NO_SHOW: "#dc2626",
    AppointmentStatus.CANCELLED_BY_PATIENT: "#94a3b8",
    AppointmentStatus.CANCELLED_BY_CLINIC: "#94a3b8",
}


@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    list_display = (
        "starts_at_local",
        "patient_name",
        "phone_link",
        "doctor",
        "service",
        "status_badge",
        "code",
    )
    list_filter = (TodayFilter, "status", "doctor", "source")
    search_fields = ("patient_name", "phone", "code")
    date_hierarchy = "starts_at"
    autocomplete_fields = ("doctor", "service")
    readonly_fields = (
        "code",
        "cancel_token",
        "created_at",
        "updated_at",
        "consent_given_at",
        "consent_text_version",
        "ip_hash",
        "user_agent",
    )
    actions = ("action_confirm", "action_complete", "action_no_show")
    fieldsets = (
        ("Bemor", {"fields": ("patient_name", "phone", "email", "comment")}),
        (
            "Qabul",
            {"fields": ("doctor", "service", "starts_at", "ends_at", "status", "source", "locale")},
        ),
        (
            "Texnik",
            {
                "classes": ("collapse",),
                "fields": (
                    "code",
                    "cancel_token",
                    "consent_given_at",
                    "consent_text_version",
                    "ip_hash",
                    "user_agent",
                    "reminder_24h_sent_at",
                    "reminder_2h_sent_at",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(description="Vaqt", ordering="starts_at")
    def starts_at_local(self, obj):
        return timezone.localtime(obj.starts_at).strftime("%d.%m.%Y  %H:%M")

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

    def _bulk_transition(self, request, queryset, target, label):
        ok = failed = 0
        for appt in queryset:
            try:
                appt.transition_to(target)
                ok += 1
            except InvalidTransition:
                failed += 1
        if ok:
            self.message_user(request, f"{ok} ta qabul → {label}", messages.SUCCESS)
        if failed:
            self.message_user(
                request, f"{failed} ta qabulda bu oʻtish mumkin emas", messages.WARNING
            )

    @admin.action(description="Tasdiqlash")
    def action_confirm(self, request, queryset):
        self._bulk_transition(request, queryset, AppointmentStatus.CONFIRMED, "tasdiqlandi")

    @admin.action(description="Yakunlandi deb belgilash")
    def action_complete(self, request, queryset):
        self._bulk_transition(request, queryset, AppointmentStatus.COMPLETED, "yakunlandi")

    @admin.action(description="Kelmadi deb belgilash")
    def action_no_show(self, request, queryset):
        self._bulk_transition(request, queryset, AppointmentStatus.NO_SHOW, "kelmadi")

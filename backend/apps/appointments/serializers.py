"""Booking API serializerlari."""

from datetime import UTC

from rest_framework import serializers

from apps.appointments.models import Appointment
from apps.core.antispam import HONEYPOT_FIELD
from apps.services.models import Service
from apps.team.models import Doctor


class SlotSerializer(serializers.Serializer):
    starts_at = serializers.SerializerMethodField()
    start_utc = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    label = serializers.CharField()
    doctor_ids = serializers.ListField(child=serializers.IntegerField())

    def get_starts_at(self, obj):
        return obj.start.isoformat()

    def get_start_utc(self, obj):
        return obj.start.astimezone(UTC).isoformat().replace("+00:00", "Z")

    def get_end(self, obj):
        return obj.end.isoformat()


class DaySlotsSerializer(serializers.Serializer):
    date = serializers.SerializerMethodField()
    weekday = serializers.IntegerField()
    closed_reason = serializers.CharField()
    slots = SlotSerializer(many=True)

    def get_date(self, obj):
        return obj.day.isoformat()


class AppointmentCreateSerializer(serializers.Serializer):
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.filter(is_active=True, is_bookable=True),
        required=False,
        allow_null=True,
    )
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(is_active=True),
        required=True,
        error_messages={"required": "service_required", "null": "service_required"},
    )
    starts_at = serializers.DateTimeField(required=True)
    patient_name = serializers.CharField(max_length=150, min_length=2)
    phone = serializers.CharField(max_length=32)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    comment = serializers.CharField(max_length=1000, required=False, allow_blank=True, default="")
    locale = serializers.ChoiceField(choices=["uz", "ru", "en"], default="uz")
    consent = serializers.BooleanField(required=True)
    consent_text_version = serializers.CharField(
        max_length=32, required=False, allow_blank=True, default=""
    )
    idempotency_key = serializers.UUIDField(required=False, allow_null=True)
    form_token = serializers.CharField(required=False, allow_blank=True, default="")
    # Honeypot — bot to'ldiradi, odam ko'rmaydi (critique #17)
    referral_note_2 = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_starts_at(self, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise serializers.ValidationError("naive_datetime")
        return value

    def validate_consent(self, value):
        if value is not True:
            raise serializers.ValidationError("consent_required")
        return value


class LeadCreateSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(
        choices=["callback", "contact", "price_request", "demo_inquiry"], default="callback"
    )
    name = serializers.CharField(max_length=150, min_length=2)
    phone = serializers.CharField(max_length=32)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    message = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    preferred_time = serializers.CharField(
        max_length=120, required=False, allow_blank=True, default=""
    )
    locale = serializers.ChoiceField(choices=["uz", "ru", "en"], default="uz")
    source_page = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    utm_source = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    utm_medium = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    utm_campaign = serializers.CharField(
        max_length=100, required=False, allow_blank=True, default=""
    )
    consent = serializers.BooleanField(required=True)
    form_token = serializers.CharField(required=False, allow_blank=True, default="")
    referral_note_2 = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_consent(self, value):
        if value is not True:
            raise serializers.ValidationError("consent_required")
        return value


class AppointmentPublicSerializer(serializers.ModelSerializer):
    """Bemor o'z qabulini ko'rishi (token orqali). Ichki maydonlar YOʻQ."""

    doctor_name = serializers.CharField(source="doctor.full_name", default=None)
    doctor_specialization = serializers.CharField(source="doctor.specialization", default=None)
    service_title = serializers.CharField(source="service.title", default=None)
    doctor_id = serializers.SerializerMethodField()
    service_id = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    can_reschedule = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = (
            "code",
            "starts_at",
            "ends_at",
            "status",
            "doctor_name",
            "doctor_specialization",
            "service_title",
            "doctor_id",
            "service_id",
            "patient_name",
            "can_cancel",
            "can_reschedule",
        )

    def get_doctor_id(self, obj):
        return obj.doctor_id

    def get_service_id(self, obj):
        return obj.service_id

    def get_can_cancel(self, obj):
        from django.utils import timezone

        return obj.is_active and obj.starts_at > timezone.now()

    def get_can_reschedule(self, obj):
        from django.utils import timezone

        return obj.is_active and obj.starts_at > timezone.now() and obj.reschedule_count < 3


HONEYPOT = HONEYPOT_FIELD

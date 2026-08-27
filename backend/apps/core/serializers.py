"""Core serializerlar. Rasmlar {src, width, height, alt} shaklida (CLS=0 uchun)."""

from django.conf import settings
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.core.models import ClinicSettings, StatCounter, WorkingHours


@extend_schema_field(
    {
        "type": "object",
        "nullable": True,
        "properties": {
            "src": {"type": "string", "format": "uri"},
            "width": {"type": "integer", "nullable": True},
            "height": {"type": "integer", "nullable": True},
            "alt": {"type": "string", "nullable": True},
        },
    }
)
class ImageField(serializers.Field):
    """
    Rasmni yalangʻoch URL emas, oʻlchamlari + alt bilan obyekt sifatida qaytaradi.
    `alt_source` — obyektdagi qoʻshni maydon nomi (masalan "photo_alt"), undan `alt` olinadi.
    `src` — `MEDIA_PUBLIC_BASE` boʻlsa oʻshandan, aks holda request host'idan (dev).
    """

    def __init__(self, alt_source=None, **kwargs):
        self.alt_source = alt_source
        kwargs.setdefault("read_only", True)
        super().__init__(**kwargs)

    def get_attribute(self, instance):
        # Butun obyektni olamiz — alt qoʻshni maydonini ham oʻqishimiz kerak.
        return instance

    def to_representation(self, instance):
        image = getattr(instance, self.field_name, None)
        if not image:
            return None
        try:
            width, height = image.width, image.height
        except (OSError, ValueError):
            width = height = None
        url = image.url  # "/media/..." (MEDIA_URL bosh slash bilan)
        base = settings.MEDIA_PUBLIC_BASE
        if base:
            src = base.rstrip("/") + url
        else:
            request = self.context.get("request")
            src = request.build_absolute_uri(url) if request else url
        alt = getattr(instance, self.alt_source, "") if self.alt_source else None
        return {"src": src, "width": width, "height": height, "alt": alt}


class WorkingHoursSerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(source="get_weekday_display", read_only=True)

    class Meta:
        model = WorkingHours
        fields = ("weekday", "weekday_display", "opens", "closes", "is_closed", "note")


class StatCounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatCounter
        fields = ("id", "label", "value", "suffix", "icon", "order")


class ClinicSettingsSerializer(serializers.ModelSerializer):
    logo = ImageField()
    favicon = ImageField()
    working_hours = serializers.SerializerMethodField()
    counters = serializers.SerializerMethodField()
    theme = serializers.SerializerMethodField()

    class Meta:
        model = ClinicSettings
        fields = (
            "name",
            "tagline",
            "about_short",
            "logo",
            "favicon",
            "theme",
            "phone_primary",
            "phone_secondary",
            "email",
            "telegram_username",
            "telegram_channel_url",
            "instagram_url",
            "facebook_url",
            "youtube_url",
            "address",
            "map_lat",
            "map_lng",
            "map_zoom",
            "yandex_maps_url",
            "two_gis_url",
            "license_text",
            "legal_entity_name",
            "prices_visible",
            "booking_enabled",
            "default_meta_title",
            "default_meta_description",
            "metrika_id",
            "ga4_id",
            "working_hours",
            "counters",
        )

    @extend_schema_field(
        {
            "type": "object",
            "properties": {
                "brand": {"type": "string"},
                "accent": {"type": "string"},
                "ink": {"type": "string"},
                "surface": {"type": "string"},
                "fontPair": {"type": "string"},
            },
        }
    )
    def get_theme(self, obj):
        """Frontend CSS custom property sifatida ishlatadi (ADR-004)."""
        return {
            "brand": obj.brand_color,
            "accent": obj.accent_color,
            "ink": obj.ink_color,
            "surface": obj.surface_color,
            "fontPair": obj.font_pair,
        }

    @extend_schema_field(WorkingHoursSerializer(many=True))
    def get_working_hours(self, obj):
        return WorkingHoursSerializer(
            WorkingHours.objects.all(), many=True, context=self.context
        ).data

    @extend_schema_field(StatCounterSerializer(many=True))
    def get_counters(self, obj):
        qs = StatCounter.objects.filter(is_active=True)
        return StatCounterSerializer(qs, many=True, context=self.context).data

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.core.serializers import ImageField, TranslatedSlugsField
from apps.team.models import Doctor


class DoctorListSerializer(serializers.ModelSerializer):
    photo = ImageField(alt_source="photo_alt")
    og_image = ImageField()
    alternates = TranslatedSlugsField()
    languages = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = (
            "id",
            "full_name",
            "slug",
            "alternates",
            "updated_at",
            "og_image",
            "specialization",
            "photo",
            "photo_alt",
            "experience_years",
            "languages",
            "is_bookable",
            "order",
        )

    @extend_schema_field({"type": "array", "items": {"type": "string"}})
    def get_languages(self, obj):
        return [x.strip() for x in obj.languages_spoken.split(",") if x.strip()]


class DoctorDetailSerializer(DoctorListSerializer):
    services = serializers.SerializerMethodField()

    class Meta(DoctorListSerializer.Meta):
        fields = DoctorListSerializer.Meta.fields + (
            "bio",
            "education",
            "certificates",
            "telegram_username",
            "services",
            "meta_title",
            "meta_description",
        )

    @extend_schema_field({"type": "array", "items": {"type": "object"}})
    def get_services(self, obj):
        from apps.services.serializers import ServiceListSerializer

        qs = obj.services.filter(is_active=True)
        return ServiceListSerializer(qs, many=True, context=self.context).data

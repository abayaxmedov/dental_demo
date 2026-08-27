from rest_framework import serializers

from apps.cases.models import CasePair
from apps.core.serializers import ImageField, TranslatedSlugsField


class CasePairSerializer(serializers.ModelSerializer):
    image_before = ImageField()
    image_after = ImageField()
    og_image = ImageField()
    alternates = TranslatedSlugsField()
    service_slug = serializers.CharField(source="service.slug", read_only=True, default=None)
    service_title = serializers.CharField(source="service.title", read_only=True, default=None)
    doctor_name = serializers.CharField(source="doctor.full_name", read_only=True, default=None)

    class Meta:
        model = CasePair
        fields = (
            "id",
            "title",
            "slug",
            "alternates",
            "updated_at",
            "image_before",
            "image_after",
            "og_image",
            "caption",
            "treatment_summary",
            "duration_note",
            "service_slug",
            "service_title",
            "doctor_name",
            "meta_title",
            "meta_description",
            "is_featured",
            "order",
        )

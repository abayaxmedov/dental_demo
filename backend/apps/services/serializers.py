from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.core.serializers import ImageField
from apps.services.models import Faq, PriceItem, Service, ServiceCategory


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("id", "title", "slug", "icon", "order")


class PriceItemSerializer(serializers.ModelSerializer):
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    service_slug = serializers.CharField(source="service.slug", read_only=True, default=None)

    class Meta:
        model = PriceItem
        fields = (
            "id",
            "title",
            "price_from",
            "price_to",
            "currency",
            "unit",
            "qualifier",
            "is_promo",
            "promo_note",
            "category_slug",
            "service_slug",
            "order",
        )


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ("id", "question", "answer", "order")


class ServiceListSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    cover = ImageField()

    class Meta:
        model = Service
        fields = (
            "id",
            "title",
            "slug",
            "excerpt",
            "icon",
            "cover",
            "duration_minutes",
            "is_featured",
            "category",
            "order",
        )


class ServiceDetailSerializer(ServiceListSerializer):
    prices = serializers.SerializerMethodField()
    faqs = FaqSerializer(many=True, read_only=True)
    doctors = serializers.SerializerMethodField()

    class Meta(ServiceListSerializer.Meta):
        fields = ServiceListSerializer.Meta.fields + (
            "body",
            "prices",
            "faqs",
            "doctors",
            "meta_title",
            "meta_description",
        )

    @extend_schema_field(PriceItemSerializer(many=True))
    def get_prices(self, obj):
        qs = obj.prices.filter(is_active=True)
        return PriceItemSerializer(qs, many=True, context=self.context).data

    @extend_schema_field({"type": "array", "items": {"type": "object"}})
    def get_doctors(self, obj):
        from apps.team.serializers import DoctorListSerializer

        qs = obj.doctors.filter(is_active=True)
        return DoctorListSerializer(qs, many=True, context=self.context).data

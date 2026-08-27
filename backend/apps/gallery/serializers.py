from rest_framework import serializers

from apps.core.serializers import ImageField
from apps.gallery.models import GalleryImage


class GalleryImageSerializer(serializers.ModelSerializer):
    image = ImageField(alt_source="alt")

    class Meta:
        model = GalleryImage
        fields = ("id", "image", "alt", "caption", "category", "instagram_url", "order")

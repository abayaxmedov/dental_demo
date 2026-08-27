from rest_framework import serializers

from apps.core.serializers import ImageField
from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    author_photo = ImageField()

    class Meta:
        model = Review
        fields = (
            "id",
            "author_name",
            "author_photo",
            "rating",
            "text",
            "source",
            "source_url",
            "reviewed_at",
            "is_featured",
            "order",
        )

from rest_framework import serializers

from apps.pages.models import StaticPage


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ("key", "title", "body", "meta_title", "meta_description")

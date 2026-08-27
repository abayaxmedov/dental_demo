from rest_framework import serializers

from apps.blog.models import Post
from apps.core.serializers import ImageField


class PostListSerializer(serializers.ModelSerializer):
    cover = ImageField()
    author_name = serializers.CharField(source="author.full_name", read_only=True, default=None)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "excerpt",
            "cover",
            "author_name",
            "published_at",
            "reading_time",
        )


class PostDetailSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ("body", "meta_title", "meta_description")

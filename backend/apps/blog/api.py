from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.blog.models import Post
from apps.blog.serializers import PostDetailSerializer, PostListSerializer


@extend_schema(tags=["content"])
class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """Blog. `?q=` — trigram qidiruv (lotin va kirill uchun)."""

    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = Post.objects.filter(is_published=True).select_related("author")
        q = self.request.query_params.get("q")
        if q:
            qs = (
                qs.annotate(similarity=TrigramSimilarity("title", q))
                .filter(Q(similarity__gt=0.1) | Q(title__icontains=q) | Q(excerpt__icontains=q))
                .order_by("-similarity", "-published_at")
            )
        return qs

    def get_serializer_class(self):
        return PostDetailSerializer if self.action == "retrieve" else PostListSerializer

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.gallery.models import GalleryImage
from apps.gallery.serializers import GalleryImageSerializer


@extend_schema(tags=["content"])
class GalleryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = GalleryImageSerializer

    def get_queryset(self):
        qs = GalleryImage.objects.filter(is_active=True)
        if category := self.request.query_params.get("category"):
            qs = qs.filter(category=category)
        return qs

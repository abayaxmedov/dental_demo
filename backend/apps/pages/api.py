from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.pages.models import StaticPage
from apps.pages.serializers import StaticPageSerializer


@extend_schema(tags=["content"])
class StaticPageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "key"
    serializer_class = StaticPageSerializer
    queryset = StaticPage.objects.filter(is_active=True)
    pagination_class = None

from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.models import ClinicSettings
from apps.services.models import Faq, PriceItem, Service, ServiceCategory
from apps.services.serializers import (
    FaqSerializer,
    PriceItemSerializer,
    ServiceCategorySerializer,
    ServiceDetailSerializer,
    ServiceListSerializer,
)


@extend_schema(tags=["services"])
class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Xizmatlar katalogi. `?featured=1` — bosh sahifadagi 6 ta."""

    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = (
            Service.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related(
                "doctors",
                Prefetch("prices", queryset=PriceItem.objects.filter(is_active=True)),
                Prefetch("faqs", queryset=Faq.objects.filter(is_active=True)),
            )
        )
        if self.request.query_params.get("featured") in ("1", "true"):
            qs = qs.filter(is_featured=True)
        if category := self.request.query_params.get("category"):
            qs = qs.filter(category__slug=category)
        return qs

    def get_serializer_class(self):
        return ServiceDetailSerializer if self.action == "retrieve" else ServiceListSerializer

    @extend_schema(responses=ServiceCategorySerializer(many=True))
    @action(detail=False, methods=["get"])
    def categories(self, request):
        qs = ServiceCategory.objects.all()
        return Response(ServiceCategorySerializer(qs, many=True, context={"request": request}).data)

    @extend_schema(responses=PriceItemSerializer(many=True))
    @action(detail=False, methods=["get"])
    def prices(self, request):
        """Narxlar. `prices_visible=False` boʻlsa boʻsh roʻyxat (ADR-004)."""
        if not ClinicSettings.load().prices_visible:
            return Response([])
        qs = PriceItem.objects.filter(is_active=True).select_related("category", "service")
        if category := request.query_params.get("category"):
            qs = qs.filter(category__slug=category)
        return Response(PriceItemSerializer(qs, many=True, context={"request": request}).data)


@extend_schema(tags=["services"])
class FaqViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = FaqSerializer
    queryset = Faq.objects.filter(is_active=True)
    pagination_class = None

from django.db.models import Avg, Count
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer


@extend_schema(tags=["content"])
class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        qs = Review.objects.filter(is_active=True)
        if self.request.query_params.get("featured") in ("1", "true"):
            qs = qs.filter(is_featured=True)
        return qs

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Reyting yigʻindisi — sharhlar sahifasi sarlavhasi uchun."""
        agg = Review.objects.filter(is_active=True).aggregate(avg=Avg("rating"), total=Count("id"))
        return Response(
            {
                "average": round(agg["avg"] or 0, 1),
                "total": agg["total"],
            }
        )

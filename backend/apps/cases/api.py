from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.cases.models import CasePair
from apps.cases.serializers import CasePairSerializer


@extend_schema(tags=["content"])
class CasePairViewSet(viewsets.ReadOnlyModelViewSet):
    """Before/After ishlar. Faqat bemor roziligi bor va chop etilganlari."""

    permission_classes = [AllowAny]
    lookup_field = "slug"
    serializer_class = CasePairSerializer

    def get_queryset(self):
        qs = CasePair.objects.filter(is_published=True, consent_on_file=True).select_related(
            "service", "doctor"
        )
        if service := self.request.query_params.get("service"):
            qs = qs.filter(service__slug=service)
        return qs

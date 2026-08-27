from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.team.models import Doctor
from apps.team.serializers import DoctorDetailSerializer, DoctorListSerializer


@extend_schema(tags=["team"])
class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = Doctor.objects.filter(is_active=True).prefetch_related("services")
        if service := self.request.query_params.get("service"):
            qs = qs.filter(services__slug=service).distinct()
        return qs

    def get_serializer_class(self):
        return DoctorDetailSerializer if self.action == "retrieve" else DoctorListSerializer

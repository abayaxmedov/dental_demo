from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.team.models import Doctor
from apps.team.serializers import DoctorDetailSerializer, DoctorListSerializer


@extend_schema(tags=["team"])
class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    queryset = Doctor.objects.filter(is_active=True).prefetch_related("services")

    def get_serializer_class(self):
        return DoctorDetailSerializer if self.action == "retrieve" else DoctorListSerializer

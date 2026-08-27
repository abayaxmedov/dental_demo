"""Core API: sayt sozlamalari (bitta endpoint — frontend layout shundan quriladi)."""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import ClinicSettings
from apps.core.serializers import ClinicSettingsSerializer


class SiteSettingsView(APIView):
    """Klinika sozlamalari + ish vaqti + counterlar. Barcha sahifalar uchun."""

    permission_classes = [AllowAny]

    @extend_schema(responses=ClinicSettingsSerializer, tags=["core"])
    def get(self, request):
        settings_obj = ClinicSettings.load()
        data = ClinicSettingsSerializer(settings_obj, context={"request": request}).data
        response = Response(data)
        response["Cache-Control"] = "public, max-age=300"
        return response

"""Core API: sayt sozlamalari (bitta endpoint — frontend layout shundan quriladi)."""

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
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


class SeoRoutesView(APIView):
    """
    Sitemap va generateStaticParams uchun bitta manba (T-P3-13).
    Har til uchun slug'lar + updated_at. Locale'ga bogʻliq emas, unpaginated.
    """

    permission_classes = [AllowAny]

    @extend_schema(responses=OpenApiTypes.OBJECT, tags=["core"])
    def get(self, request):
        from apps.blog.models import Post
        from apps.cases.models import CasePair
        from apps.pages.models import StaticPage
        from apps.services.models import Service
        from apps.team.models import Doctor

        def slugs(obj):
            return {lang: getattr(obj, f"slug_{lang}", None) or obj.slug for lang in ("uz", "ru", "en")}

        def rows(qs):
            return [
                {"slugs": slugs(o), "updated_at": o.updated_at.isoformat()}
                for o in qs
            ]

        data = {
            "generated_at": timezone.now().isoformat(),
            "services": rows(Service.objects.filter(is_active=True)),
            "doctors": rows(Doctor.objects.filter(is_active=True)),
            "cases": rows(CasePair.objects.filter(is_published=True, consent_on_file=True)),
            "posts": rows(Post.objects.filter(is_published=True)),
            "pages": [
                {"key": p.key, "updated_at": p.updated_at.isoformat()}
                for p in StaticPage.objects.filter(is_active=True)
            ],
        }
        resp = Response(data)
        resp["Cache-Control"] = "public, max-age=300"
        return resp

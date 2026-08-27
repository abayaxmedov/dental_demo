"""
Root URLconf — headless backend (ADR-016).
Faqat /admin/, /api/v1/ va /healthz/. i18n_patterns YOʻQ — URL prefiks Next.js'da.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from apps.core.views import healthz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz, name="healthz"),
    # API v1
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/v1/", include("apps.core.api_urls")),
]

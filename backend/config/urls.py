"""
Root URLconf — headless backend (ADR-016).
Faqat /admin/, /api/v1/ va /healthz/. i18n_patterns YOʻQ — URL prefiks Next.js'da.
"""

from django.conf import settings
from django.conf.urls.static import static
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

# Dev'da yuklangan media'ni Django servis qiladi (prod'da nginx `/media/` ni beradi).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

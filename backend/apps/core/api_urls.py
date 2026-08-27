"""
/api/v1/ marshrutlari (ADR E-qism) — read (Faza 1) + write (Faza 2).
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.appointments.api import (
    AppointmentCancelView,
    AppointmentCreateView,
    AppointmentRescheduleView,
    AppointmentTokenView,
    FormTokenView,
    LeadCreateView,
    SlotsView,
)
from apps.blog.api import PostViewSet
from apps.cases.api import CasePairViewSet
from apps.core.api import SiteSettingsView
from apps.gallery.api import GalleryViewSet
from apps.pages.api import StaticPageViewSet
from apps.reviews.api import ReviewViewSet
from apps.services.api import FaqViewSet, ServiceViewSet
from apps.team.api import DoctorViewSet

router = DefaultRouter()
router.register("services", ServiceViewSet, basename="service")
router.register("doctors", DoctorViewSet, basename="doctor")
router.register("cases", CasePairViewSet, basename="case")
router.register("gallery", GalleryViewSet, basename="gallery")
router.register("reviews", ReviewViewSet, basename="review")
router.register("posts", PostViewSet, basename="post")
router.register("faq", FaqViewSet, basename="faq")
router.register("pages", StaticPageViewSet, basename="page")

urlpatterns = [
    path("site-settings/", SiteSettingsView.as_view(), name="site-settings"),
    # Booking (Faza 2) — router'dan OLDIN aniq yo'llar
    path("appointments/slots/", SlotsView.as_view(), name="slots"),
    path("appointments/form-token/", FormTokenView.as_view(), name="form-token"),
    path("appointments/", AppointmentCreateView.as_view(), name="appointment-create"),
    path(
        "appointments/<uuid:cancel_token>/",
        AppointmentTokenView.as_view(),
        name="appointment-detail",
    ),
    path(
        "appointments/<uuid:cancel_token>/cancel/",
        AppointmentCancelView.as_view(),
        name="appointment-cancel",
    ),
    path(
        "appointments/<uuid:cancel_token>/reschedule/",
        AppointmentRescheduleView.as_view(),
        name="appointment-reschedule",
    ),
    path("leads/", LeadCreateView.as_view(), name="lead-create"),
    path("", include(router.urls)),
]

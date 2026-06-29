from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from apps.api.views import HealthCheckView, MeView, MembershipViewSet, OrganizationViewSet

router = DefaultRouter()
router.register(r"orgs", OrganizationViewSet, basename="org")
router.register(r"members", MembershipViewSet, basename="member")

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/me/", MeView.as_view(), name="api-me"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

from django.urls import path as django_path
urlpatterns += [django_path("health/", HealthCheckView.as_view(), name="health-check")]

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.api.permissions import IsOrgAdmin, IsOrgMember
from apps.api.serializers import (
    MembershipSerializer,
    OrganizationSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from apps.organizations.models import Membership, Organization


class MeView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class OrganizationViewSet(ReadOnlyModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrgMember]
    authentication_classes = [SessionAuthentication]
    lookup_field = "slug"

    def get_queryset(self):
        return Organization.objects.filter(
            memberships__user=self.request.user,
            is_active=True,
        )

    def partial_update(self, request, *args, **kwargs):
        if not IsOrgAdmin().has_permission(request, self):
            return Response({"detail": "Admin access required."}, status=status.HTTP_403_FORBIDDEN)
        org = self.get_object()
        serializer = self.get_serializer(org, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MembershipViewSet(ReadOnlyModelViewSet):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, IsOrgMember]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        org = getattr(self.request, "org", None)
        if not org:
            return Membership.objects.none()
        return Membership.objects.filter(org=org).select_related("user")

    def destroy(self, request, *args, **kwargs):
        if not IsOrgAdmin().has_permission(request, self):
            return Response({"detail": "Admin access required."}, status=status.HTTP_403_FORBIDDEN)
        membership = self.get_object()
        if membership.is_owner:
            return Response({"detail": "Cannot remove the owner."}, status=status.HTTP_400_BAD_REQUEST)
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        checks = {}
        status_code = 200

        try:
            from django.db import connection
            connection.ensure_connection()
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {str(e)}"
            status_code = 503

        try:
            from django.core.cache import cache
            cache.set("health_check", "1", 5)
            assert cache.get("health_check") == "1"
            checks["redis"] = "ok"
        except Exception as e:
            checks["redis"] = f"error: {str(e)}"
            status_code = 503

        try:
            from config.celery import app as celery_app
            celery_app.control.ping(timeout=1)
            checks["celery"] = "ok"
        except Exception:
            checks["celery"] = "unavailable"

        return Response(
            {
                "status": "healthy" if status_code == 200 else "degraded",
                "checks": checks,
                "version": "1.0.0",
            },
            status=status_code,
        )


def handler404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def handler500(request):
    return render(request, "errors/500.html", status=500)


def handler403(request, exception=None):
    return render(request, "errors/403.html", status=403)

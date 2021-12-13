from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import views as rest_framework_simplejwt_views

from app import models
from . import serializers

class LogoutAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        if getattr(settings, 'ACCOUNT_LOGOUT_ON_GET', False):
            response = self.logout(request)
        else:
            response = self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        if getattr(settings, 'REST_SESSION_LOGIN', True):
            django_logout(request)

        response = Response({"detail": _("Successfully logged out.")},
                            status=status.HTTP_200_OK)
        if getattr(settings, 'REST_USE_JWT', False):
            from rest_framework_simplejwt.settings import api_settings as jwt_settings
            if jwt_settings.JWT_AUTH_COOKIE:
                response.delete_cookie(jwt_settings.JWT_AUTH_COOKIE)

        return response


class FlowModelViewSet(viewsets.ModelViewSet):
    queryset = models.Flow.objects.all()
    serializer_class = serializers.FlowModelSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'post', 'put']

    def get_queryset(self):
        return self.queryset.filter(staff__in=self.request.user.company.staff_set.all())


class StaffModelViewSet(viewsets.ModelViewSet):
    queryset = models.Staff.objects.all()
    serializer_class = serializers.StaffModelSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'post']

    def retrieve(self, request, *args, **kwargs):
        company = self.request.user.company
        staff = models.Staff.objects.filter(company=company)
        serializer = self.get_serializer(staff, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        company = self.request.user.company
        staff = models.Staff.objects.filter(company=company)
        serializer = self.get_serializer(staff, many=True)
        return Response(serializer.data)


class JWTTokenObtainView(rest_framework_simplejwt_views.TokenObtainPairView):
    serializer_class = serializers.JWTTokenObtainSerializer


#
# class JWTTokenVerifyView(rest_framework_simplejwt_views.TokenVerifyView):
#     serializer_class = serializers.JWTTokenVerifySerializer


class JWTTokenRefreshView(rest_framework_simplejwt_views.TokenRefreshView):
    pass

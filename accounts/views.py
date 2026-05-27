from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        self.user = serializer.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        token, _ = Token.objects.get_or_create(user=self.user)
        response.data["token"] = token.key
        return response


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

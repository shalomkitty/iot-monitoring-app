from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Device
from .permissions import IsOwnerOrStaff
from .serializers import DeviceSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        queryset = Device.objects.all()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="rotate-key")
    def rotate_key(self, request, pk=None):
        device = self.get_object()
        device.rotate_api_key()
        return Response({"api_key": device.api_key})

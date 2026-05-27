from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from devices.models import Device

from .models import AIInsight
from .serializers import AIInsightSerializer, GenerateInsightSerializer
from .tasks import generate_ai_insight


class GenerateInsightView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = GenerateInsightSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        device = None
        if serializer.validated_data.get("device_id"):
            device = Device.objects.get(id=serializer.validated_data["device_id"])

        metric = serializer.validated_data.get("metric", "")
        hours = serializer.validated_data["hours"]

        insight = AIInsight.objects.create(
            owner=request.user,
            device=device,
            metric=metric,
            hours=hours,
            prompt="Pending generation.",
        )
        task = generate_ai_insight.delay(insight.id)

        return Response(
            {
                "insight_id": insight.id,
                "status": insight.status,
                "task_id": str(task.id),
            },
            status=status.HTTP_202_ACCEPTED,
        )


class AIInsightViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AIInsightSerializer
    filterset_fields = ["device", "metric", "status"]
    ordering_fields = ["created_at", "completed_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = AIInsight.objects.select_related("owner", "device")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(owner=self.request.user)

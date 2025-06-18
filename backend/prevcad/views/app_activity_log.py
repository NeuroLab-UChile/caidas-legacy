from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from prevcad.models import AppActivityLog
from prevcad.serializers.app_activity_log_serializer import AppActivityLogSerializer


class AppActivityLogView(viewsets.ModelViewSet):
    queryset = AppActivityLog.objects.all()
    serializer_class = AppActivityLogSerializer

    def get_queryset(self):
        # Return only the activity logs for the requesting user
        return AppActivityLog.objects.filter(user=self.request.user)

    def create(self, request: Request, *args, **kwargs) -> Response:
        request.data["user"] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

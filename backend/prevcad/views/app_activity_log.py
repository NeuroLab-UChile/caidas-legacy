from typing import cast
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from prevcad.models import AppActivityLog
from prevcad.serializers.app_activity_log_serializer import AppActivityLogSerializer


class AppActivityLogView(viewsets.ModelViewSet):
    queryset = AppActivityLog.objects.all()
    serializer_class = AppActivityLogSerializer

    def get_queryset(self):
        # Return only the activity logs for the requesting user
        return AppActivityLog.objects.filter(user=self.request.user)

    def create(self, request: Request, *args, **kwargs) -> Response:
        user = request.user
        actions = request.data.get("actions", {})
        date = request.data.get("date")

        # Check if date exists, if not, set it to today
        if not date:
            date = timezone.now().date()

        overwrite_actions = request.query_params.get(
            "overwrite_actions", "false"
        ).lower() in ["true", "1"]

        # Check if an instance already exists
        instance, created = AppActivityLog.objects.get_or_create(user=user, date=date)
        print("Created: ", created)

        instance = cast(AppActivityLog, instance)

        if not created and overwrite_actions:
            # Backup the current actions
            backup_actions = instance.actions
            try:
                # Clear the actions field
                instance.actions = {}
                instance.add_actions(actions)
            except Exception as e:
                # Restore the backup if validation fails
                instance.actions = backup_actions
                raise ValidationError(
                    {"detail": f"Error overwriting actions: {str(e)}"}
                )
        # elif not created and not overwrite_actions:
        else:
            # Add actions without overwriting existing actions
            instance.add_actions(actions)

        # Save the updated instance
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

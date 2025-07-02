from typing import cast
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from prevcad.models import DownloadableContent, DownloadByUser
from prevcad.serializers.downloads_serializer import DownloadByUserSerializer


class DownloadByUserViewSet(viewsets.ModelViewSet):
    queryset = DownloadByUser.objects.none()
    serializer_class = DownloadByUserSerializer

    def get_queryset(self):
        # Get or create and return all the DownloadByUser objects related to DownloadableContent
        return DownloadByUser.get_all_downloads_for_user(self.request.user)

    def create(self, request: Request, *args, **kwargs) -> Response:
        user = request.user
        content = request.data.get("content", None)
        download_date = request.data.get("download_date", None)
        downloaded = request.data.get("downloaded", False)

        # Check if date exists, if not, set it to today
        if downloaded and not download_date:
            download_date = timezone.now()

        # Check if an instance already exists
        instance, created = DownloadByUser.objects.get_or_create(
            user=user, content=content
        )
        # Update fields
        instance = cast(DownloadByUser, instance)
        instance.downloaded = downloaded
        instance.download_date = download_date

        # Save the updated instance
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

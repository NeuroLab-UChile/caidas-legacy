from rest_framework import serializers
from django.utils.encoding import smart_str

from prevcad.models import DownloadableContent, DownloadByUser


class DownloadableContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadableContent
        fields = "__all__"


class DownloadByUserSerializer(serializers.ModelSerializer):
    content = DownloadableContentSerializer(read_only=True)

    class Meta:
        model = DownloadByUser
        fields = "__all__"
        read_only_fields = ["user", "download_date"]

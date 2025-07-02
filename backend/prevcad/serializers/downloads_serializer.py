from rest_framework import serializers
from django.utils.encoding import smart_str

from prevcad.models import DownloadableContent, DownloadByUser


class DownloadByUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadByUser
        fields = "__all__"
        read_only_fields = ["user", "download_date"]

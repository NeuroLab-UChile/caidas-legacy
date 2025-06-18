from rest_framework import serializers
from django.utils.encoding import smart_str

from prevcad.models import AppActivityLog


class AppActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppActivityLog
        fields = "__all__"
        read_only_fields = ["timestamp"]

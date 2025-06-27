from rest_framework import serializers
from ..models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        # fields = ['id', 'title', 'date', 'description', 'created_at']
        fields = "__all__"
        read_only_fields = ["created_at"]

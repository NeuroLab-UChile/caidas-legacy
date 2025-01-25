from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Appointment
from ..serializers.appointment_serializer import AppointmentSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer
    
    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

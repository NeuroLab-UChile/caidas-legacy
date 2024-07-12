from django.http import JsonResponse
from rest_framework import viewsets
from prevcad.models import HealthCategory

class HealthCategoryView(viewsets.ViewSet):
    queryset =HealthCategory.objects.all()
    def create(self, request):
        return JsonResponse({'message': 'Create a new health category'})
    
    def list(self, request):

        categories = [
            {'title': 'Historia de caídas', 'icon': 'local_hospital'},
            {'title': 'Actividad física', 'icon': 'directions_run'},
            {'title': 'Alimentación saludable', 'icon': 'restaurant'},
            {'title': 'Medicamentos', 'icon': 'accessibility'},
            {'title': 'Salud mental', 'icon': 'home'},
            {'title': 'Salud sexual', 'icon': 'medication'},
            {'title': 'Salud bucal', 'icon': 'psychology'},
            {'title': 'Salud visual', 'icon': 'visibility'},
            {'title': 'Salud auditiva', 'icon': 'fitness_center'},
        ]
        return JsonResponse({'categories': categories})

    # Other methods can remain unchanged if not used

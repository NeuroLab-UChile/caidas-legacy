from django.http import JsonResponse
from rest_framework import viewsets
from prevcad.models import HealthCategory

class HealthCategoryView(viewsets.ViewSet):
    queryset =HealthCategory.objects.all()
    def create(self, request):
        return JsonResponse({'message': 'Create a new health category'})
    
    def list(self, request):

        categories = [
            {'title': 'Historia de caídas', 'icon': 'account_balance'},
            {'title': 'Actividad física', 'icon': 'run_circle'},
            {'title': 'Alimentación saludable', 'icon': 'local_dining'},
            {'title': 'Medicamentos', 'icon': 'medication'},
            # Add more categories as needed
        ]
        return JsonResponse({'categories': categories})

    # Other methods can remain unchanged if not used

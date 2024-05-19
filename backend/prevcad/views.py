from django.http import JsonResponse
from rest_framework import viewsets

class HealthCategoryView(viewsets.ViewSet):
    
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

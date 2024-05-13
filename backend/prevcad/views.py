from django.http import JsonResponse
from rest_framework import viewsets
from django.contrib.auth.models import User

class PrevcadView(viewsets.ViewSet):
    queryset = User.objects.all()
    
    def list(self, request):
        return JsonResponse({'message': 'Hello, world!'})

    def create(self, request):
        return JsonResponse({'message': 'Hello, world!'})
    
    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass

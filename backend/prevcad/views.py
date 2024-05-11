from django.http import JsonResponse
from rest_framework import viewsets
from .models import User

class PrevcadView(viewsets.ViewSet):
    queryset = User.objects.all()
    
    def list(self, request):
        users = User.objects.all()
        print(users)
        return JsonResponse({'users': list(users.values())})

    def create(self, request):
        return User.objects.create()
    

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass

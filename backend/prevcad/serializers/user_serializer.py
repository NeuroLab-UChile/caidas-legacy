from rest_framework import serializers

from django.contrib.auth.models import User
from prevcad.serializers.profile_serializer import ProfileSerializer


class UserSerializer(serializers.ModelSerializer):
  profile = ProfileSerializer()  # Relacionamos el perfil con el usuario

  class Meta:
    model = User
    fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']  # Incluimos el perfil

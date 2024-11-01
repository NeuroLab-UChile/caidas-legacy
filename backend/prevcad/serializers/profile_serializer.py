import base64
from rest_framework import serializers

from prevcad.models import (
  Profile,
)



class ProfileSerializer(serializers.ModelSerializer):
  profile_picture = serializers.SerializerMethodField()  # Procesar la imagen como base64

  class Meta:
    model = Profile
    fields = ['profile_picture']  # Puedes agregar más campos si los tienes

  def get_profile_picture(self, obj):
    # Convertir la imagen de perfil a bytes base64
    if obj.profile_picture and hasattr(obj.profile_picture, 'path'):
      with open(obj.profile_picture.path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    return None

import base64
from rest_framework import serializers
from django.utils.encoding import smart_str

from prevcad.models import (
  HealthCategory,
)


class HealthCategorySerializer(serializers.ModelSerializer):
  name = serializers.CharField(max_length=255)
  description = serializers.CharField()
  image = serializers.SerializerMethodField()  # Campo para la imagen en bytes
  icon = serializers.SerializerMethodField()  # Campo para el icono en bytes

  class Meta:
    model = HealthCategory
    fields = ['id', 'name', 'description', 'image', 'icon']

  def get_image(self, obj):
    # Convertir la imagen a bytes base64
    if obj.image and hasattr(obj.image, 'path'):
      with open(obj.image.path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')  # Convertir a base64
    return None

  def get_icon(self, obj):
    # Convertir el icono a bytes base64
    if obj.icon and hasattr(obj.icon, 'path'):
      with open(obj.icon.path, 'rb') as icon_file:
        return base64.b64encode(icon_file.read()).decode('utf-8')
    return None

  def to_representation(self, instance):
    # Asegurar que los campos de texto se codifiquen correctamente
    instance.name = smart_str(instance.name)
    instance.description = smart_str(instance.description)
    return super().to_representation(instance)

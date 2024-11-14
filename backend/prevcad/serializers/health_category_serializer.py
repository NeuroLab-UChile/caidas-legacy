import base64
from rest_framework import serializers
from django.utils.encoding import smart_str

from prevcad.models import HealthCategory


class HealthCategorySerializer(serializers.ModelSerializer):
  name = serializers.CharField(max_length=255)
  image = serializers.SerializerMethodField()
  description = serializers.CharField()
  description_2 = serializers.CharField()

  class Meta:
    model = HealthCategory
    fields = ['id', 'name', 'description', 'description_2', 'image']

  def get_image(self, obj):
    if obj.image and hasattr(obj.image, 'path'):
      with open(obj.image.path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    return None

  def to_representation(self, instance):
    instance.name = smart_str(instance.name)
    instance.description = smart_str(instance.description)
    instance.description_2 = smart_str(instance.description_2)
    return super().to_representation(instance)
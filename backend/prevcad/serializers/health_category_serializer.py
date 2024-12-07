import base64
from rest_framework import serializers
from django.utils.encoding import smart_str

from prevcad.models import HealthCategory


from rest_framework import serializers
from prevcad.models import HealthCategory

class HealthCategorySerializer(serializers.ModelSerializer):
  name = serializers.SerializerMethodField()
  icon = serializers.SerializerMethodField()
  description = serializers.SerializerMethodField()

  def get_name(self, obj):
    return smart_str(obj.template.name) if obj.template else None

  def get_icon(self, obj):
    if obj.template and obj.template.icon and hasattr(obj.template.icon, 'path'):
      try:
        with open(obj.template.icon.path, 'rb') as image_file:
          return base64.b64encode(image_file.read()).decode('utf-8')
      except Exception as e:
        print(f"Error reading image file: {e}")
        return None
    return None

  def get_description(self, obj):
    return obj.template.description if obj.template else None

  class Meta:
    model = HealthCategory
    fields = ['id', 'name', 'icon', 'description', 'root_node']

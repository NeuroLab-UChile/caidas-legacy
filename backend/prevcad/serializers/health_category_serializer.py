import base64
from rest_framework import serializers
from django.utils.encoding import smart_str

from prevcad.models import HealthCategory


class HealthCategorySerializer(serializers.ModelSerializer):
  name = serializers.CharField(max_length=255)
  icon = serializers.SerializerMethodField()
  description = serializers.CharField()
  description_2 = serializers.CharField(required=False)
  type = serializers.ChoiceField(choices=HealthCategory.CategoryType.choices)
  evaluation_form = serializers.JSONField(required=False)
  workout_form = serializers.JSONField(required=False)
  category_form = serializers.JSONField(required=False)
  user = serializers.PrimaryKeyRelatedField(read_only=True)

  class Meta:
    model = HealthCategory
    fields = ['id', 'name', 'description', 'description_2', 'icon',
             'type', 'evaluation_form', 'workout_form', 'category_form', 'user']

  def get_icon(self, obj):
    if obj.icon and hasattr(obj.icon, 'path'):
      with open(obj.icon.path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    return None

  def to_representation(self, instance):
    instance.name = smart_str(instance.name)
    instance.description = smart_str(instance.description)
    if instance.description_2:
      instance.description_2 = smart_str(instance.description_2)
    return super().to_representation(instance)

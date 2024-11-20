import base64
from rest_framework import serializers
from django.utils.encoding import smart_str

from prevcad.models import HealthCategory


from rest_framework import serializers
from prevcad.models import HealthCategory

class HealthCategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = HealthCategory
    fields = ['id', 'name', 'icon', 'template', 'user', 'root_node_id']
    read_only_fields = ['template']

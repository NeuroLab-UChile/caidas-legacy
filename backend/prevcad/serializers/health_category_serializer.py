import base64
from rest_framework import serializers
from django.utils.encoding import smart_str

from prevcad.models import HealthCategory


from rest_framework import serializers
from prevcad.models import HealthCategory

class HealthCategorySerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    def get_icon(self, obj):
        if obj.icon and hasattr(obj.icon, 'path'):
            try:
                with open(obj.icon.path, 'rb') as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            except Exception as e:
                print(f"Error reading image file: {e}")
                return None
        return None

    def to_representation(self, instance):
        # Convert name to proper string encoding
        instance.name = smart_str(instance.name)
        return super().to_representation(instance)

    class Meta:
        model = HealthCategory
        fields = ['id', 'name', 'icon', 'template', 'user', 'root_node_id']
        read_only_fields = ['template']

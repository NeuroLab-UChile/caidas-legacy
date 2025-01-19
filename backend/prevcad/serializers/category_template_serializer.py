from prevcad.models import CategoryTemplate
from rest_framework import serializers
import base64

class CategoryTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryTemplate
        fields = ['id', 'name', 'icon', 'default_recommendations']

    def get_icon(self, obj):
        if obj.icon:
            return obj.get_icon_base64()
        return None
    


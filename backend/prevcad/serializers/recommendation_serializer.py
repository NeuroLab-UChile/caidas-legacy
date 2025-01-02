from rest_framework import serializers
from ..models import Recommendation

class RecommendationSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.SerializerMethodField()
    status_color_display = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = [
            'id', 'status_color', 'status_color_display', 
            'text', 'updated_by', 'updated_by_name',
            'updated_at', 'is_draft'
        ]

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.user.get_full_name()}"
        return None

    def get_status_color_display(self, obj):
        return obj.get_status_color_display() 
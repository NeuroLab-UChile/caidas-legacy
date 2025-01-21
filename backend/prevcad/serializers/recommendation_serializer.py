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
            'updated_at', 'is_draft', 'media_url'
        ]

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.user.get_full_name()}"
        return None

    def get_status_color_display(self, obj):
        return obj.get_status_color_display() 

    def get_media_url(self, request=None):
        from django.conf import settings
        """Método base para obtener URL absoluta de archivos multimedia"""
        media_field = None
        print(self.video)
        
        if hasattr(self, 'video'):
            media_field = request.build_absolute_uri(settings.MEDIA_URL + self.video.url)
        elif hasattr(self, 'image'):
            media_field = request.build_absolute_uri(settings.MEDIA_URL + self.image.url)
        
        if media_field:
            return request.build_absolute_uri(settings.MEDIA_URL + media_field.url)
        return None

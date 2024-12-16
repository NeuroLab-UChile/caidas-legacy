import base64
from rest_framework import serializers
from django.utils.encoding import smart_str
from prevcad.models import HealthCategory
from .activity_node_serializer import ActivityNodeDescriptionSerializer, ResultNodeSerializer


class HealthCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    evaluation_form = serializers.SerializerMethodField()
    training_nodes = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = HealthCategory
        fields = [
            'id', 
            'name', 
            'icon', 
            'evaluation_form',
            'training_nodes',
            'responses',
            'completion_date',
            'status_color',
            'doctor_recommendations',
            'status'
        ]

    def get_name(self, obj):
        return obj.template.name if obj.template else None

    def get_icon(self, obj):
        if obj.template and obj.template.icon:
            return obj.template.icon.url
        return None

    def get_evaluation_form(self, obj):
        if obj.template:
            return obj.template.evaluation_form
        return None

    def get_training_nodes(self, obj):
        if obj.template:
            return obj.template.training_nodes
        return None

    def get_status(self, obj):
        if not obj.status_color:
            return None
            
        status_map = {
            'green': {'color': 'green', 'text': 'Saludable'},
            'yellow': {'color': 'yellow', 'text': 'Precaución'},
            'red': {'color': 'red', 'text': 'Atención Requerida'}
        }
        
        return status_map.get(obj.status_color, None)

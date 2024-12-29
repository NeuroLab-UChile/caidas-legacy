import base64
from rest_framework import serializers
from django.utils.encoding import smart_str
from prevcad.models import HealthCategory, CategoryTemplate
from .activity_node_serializer import ActivityNodeDescriptionSerializer, ResultNodeSerializer


class HealthCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    evaluation_form = serializers.SerializerMethodField()
    training_form = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    doctor_recommendations_updated_by = serializers.SerializerMethodField()
    doctor_recommendations_updated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Solo incluir recomendaciones si no es borrador
        if instance.is_draft:
            ret['doctor_recommendations'] = None
            ret['doctor_recommendations_updated_at'] = None
            ret['doctor_recommendations_updated_by'] = None
            ret['status_color'] = None
        return ret

    class Meta:
        model = HealthCategory
        fields = '__all__'

    def get_name(self, obj):
        return obj.template.name if obj.template else None

    def get_icon(self, obj):
        if obj.template and obj.template.icon:
            print("Icon:", obj.template.icon)
            return obj.template.get_icon_base64()
        return None

    def get_evaluation_form(self, obj):
        if obj.template:
            return obj.template.evaluation_form
        print("No se encontró template")
        return None

    def get_training_form(self, obj):
        if obj.template:
            return obj.template.training_form
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

    def get_description(self, obj):
        """Obtener la descripción del template"""
        print(f"Getting description for category {obj.id}")
        if obj.template and obj.template.root_node:
            return obj.template.root_node.description
        if obj.template:
            return obj.template.description
        print("No description found")
        return None
    

    def get_responses(self, obj):
        return obj.responses

    def get_doctor_recommendations_updated_by(self, obj):
        if obj.doctor_recommendations_updated_by:
            return {
                'id': obj.doctor_recommendations_updated_by.id,
                'username': obj.doctor_recommendations_updated_by.username,
                'first_name': obj.doctor_recommendations_updated_by.first_name,
                'last_name': obj.doctor_recommendations_updated_by.last_name
            }
        return None

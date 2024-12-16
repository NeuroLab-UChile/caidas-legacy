import base64
from rest_framework import serializers
from django.utils.encoding import smart_str
from prevcad.models import HealthCategory
from .activity_node_serializer import ActivityNodeDescriptionSerializer, ResultNodeSerializer


class HealthCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    evaluation_form = serializers.SerializerMethodField()
    training_nodes = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_info = serializers.SerializerMethodField()

    class Meta:
        model = HealthCategory
        fields = [
            'id', 
            'name', 
            'icon', 
            'description',
            'evaluation_form',
            'training_nodes',
            'responses',
            'completion_date',
            'status',
            'status_color',
            'doctor_recommendations',
            'status_info'
        ]

    def get_name(self, obj):
        return obj.template.name if obj.template else None

    def get_icon(self, obj):
        if obj.template and obj.template.icon:
            return obj.template.icon.url
        return None

    def get_evaluation_form(self, obj):
        print(f"\nSerializando evaluation_form para categoría {obj.id}")
        if obj.template:
            print(f"Template encontrado: {obj.template.id}")
            print(f"Evaluation form: {obj.template.evaluation_form}")
            return obj.template.evaluation_form
        print("No se encontró template")
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

    def get_description(self, obj):
        """Obtener la descripción del template"""
        print(f"Getting description for category {obj.id}")
        if obj.template and obj.template.root_node:
            print(f"Root node description: {obj.template.root_node.description}")
            return obj.template.root_node.description
        if obj.template:
            print(f"Template description: {obj.template.description}")
            return obj.template.description
        print("No description found")
        return None

    def get_status_info(self, obj):
        if obj.doctor_recommendations and obj.status_color:
            return {
                'status': 'reviewed',
                'text': '✅ Evaluación Revisada por Doctor'
            }
        
        if obj.completion_date:
            return {
                'status': 'completed',
                'text': '✅ Evaluación Completada'
            }
        
        if obj.responses:
            total_questions = len(obj.template.evaluation_form.get('question_nodes', []))
            answered_questions = len(obj.responses)
            if answered_questions > 0:
                return {
                    'status': 'in_progress',
                    'text': f'📝 Evaluación en Progreso ({answered_questions}/{total_questions})'
                }
        
        return {
            'status': 'pending',
            'text': '📝 Evaluación Pendiente'
        }

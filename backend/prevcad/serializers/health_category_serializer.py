import base64
from rest_framework import serializers
from django.utils.encoding import smart_str
from prevcad.models import HealthCategory, CategoryTemplate
from .activity_node_serializer import ActivityNodeDescriptionSerializer, ResultNodeSerializer


class HealthCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    evaluation_type = serializers.SerializerMethodField()
    evaluation_form = serializers.SerializerMethodField()
    evaluation_results = serializers.SerializerMethodField()
    training_form = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    professional_info = serializers.SerializerMethodField()
    professional_evaluation_result = serializers.SerializerMethodField()

    class Meta:
        model = HealthCategory
        fields = [
            'id', 
            'name', 
            'icon', 
            'description',
            'evaluation_type',
            'evaluation_form',
            'evaluation_results',
            'training_form',
            'completion_date',
            'status',
            'professional_info',
            'is_draft',
            'professional_evaluation_result'
        ]

    def get_name(self, obj):
        return obj.template.name if obj.template else None

    def get_icon(self, obj):
        if obj.template and obj.template.icon:
            return obj.template.get_icon_base64()
        return None

    def get_evaluation_type(self, obj):
        """Obtener el tipo de evaluación y su etiqueta"""
        if not obj.template:
            return None
            
        types = {
            'SELF': 'Autoevaluación',
            'PROFESSIONAL': 'Evaluación Profesional'
        }
        return {
            'type': obj.template.evaluation_type,
            'label': types.get(obj.template.evaluation_type, 'Desconocido')
        }

    def get_evaluation_form(self, obj):
        """Obtener el formulario de evaluación según el tipo"""
        if not obj.template:
            return None
            
        return obj.template.get_evaluation_form()

    def get_evaluation_results(self, obj):
        """Obtener los resultados de evaluación según el tipo"""
        if not obj.template:
            return None
            
        results = obj.get_evaluation_results()
        if not results:
            return None

        # Agregar metadatos según el tipo de evaluación
        if obj.template.evaluation_type == 'PROFESSIONAL':
            return {
                'data': results.get('evaluation_data'),
                'professional': {
                    'id': results.get('professional_id'),
                    'name': results.get('professional_name')
                },
                'date': results.get('date'),
                'updated_at': results.get('updated_at')
            }
        else:
            return {
                'data': results.get('evaluation_data'),
                'date': results.get('date'),
                'updated_at': results.get('updated_at')
            }

    def get_training_form(self, obj):
        if obj.template:
            return obj.template.training_form
        return None

    def get_professional_evaluation_result(self, obj):
        if obj.template.evaluation_type == 'PROFESSIONAL':
            return obj.professional_evaluation_result
        return None

    def get_status(self, obj):
        """Obtener información completa del estado"""
        status_colors = {
            'verde': {'color': 'green', 'text': 'Saludable'},
            'amarillo': {'color': 'yellow', 'text': 'Precaución'},
            'rojo': {'color': 'red', 'text': 'Atención Requerida'},
            'gris': {'color': 'gray', 'text': 'Sin evaluar'}
        }
        
        draft_status = {
            True: 'Borrador',
            False: 'Publicado'
        }
        
        return {
            'color': status_colors.get(obj.status_color, status_colors['gris']),
            'draft': draft_status.get(obj.is_draft, 'Borrador'),
            'has_evaluation': bool(obj.get_evaluation_results())
        }

    def get_professional_info(self, obj):
        """Obtener información del profesional que realizó la última actualización"""
        if not obj.professional_recommendations_updated_by:
            return None
            
        return {
            'name': obj.professional_recommendations_updated_by,
            'date': obj.professional_recommendations_updated_at.strftime('%d/%m/%Y %H:%M') if obj.professional_recommendations_updated_at else None,
            'recommendations': obj.professional_recommendations,
            'is_draft': obj.is_draft
        }

    def get_description(self, obj):
        if not obj.template:
            return None
            
        return (obj.template.root_node.description 
                if obj.template.root_node 
                else obj.template.description)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Asegurar que los campos requeridos estén presentes
        required_fields = {
            'professional_info': None,
            'is_draft': True,
            'evaluation_results': None
        }
        
        for field, default in required_fields.items():
            if field not in data:
                data[field] = default
                
        return data

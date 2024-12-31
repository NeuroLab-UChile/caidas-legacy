import base64
from rest_framework import serializers
from django.utils.encoding import smart_str
from prevcad.models import HealthCategory, CategoryTemplate

class HealthCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    evaluation_type = serializers.SerializerMethodField()
    evaluation_form = serializers.SerializerMethodField()
    evaluation_results = serializers.SerializerMethodField()
    training_form = serializers.SerializerMethodField()

   
    professional_evaluation_results = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()

    STATUS_COLORS = {
        'verde': {'color': '#008000', 'text': '✅ Evaluación Completada'},
        'amarillo': {'color': '#FFFF00', 'text': '🟡 Evaluación Pendiente'},
        'gris': {'color': '#808080', 'text': '⚪️ Sin Evaluación'},
    }

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
            'is_draft',
            'professional_evaluation_results',
            'recommendations'
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



    def get_evaluation_results(self, obj):
        """Obtener los resultados de evaluación según el tipo"""
        if not obj.template:
            return None
            
     
            return None

        # Agregar metadatos según el tipo de evaluación
        if obj.template.evaluation_type == 'PROFESSIONAL':
            return {
                'data': obj.professional_evaluation_results.get('evaluation_data'),
                'professional': {
                    'id': obj.professional_evaluation_results.get('professional_id'),
                    'name': obj.professional_evaluation_results.get('professional_name')
                },
                'date': obj.professional_evaluation_results.get('date'),
                'updated_at': obj.professional_evaluation_results.get('updated_at')
            }
        else:
            return {
                'data': obj.responses.get('evaluation_data'),
                'date': obj.responses.get('date'),
                'updated_at': obj.responses.get('updated_at')
            }

    def get_training_form(self, obj):
        if obj.template:
            return obj.template.training_form
        return None

    def get_professional_evaluation_results(self, obj):
        if obj.template.evaluation_type == 'PROFESSIONAL':
            return obj.professional_evaluation_results
        return None

    def get_status(self, obj):
        """Obtener información completa del estado"""
        status_info = self.STATUS_COLORS.get(obj.status_color, self.STATUS_COLORS['gris'])
        
        # Obtener el tipo de evaluación del template
        evaluation_type = obj.template.evaluation_type if obj.template else None
        
        # Determinar si está completado según el tipo de evaluación
        has_responses = False
        if evaluation_type == 'SELF':
            has_responses = bool(obj.responses)
        elif evaluation_type == 'PROFESSIONAL':
            has_responses = bool(obj.professional_evaluation_results)
        
        is_completed = bool(has_responses)
        
        return {
            'color': status_info,
            'draft': 'Borrador' if obj.is_draft else 'Publicado',
            'has_evaluation': is_completed,
            'professional_reviewed': bool(obj.professional_evaluation_results)
        }


        """Obtener información del profesional que realizó la última actualización"""
        if not obj.professional_recommendations_updated_by:
            return None
            
        return {
            'name': obj.professional_recommendations_updated_by,
            'date': obj.professional_recommendations_updated_at.strftime('%d/%m/%Y %H:%M') if obj.professional_recommendations_updated_at else None,
            'recommendations': obj.professional_recommendations,
            'is_draft': obj.is_draft
        }
    def get_evaluation_form(self, obj):
        """Obtener el formulario de evaluación del template."""
        return obj.template.evaluation_form
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
       
            'is_draft': True,
            'evaluation_results': None
        }
        
        for field, default in required_fields.items():
            if field not in data:
                data[field] = default
                
        return data

    def get_recommendations(self, obj):
        """
        Obtener las recomendaciones con status, información profesional y metadata
        """
        if not obj.template:
            return None

        # Obtener el status actual
        status_info = self.STATUS_COLORS.get(obj.status_color, self.STATUS_COLORS['gris'])
        
        # Si es evaluación profesional
        if obj.template.evaluation_type == 'PROFESSIONAL' and obj.professional_evaluation_results:
            return {
                'status': {
                    'color': status_info['color'],
                    'text': status_info['text']
                },
                'professional': {
                    'id': obj.professional_evaluation_results.get('professional_id'),
                    'name': obj.professional_evaluation_results.get('professional_name')
                },
                'updated_at': obj.professional_evaluation_results.get('updated_at'),
                'text': obj.professional_evaluation_results.get('recommendations')
            }
        
        # Para autoevaluación o sin evaluación profesional
        recommendations_text = None
        if obj.use_default_recommendations and obj.template.default_recommendations:
            recommendations = obj.template.default_recommendations.get(obj.status_color, {})
            recommendations_text = recommendations.get('text')
        elif obj.recommendations and obj.status_color in obj.recommendations:
            recommendations_text = obj.recommendations[obj.status_color].get('text')

        return {
            'status': {
                'color': status_info['color'],
                'text': status_info['text']
            },
            'professional': None,
            'updated_at': obj.completion_date.isoformat() if obj.completion_date else None,
            'text': recommendations_text
        }

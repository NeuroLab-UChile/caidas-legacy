from rest_framework import serializers
from prevcad.models import HealthCategory, CategoryTemplate

class HealthCategorySerializer(serializers.ModelSerializer):
    # Campos básicos
    name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    
    # Campos de evaluación
    evaluation_type = serializers.SerializerMethodField()
    evaluation_form = serializers.SerializerMethodField()
    evaluation_results = serializers.SerializerMethodField()
    
    # Campos de estado y recomendaciones
    status = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()
    
    # Campos adicionales
    training_form = serializers.SerializerMethodField()

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
            'status',
            'recommendations',
            'training_form',
        ]

    def get_template_attribute(self, obj, attr, default=None):
        """Helper para obtener atributos del template de forma segura"""
        return getattr(obj.template, attr, default) if obj.template else default

    def get_evaluation_attribute(self, obj, attr, default=None):
        """Helper para obtener atributos del evaluation_form de forma segura"""
        try:
            evaluation_form = obj.get_or_create_evaluation_form()
            return getattr(evaluation_form, attr, default)
        except Exception as e:
            print(f"Error getting evaluation attribute {attr}: {str(e)}")
            return default

    def get_recommendation_attribute(self, obj, attr, default=None):
        """Helper para obtener atributos de recommendation de forma segura"""
        try:
            recommendation = obj.get_or_create_recommendation()
            return getattr(recommendation, attr, default)
        except Exception as e:
            print(f"Error getting recommendation attribute {attr}: {str(e)}")
            return default

    # Getters básicos
    def get_name(self, obj):
        return self.get_template_attribute(obj, 'name')

    def get_icon(self, obj):
        if obj.template and obj.template.icon:
            return obj.template.get_icon_base64()
        return None

    def get_description(self, obj):
        return (self.get_template_attribute(obj, 'root_node.description') or 
                self.get_template_attribute(obj, 'description'))

    def get_evaluation_type(self, obj):
        eval_type = self.get_template_attribute(obj, 'evaluation_type')
        if not eval_type:
            return None
            
        types = {
            'SELF': 'Autoevaluación',
            'PROFESSIONAL': 'Evaluación Profesional'
        }
        return {
            'type': eval_type,
            'label': types.get(eval_type, 'Desconocido')
        }

    def get_evaluation_form(self, obj):
        """Obtener el formulario de evaluación"""
        return self.get_template_attribute(obj, 'evaluation_form')

    def get_evaluation_results(self, obj):
        """Obtener resultados de evaluación"""
        if not obj.template or not hasattr(obj, 'evaluation_form'):
            return None

        eval_form = obj.evaluation_form
        is_professional = obj.template.evaluation_type == 'PROFESSIONAL'

        base_result = {
            'completed_date': eval_form.completed_date.isoformat() if eval_form.completed_date else None,
            'is_completed': bool(eval_form.completed_date),
        }

        if is_professional:
            base_result.update({
                'professional_responses': eval_form.professional_responses,
                'updated_at': eval_form.completed_date.isoformat() if eval_form.completed_date else None
            })
        else:
            base_result.update({
                'responses': eval_form.responses,
                'question_nodes': eval_form.question_nodes
            })

        return base_result

    def get_status(self, obj):
        """Obtener estado completo"""
        try:
            evaluation_form = obj.get_or_create_evaluation_form()
            recommendation = obj.get_or_create_recommendation()
            
            status_color = self.get_recommendation_attribute(obj, 'status_color', 'gris')
            status_info = self.STATUS_COLORS.get(status_color, self.STATUS_COLORS['gris'])
            
            return {
                'color': status_info['color'],
                'text': status_info['text'],
                'is_completed': bool(evaluation_form.completed_date),
                'is_draft': self.get_recommendation_attribute(obj, 'is_draft', True),
                'last_updated': self.get_recommendation_attribute(obj, 'updated_at'),
                'professional_reviewed': (
                    bool(evaluation_form.professional_responses) 
                    if obj.template.evaluation_type == 'PROFESSIONAL' 
                    else None
                )
            }
        except Exception as e:
            print(f"Error getting status: {str(e)}")
            return self.get_default_status()

    def get_recommendations(self, obj):
        """Obtener recomendaciones"""
        if not obj.template:
            return None

        try:
            status = self.get_status(obj)
            recommendation = obj.get_or_create_recommendation()

            base_recommendation = {
                'status': {
                    'color': status['color'],
                    'text': status['text']
                },
                'text': self.get_recommendation_attribute(obj, 'text'),
                'updated_at': self.get_recommendation_attribute(obj, 'updated_at'),
                'is_draft': self.get_recommendation_attribute(obj, 'is_draft', True)
            }

            if obj.template.evaluation_type == 'PROFESSIONAL':
                base_recommendation['professional'] = {
                    'name': self.get_recommendation_attribute(obj, 'updated_by'),
                }

            return base_recommendation
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            return None

    def get_training_form(self, obj):
        return self.get_template_attribute(obj, 'training_form')

    def get_default_status(self):
        """Helper para obtener estado por defecto"""
        return {
            'color': self.STATUS_COLORS['gris']['color'],
            'text': self.STATUS_COLORS['gris']['text'],
            'is_completed': False,
            'is_draft': True,
            'last_updated': None,
            'professional_reviewed': None
        }

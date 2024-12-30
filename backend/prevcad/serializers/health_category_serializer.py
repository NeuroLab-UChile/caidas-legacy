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
    status_color = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    professional_recommendations_updated_by = serializers.SerializerMethodField()
    professional_recommendations_updated_at = serializers.DateTimeField(read_only=True)
    is_draft = serializers.BooleanField(read_only=True)

    class Meta:
        model = HealthCategory
        fields = [
            'id', 
            'name', 
            'icon', 
            'description',
            'evaluation_form',
            'training_form',
            'responses',
            'completion_date',
            'status_color',
            'professional_recommendations',
            'is_draft',
            'status_display',
            'professional_recommendations_updated_by',
            'professional_recommendations_updated_at'
        ]

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

    def get_status_color(self, obj):
        if not obj.status_color:
            return None
            
        status_map = {
            'verde': {'color': 'green', 'text': 'Saludable'},
            'amarillo': {'color': 'yellow', 'text': 'Precaución'},
            'rojo': {'color': 'red', 'text': 'Atención Requerida'},
            'gris': {'color': 'gray', 'text': 'Sin evaluar'}
        }
        
        return status_map.get(obj.status_color, None)
    
    def get_status_display(self, obj):
        """
        Devuelve el texto del estado de las recomendaciones usando el display del modelo
        """
        if hasattr(obj, 'get_is_draft_display'):
            return obj.get_is_draft_display()
        
        # Fallback por si acaso
        status_map = {
            'borrador': 'Borrador',
            'publicado': 'Publicado',
            'archivado': 'Archivado'
        }
        return status_map.get(obj.is_draft, 'Borrador')  # Default a 'Borrador'

    def get_description(self, obj):
        """Obtener la descripción del template"""
        if obj and obj.template:
            if obj.template.root_node:
                return obj.template.root_node.description
            return obj.template.description
        return None

    def get_professional_recommendations_updated_by(self, obj):
        """
        Devuelve el nombre del usuario que actualizó las recomendaciones.
        """
        if obj.professional_recommendations_updated_by:
            return {
                'name': obj.professional_recommendations_updated_by,
                'date': obj.professional_recommendations_updated_at.strftime('%d/%m/%Y %H:%M') if obj.professional_recommendations_updated_at else None
            }
        return None

    def to_representation(self, instance):
        """
        Personaliza la representación final del objeto
        """
        data = super().to_representation(instance)
        
        # Asegura que los campos de recomendaciones estén presentes
        if 'professional_recommendations' not in data:
            data['professional_recommendations'] = None
            
        if 'is_draft' not in data:
            data['is_draft'] = True
            
        return data

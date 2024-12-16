import base64
from rest_framework import serializers
from django.utils.encoding import smart_str
from prevcad.models import HealthCategory
from .activity_node_serializer import ActivityNodeDescriptionSerializer, ResultNodeSerializer


class HealthCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    root_node = serializers.SerializerMethodField()
    evaluation_form = serializers.SerializerMethodField()
    responses = serializers.JSONField(required=False)
    score = serializers.IntegerField(required=False)
    completion_date = serializers.DateTimeField(required=False)
    recommendations = serializers.JSONField(required=False)
    

    def get_name(self, obj):
        """Returns the name of the category template"""
        print(f"\nDebug get_name para categoría {obj.id}")
        name = smart_str(obj.template.name) if obj.template else None
        print(f"Nombre obtenido: {name}")
        return name

    def get_icon(self, obj):
        """Returns the icon in base64 encoding, or None if not available"""
        print(f"\nDebug get_icon para categoría {obj.id}")
        if obj.template and obj.template.icon and hasattr(obj.template.icon, 'path'):
            try:
                with open(obj.template.icon.path, 'rb') as image_file:
                    icon_data = base64.b64encode(image_file.read()).decode('utf-8')
                    print("Icon cargado exitosamente")
                    return icon_data
            except Exception as e:
                print(f"Error reading image file: {e}")
                return None
        print("No se encontró icon")
        return None

    def get_root_node(self, obj):
        """Returns the root node data"""
        print(f"\nDebug get_root_node para categoría {obj.id}")
        if not obj.template:
            print("No template encontrado")
            return None
            
        root_node = {
            "type": "CATEGORY_DESCRIPTION",
            "description": obj.template.description,
            "first_button_text": "Comenzar Evaluación",
            "first_button_node_id": obj.evaluation_form.get("question_nodes", [])[0].get("id") if obj.evaluation_form else None
        }
        print(f"Root node creado: {root_node}")
        return root_node

    def get_evaluation_form(self, obj):
        """Returns the evaluation form from the template"""
        print(f"\nDebug get_evaluation_form para categoría {obj.id}")
        form = obj.template.evaluation_form if obj.template else None
        print(f"Evaluation form: {form}")
        return form

    class Meta:
        model = HealthCategory
        fields = ['id', 'name', 'icon', 'root_node', 'evaluation_form', 
                 'responses', 'score', 'completion_date', 'recommendations']

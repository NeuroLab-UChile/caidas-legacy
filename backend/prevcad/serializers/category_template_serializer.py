from prevcad.models import CategoryTemplate
from rest_framework import serializers
from .activity_node_serializer import ActivityNodeSerializer
from prevcad.utils import build_media_url

class CategoryTemplateSerializer(serializers.ModelSerializer):
    training_form = serializers.SerializerMethodField()

    class Meta:
        model = CategoryTemplate
        fields = ['id', 'name', 'icon', 'default_recommendations', 'training_form']

    def get_icon(self, obj):
        if obj.icon:
            return obj.get_icon_base64()
        return None
    
    def serialize_node(self, node):
        """Helper method para serializar nodos individuales"""
        from prevcad.serializers.activity_node_serializer import ActivityNodeSerializer
        
        try:
            serializer = ActivityNodeSerializer(node)
            return serializer.data
        except Exception as e:
            print(f"Error serializing node {node.id}: {str(e)}")
            return {}

    def get_training_form(self, obj):
        try:
            if not obj.training_form:
                return None

            # Obtener los nodos de entrenamiento
            training_nodes = obj.training_form.get_nodes()
            if not training_nodes:
                return None

            # Serializar nodos con sus media_files
            serialized_nodes = []
            for node in training_nodes:
                node_data = ActivityNodeSerializer(node).data
                
                # Asegurarse de que media_file se procese correctamente
                if hasattr(node, 'media_file') and node.media_file:
                    node_data['media_url'] = build_media_url(node.media_file)
                
                serialized_nodes.append(node_data)

            return {
                'training_nodes': serialized_nodes
            }
        except Exception as e:
            print(f"Error en get_training_form: {str(e)}")
            return None
    

    


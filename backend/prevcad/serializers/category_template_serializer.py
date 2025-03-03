from prevcad.models import CategoryTemplate
from rest_framework import serializers
from .activity_node_serializer import ActivityNodeSerializer

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

            # Usar ActivityNodeSerializer para cada nodo
            serialized_nodes = []
            for node in training_nodes:
                serialized_node = ActivityNodeSerializer(node).data
                serialized_nodes.append(serialized_node)

            return {
                'training_nodes': serialized_nodes
            }
        except Exception as e:
            print(f"Error en get_training_form: {str(e)}")
            return None
    

    


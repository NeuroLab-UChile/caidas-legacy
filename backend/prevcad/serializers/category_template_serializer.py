from prevcad.models import CategoryTemplate, VideoNode, ImageNode
from rest_framework import serializers

class CategoryTemplateSerializer(serializers.ModelSerializer):
    training_form = serializers.SerializerMethodField()

    class Meta:
        model = CategoryTemplate
        fields = ['id', 'name', 'icon', 'default_recommendations', 'training_form']

    def get_icon(self, obj):
        if obj.icon:
            return obj.get_icon_base64()
        return None
    
    def get_training_form(self, obj):
        try:
            if not obj.training_form:
                print("No training form found")  # Debug
                return None

            training_nodes = obj.training_form.get_nodes()
            if not training_nodes:
                print("No nodes found")  # Debug
                return None

            serialized_nodes = []
            for node in training_nodes:
                # Forzar URLs completas según el tipo de nodo
                node_data = {
                    'id': node.id,
                    'title': getattr(node, 'title', ''),
                    'description': getattr(node, 'description', ''),
                    'type': node.__class__.__name__.upper(),
                    'next_node_id': getattr(node, 'next_node_id', None),
                }

                if isinstance(node, VideoNode):
                    node_data['media_url'] = "https://caidas.uchile.cl/media/training_videos/warmup.mp4"
                elif isinstance(node, ImageNode):
                    node_data['media_url'] = "https://caidas.uchile.cl/media/training/balance-exercises.jpg"

                print(f"Node serialized: {node_data}")  # Debug
                serialized_nodes.append(node_data)

            return {
                'training_nodes': serialized_nodes
            }

        except Exception as e:
            print(f"Error in get_training_form: {str(e)}")
            return None
    

    


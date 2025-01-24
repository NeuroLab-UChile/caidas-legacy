from prevcad.models import CategoryTemplate
from rest_framework import serializers
import base64

class CategoryTemplateSerializer(serializers.ModelSerializer):

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
        if not obj.template:
            return None
        
        if not obj.template.training_form:
            return None 
        
        training_form = obj.training_form
        if not training_form:
            return None
        
        training_nodes = training_form.get('training_nodes')
        if not training_nodes:
            return None
        serialized_training_nodes = []
        for node, index in enumerate(training_nodes):
          
            node_data = self.serialize_node(node)
            print('node_data',node_data)
     
            serialized_training_nodes.append(node_data)


        print('serialized_training_nodes',serialized_training_nodes)
        training_form['training_nodes'] = serialized_training_nodes
      
            
                
            
        
        return training_form
    

    


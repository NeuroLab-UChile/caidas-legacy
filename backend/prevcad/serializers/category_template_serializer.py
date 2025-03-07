from prevcad.models import CategoryTemplate
from rest_framework import serializers
from django.conf import settings
from urllib.parse import urljoin

class CategoryTemplateSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = CategoryTemplate
        fields = ['id', 'name', 'icon', 'default_recommendations', 'training_form']

    def get_icon(self, obj):
        """Retorna la URL absoluta del icono"""
        if not obj.icon:
            return None
            
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.icon.url)
            
        # Si no hay request, usar el dominio de settings
        domain = getattr(settings, 'BASE_URL', 'https://caidas.uchile.cl')
        return urljoin(domain, f'/media/{obj.icon.name}')
    
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
        if not obj.training_form:
            return None
        
        training_form = obj.training_form.copy()  # Hacer una copia para no modificar el original
        training_nodes = training_form.get('training_nodes', [])
        
        # Convertir URLs relativas a absolutas
        for node in training_nodes:
            if node.get('media_url'):
                request = self.context.get('request')
                if request:
                    node['media_url'] = request.build_absolute_uri(f'/media/{node["media_url"]}')
                else:
                    # Si no hay request, usar el dominio de settings
                    domain = getattr(settings, 'BASE_URL', 'https://caidas.uchile.cl')
                    node['media_url'] = urljoin(domain, f'/media/{node["media_url"]}')
        
        training_form['training_nodes'] = training_nodes
        return training_form
    

    


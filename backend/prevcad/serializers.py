from rest_framework import serializers
from django.utils.encoding import smart_str
from prevcad.models import HealthCategory, TextRecomendation

class HealthCategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()

    class Meta:
        model = HealthCategory
        fields = '__all__'

    def to_representation(self, instance):
        # Asegurarte de que los campos se codifiquen correctamente
        instance.name = smart_str(instance.name)
        instance.description = smart_str(instance.description)
        return super().to_representation(instance)


class TextRecomendationSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255)
    inside_text = serializers.CharField()

    class Meta:
        model = TextRecomendation
        fields = '__all__'

    def to_representation(self, instance):
        # Asegurarte de que los campos se codifiquen correctamente
        instance.title = smart_str(instance.title)
        instance.inside_text = smart_str(instance.inside_text)
        return super().to_representation(instance)

from rest_framework import serializers
from django.db import models
from ..models import (
    ActivityNodeDescription,
    TextQuestion,
    SingleChoiceQuestion,
    MultipleChoiceQuestion,
    ScaleQuestion,
    ImageQuestion,
    ResultNode,
    WeeklyRecipeNode,
    VideoNode,
    TextNode,
    ImageNode
)

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
import os
from prevcad.utils import build_media_url
import logging

logger = logging.getLogger(__name__)

# Serializador base para ActivityNode
class ActivityNodeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'title', 'description', 'type', 'next_node_id', 'media_url']

    def to_representation(self, instance):
        data = {
            'id': instance.id,
            'title': getattr(instance, 'title', None),
            'description': getattr(instance, 'description', None),
            'type': instance.__class__.__name__.upper(),
            'next_node_id': getattr(instance, 'next_node_id', None),
        }
        
        # Forzar URL completa para videos y otros archivos
        if isinstance(instance, VideoNode):
            data['media_url'] = "https://caidas.uchile.cl/media/training_videos/warmup.mp4"
        elif isinstance(instance, ImageNode):
            data['media_url'] = "https://caidas.uchile.cl/media/training/balance-exercises.jpg"
            
        return data


# Serializadores específicos para cada tipo de nodo
class ActivityNodeDescriptionSerializer(serializers.ModelSerializer):
    next_node_type = serializers.CharField(write_only=True, required=False, allow_null=True)
    next_node_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ActivityNodeDescription
        fields = '__all__'
        extra_fields = ['next_node_type', 'next_node_id']

    def create(self, validated_data):
        next_node_type = validated_data.pop('next_node_type', None)
        next_node_id = validated_data.pop('next_node_id', None)

        instance = super().create(validated_data)

        if next_node_type and next_node_id:
            content_type = ContentType.objects.get(model=next_node_type.lower())
            instance.content_type = content_type
            instance.object_id = next_node_id
            instance.save()

        return instance

    def update(self, instance, validated_data):
        next_node_type = validated_data.pop('next_node_type', None)
        next_node_id = validated_data.pop('next_node_id', None)

        instance = super().update(instance, validated_data)

        if next_node_type and next_node_id:
            content_type = ContentType.objects.get(model=next_node_type.lower())
            instance.content_type = content_type
            instance.object_id = next_node_id
            instance.save()

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.next_node:
            data['next_node_type'] = instance.next_node._meta.model_name
            data['next_node_id'] = instance.next_node.id
        return data

class TextQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextQuestion
        fields = '__all__'

class SingleChoiceQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleChoiceQuestion
        fields = '__all__'

class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceQuestion
        fields = '__all__'

class ScaleQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScaleQuestion
        fields = '__all__'

class ImageQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageQuestion
        fields = '__all__'


class ResultNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultNode
        fields = '__all__'


class WeeklyRecipeNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyRecipeNode
        fields = '__all__'


class VideoNodeSerializer(serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()


    
    class Meta:
        model = VideoNode
        fields = '__all__'
        extra_fields = ['media_url']


    def get_media_url(self, obj):
        if hasattr(obj, 'media_file') and obj.media_file: 
            return f"https://caidas.uchile.cl/media/{obj.media_file.name.lstrip('/')}"
        return None

    
    

class TextNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextNode
        fields = '__all__'


class ImageNodeSerializer(serializers.ModelSerializer):
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageNode
        fields = '__all__'
        
    def get_media_url(self, obj):
        if hasattr(obj, 'media_file') and obj.media_file:
            # Construir URL absoluta
            return f"https://caidas.uchile.cl/media/{obj.media_file.name.lstrip('/')}"
        return None




from rest_framework import serializers
from prevcad.models import HealthCategory, TextRecomendation


class HealthCategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = HealthCategory
    fields = '__all__'


class TextRecomendationSerializer(serializers.ModelSerializer):
  class Meta:
    model = TextRecomendation
    fields = '__all__'

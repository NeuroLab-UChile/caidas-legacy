from rest_framework import serializers
from django.utils.encoding import smart_str

from prevcad.models import (
  TextRecomendation,
)


class TextRecomendationSerializer(serializers.ModelSerializer):
  class Meta:
    model = TextRecomendation
    fields = [
      'id',
      'theme',
      'category',
      'sub_category',
      'learn',
      'remember',
      'data',
      'practic_data',
      'context_explanation',
      'quote_link',
      'keywords',

    ]

  def to_representation(self, instance):
    instance.theme = smart_str(instance.theme)
    instance.category = smart_str(instance.category)
    instance.sub_category = smart_str(instance.sub_category)
    instance.learn = smart_str(instance.learn)
    instance.remember = smart_str(instance.remember)
    instance.data = smart_str(instance.data)
    instance.practic_data = smart_str(instance.practic_data)
    instance.context_explanation = smart_str(instance.context_explanation)
    instance.quote_link = smart_str(instance.quote_link)
    instance.keywords = smart_str(instance.keywords)
    return super().to_representation(instance)

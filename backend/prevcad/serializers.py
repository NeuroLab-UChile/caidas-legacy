from rest_framework import serializers
from django.utils.encoding import smart_str
from prevcad.models import HealthCategory, TextRecomendation, Profile

import base64
from rest_framework import serializers
from django.utils.encoding import smart_str
from prevcad.models import HealthCategory

from django.contrib.auth.models import User


class HealthCategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    image = serializers.SerializerMethodField()  # Campo para la imagen en bytes
    icon = serializers.SerializerMethodField()  # Campo para el icono en bytes

    class Meta:
        model = HealthCategory
        fields = ['id', 'name', 'description', 'image', 'created_at', 'updated_at', 'icon']

    def get_image(self, obj):
        # Convertir la imagen a bytes base64
        if obj.image and hasattr(obj.image, 'path'):
            with open(obj.image.path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')  # Convertir a base64
        return None

    def get_icon(self, obj):
        # Convertir el icono a bytes base64
        if obj.icon and hasattr(obj.icon, 'path'):
            with open(obj.icon.path, 'rb') as icon_file:
                return base64.b64encode(icon_file.read()).decode('utf-8')
        return None
    def to_representation(self, instance):
        # Asegurar que los campos de texto se codifiquen correctamente
        instance.name = smart_str(instance.name)
        instance.description = smart_str(instance.description)
     
        return super().to_representation(instance)

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

  # Sobrescribir el método to_representation para personalizar el JSON
    def to_representation(self, instance):
        # Asegurar que los campos de texto se codifiquen correctamente
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
  

class ProfileSerializer(serializers.ModelSerializer):
  profile_picture = serializers.SerializerMethodField()  # Procesar la imagen como base64

  class Meta:
    model = Profile
    fields = ['profile_picture']  # Puedes agregar más campos si los tienes

  def get_profile_picture(self, obj):
    # Convertir la imagen de perfil a bytes base64
    if obj.profile_picture and hasattr(obj.profile_picture, 'path'):
      with open(obj.profile_picture.path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    return None
class UserSerializer(serializers.ModelSerializer):
  profile = ProfileSerializer()  # Relacionamos el perfil con el usuario

  class Meta:
    model = User
    fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']  # Incluimos el perfil
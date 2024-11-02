import base64
from rest_framework import serializers

from prevcad.models import (
  Profile,
)


class ProfileSerializer(serializers.ModelSerializer):
  profile_picture = serializers.SerializerMethodField()

  class Meta:
    model = Profile
    fields = ['profile_picture']

  def get_profile_picture(self, obj):
    if obj.profile_picture and hasattr(obj.profile_picture, 'path'):
      with open(obj.profile_picture.path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    return None

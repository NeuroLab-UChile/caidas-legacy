from rest_framework import serializers

from django.contrib.auth.models import User
from prevcad.serializers.profile_serializer import ProfileSerializer


class UserSerializer(serializers.ModelSerializer):
  profile = ProfileSerializer(required=False)

  class Meta:
    model = User
    fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

  def to_representation(self, instance):
    data = super().to_representation(instance)
    if data['profile'] is None:
      data['profile'] = {'profile_picture': None}
    return data

from rest_framework import serializers

from django.contrib.auth.models import User
from prevcad.models.profile import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_image', 'phone', 'birth_date']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret.get('profile_image'):
            request = self.context.get('request')
            if request is not None:
                ret['profile_image'] = request.build_absolute_uri(instance.profile_image.url)
        return ret

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        if hasattr(instance, 'profile'):
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            instance.profile.save()
        else:
            Profile.objects.create(user=instance, **profile_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

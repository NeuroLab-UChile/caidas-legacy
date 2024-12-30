from rest_framework import serializers
from django.contrib.auth.models import User
from prevcad.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['profile_image', 'phone', 'birth_date', 'role']

    def get_profile_image(self, obj):
        """
        Obtiene la URL de la imagen de perfil si existe
        """
        if hasattr(obj, 'profile_image') and obj.profile_image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.profile_image.url)
        return None

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']

    def to_representation(self, instance):
        """
        Asegura que el perfil existe y serializa los datos correctamente
        """
        ret = super().to_representation(instance)
        
        # Asegurar que existe el perfil
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance)
            instance.refresh_from_db()
        
        # Serializar el perfil con el contexto correcto
        profile_serializer = UserProfileSerializer(
            instance.profile,
            context=self.context
        )
        ret['profile'] = profile_serializer.data
        
        return ret

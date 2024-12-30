from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from prevcad.models.user_profile import UserProfile
from prevcad.serializers.user_profile_serializer import UserProfileSerializer
import os
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def uploadProfileImage(request):
    try:
        user = request.user
        logger.info(f"Procesando imagen para usuario: {user.username}")
        
        # Obtener o crear perfil
        profile, created = UserProfile.objects.get_or_create(user=user)
        logger.info(f"Perfil {'creado' if created else 'encontrado'} para {user.username}")
        
        image = request.FILES.get('profile_image')
        if not image:
            return Response({'error': 'No image provided'}, status=400)
            
        logger.info(f"Imagen recibida: {image.name}")
        
        # Eliminar imagen anterior si existe
        if profile.profile_image:
            try:
                if os.path.isfile(profile.profile_image.path):
                    os.remove(profile.profile_image.path)
                    logger.info("Imagen anterior eliminada")
            except Exception as e:
                logger.warning(f"Error al eliminar imagen anterior: {str(e)}")
        
        # Crear directorio si no existe
        upload_path = f'profile_images/{user.id}'
        os.makedirs(f'media/{upload_path}', exist_ok=True)
        
        # Guardar nueva imagen
        filename = f'{upload_path}/{image.name}'
        profile.profile_image = default_storage.save(filename, image)
        profile.save()
        
        logger.info(f"Imagen guardada: {filename}")
        
        # Refrescar usuario y serializar
        user.refresh_from_db()
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error en uploadProfileImage: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=500
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request):
    try:
        user = request.user
        # Asegurar que existe el perfil
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error en getProfile: {str(e)}")
        return Response(
            {'error': str(e)},
            status=500
        )

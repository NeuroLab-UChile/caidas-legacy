from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from prevcad.models.user_profile import UserProfile
from prevcad.serializers.user_profile_serializer import UserProfileSerializer, UserSerializer
import os
import logging
from ..decorators import log_action

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
@log_action('PROFILE_UPDATE', 'Actualización de imagen de perfil')
def uploadProfileImage(request):
    try:
        # Obtener o crear perfil
        profile = request.user.profile
        if not profile:
            profile = UserProfile.objects.create(user=request.user)
            
        logger.info(f"Procesando imagen para usuario: {request.user.username}")
        
        image = request.FILES.get('profile_image')
        if not image:
            return Response(
                {'error': 'No se proporcionó ninguna imagen'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        logger.info(f"Imagen recibida: {image.name}")
        
        # Eliminar imagen anterior si existe
        if profile.profile_image:
            try:
                profile.profile_image.delete(save=False)
                logger.info("Imagen anterior eliminada")
            except Exception as e:
                logger.warning(f"Error al eliminar imagen anterior: {str(e)}")
        
        # Crear directorio si no existe
        upload_path = f'profile_images/{request.user.id}'
        os.makedirs(os.path.join('media', upload_path), exist_ok=True)
        
        # Guardar nueva imagen
        filename = f'{upload_path}/{image.name}'
        profile.profile_image = default_storage.save(filename, image)
        profile.save()
        
        logger.info(f"Imagen guardada: {filename}")
        
        # Serializar la respuesta
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error en uploadProfileImage: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@log_action('PROFILE_VIEW', 'Visualización de perfil')
def getProfile(request):
    try:
        # Asegurar que existe el perfil
        profile = request.user.profile
        if not profile:
            profile = UserProfile.objects.create(user=request.user)
        
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error en getProfile: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@log_action('PROFILE_UPDATE', 'Eliminación de imagen de perfil')
def deleteProfileImage(request):
    try:
        profile = request.user.profile
        if not profile or not profile.profile_image:
            return Response(
                {'error': 'No hay imagen de perfil para eliminar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Eliminar la imagen
        profile.profile_image.delete(save=False)
        profile.profile_image = None
        profile.save()

        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error en deleteProfileImage: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

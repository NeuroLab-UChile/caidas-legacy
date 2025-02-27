from django.contrib.auth import get_user_model
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
from django.conf import settings

# Obtener el modelo User correcto
User = get_user_model()

logger = logging.getLogger(__name__)

def get_absolute_url(request, url):
    """
    Convierte una URL relativa en absoluta
    """
    if url.startswith('http'):
        return url
    
    # Obtener el dominio del settings.py
    domain = settings.DOMAIN.rstrip('/')
    url = url.lstrip('/')
    return f"{domain}/{url}"

def get_media_url(path):
    from django.conf import settings
    return f"{settings.DOMAIN}/{settings.MEDIA_URL}/{path}"

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
@log_action('PROFILE_UPDATE', 'Actualización de imagen de perfil')
def uploadProfileImage(request):
    logger.info("="*50)
    logger.info("Iniciando uploadProfileImage")
    logger.info(f"Usuario: {request.user}")
    logger.info(f"FILES: {request.FILES}")
    logger.info(f"Headers: {request.headers}")

    try:
        # Verificar si hay archivo
        if 'profile_image' not in request.FILES:
            logger.error("No se encontró 'profile_image' en request.FILES")
            return Response(
                {'error': 'No se proporcionó ninguna imagen'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        image = request.FILES['profile_image']
        logger.info(f"Imagen recibida: {image.name}, tamaño: {image.size}")

        # Usar directamente request.user en lugar de buscar el usuario
        user = request.user
        logger.info(f"Usuario: {user.username}")
        
        # Obtener o crear perfil
        try:
            profile = UserProfile.objects.get_or_create(user=user)[0]
            logger.info(f"Perfil obtenido/creado para: {user.username}")
        except Exception as e:
            logger.error(f"Error al obtener/crear perfil: {str(e)}", exc_info=True)
            raise

        # Crear directorio
        try:
            upload_path = f'profile_images/{request.user.id}'
            full_path = os.path.join(settings.MEDIA_ROOT, upload_path)
            os.makedirs(full_path, exist_ok=True)
            logger.info(f"Directorio creado: {full_path}")
        except Exception as e:
            logger.error(f"Error al crear directorio: {str(e)}", exc_info=True)
            raise

        # Eliminar imagen anterior
        if profile.profile_image:
            try:
                old_path = profile.profile_image.path
                profile.profile_image.delete(save=False)
                logger.info(f"Imagen anterior eliminada: {old_path}")
            except Exception as e:
                logger.warning(f"Error al eliminar imagen anterior: {str(e)}")

        # Guardar nueva imagen
        try:
            filename = f'{upload_path}/{image.name}'
            profile.profile_image = default_storage.save(filename, image)
            profile.save()
            logger.info(f"Nueva imagen guardada: {filename}")
        except Exception as e:
            logger.error(f"Error al guardar nueva imagen: {str(e)}", exc_info=True)
            raise

        # Serializar respuesta
        try:
            serializer = UserSerializer(request.user, context={'request': request})
            logger.info("Perfil serializado exitosamente")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error al serializar respuesta: {str(e)}", exc_info=True)
            raise

    except Exception as e:
        logger.error(f"Error general en uploadProfileImage: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request):
    try:
        user = request.user
        profile = user.profile
        
        # Verificar si la imagen existe físicamente
        if profile.profile_image and profile.profile_image.storage.exists(profile.profile_image.name):
            # Construir la URL correcta
            image_url = request.build_absolute_uri(settings.MEDIA_URL + profile.profile_image.name)
            logger.info(f"URL de imagen construida: {image_url}")
        else:
            logger.warning(f"La imagen no existe en el sistema de archivos: {profile.profile_image.name if profile.profile_image else 'No hay imagen'}")
            image_url = None
            
        # Actualizar el perfil con la URL correcta
        profile.profile_image = image_url
        
        serializer = UserSerializer(user, context={'request': request})
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



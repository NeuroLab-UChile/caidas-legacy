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
import uuid
import base64
from django.core.files.base import ContentFile

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
def uploadProfileImage(request):
    try:
        logger.info("="*50)
        logger.info("Iniciando uploadProfileImage")
        logger.info(f"Usuario: {request.user}")
        
        # Obtener la imagen en base64 del body
        image_data = request.data.get('image')
        if not image_data:
            logger.error("No se encontró imagen en la solicitud")
            return Response(
                {'error': 'No se proporcionó ninguna imagen'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Procesar la imagen base64
        if 'data:' in image_data and ';base64,' in image_data:
            # Separar el header del contenido base64
            format, base64_str = image_data.split(';base64,')
            # Obtener la extensión del archivo
            ext = format.split('/')[-1]
        else:
            base64_str = image_data
            ext = 'jpg'  # default extension

        # Decodificar base64 a archivo
        try:
            image_data = base64.b64decode(base64_str)
        except Exception as e:
            logger.error(f"Error decodificando base64: {str(e)}")
            return Response(
                {'error': 'Imagen inválida'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear un archivo temporal
        filename = f"{uuid.uuid4()}.{ext}"
        upload_path = f'profile_images/{request.user.id}'
        full_path = os.path.join(upload_path, filename)

        # Crear el directorio si no existe
        full_media_path = os.path.join(settings.MEDIA_ROOT, upload_path)
        os.makedirs(full_media_path, exist_ok=True)

        # Guardar la imagen anterior
        profile = request.user.profile
        old_image = profile.profile_image

        # Guardar la nueva imagen
        absolute_path = os.path.join(settings.MEDIA_ROOT, full_path)
        with open(absolute_path, 'wb') as f:
            f.write(image_data)

        # Verificar que el archivo se guardó correctamente
        if not os.path.exists(absolute_path):
            raise Exception("La imagen no se guardó correctamente")

        # Actualizar el perfil
        profile.profile_image = full_path
        profile.save()

        # Eliminar la imagen anterior si existe
        if old_image:
            try:
                old_image_path = os.path.join(settings.MEDIA_ROOT, str(old_image))
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
                    logger.info(f"Imagen anterior eliminada: {old_image_path}")
            except Exception as e:
                logger.error(f"Error al eliminar imagen anterior: {str(e)}")

        # Construir la URL completa
        image_url = request.build_absolute_uri(settings.MEDIA_URL + full_path)
        logger.info(f"URL de imagen construida: {image_url}")

        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error en uploadProfileImage: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request):
    try:
        logger.info("="*50)
        logger.info("Iniciando getProfile")
        logger.info(f"Usuario: {request.user}")
        
        user = request.user
        profile = user.profile
        
        # Construir la URL de la imagen correctamente
        if profile.profile_image:
            # Convertir ImageFieldFile a string usando su URL
            image_url = request.build_absolute_uri(profile.profile_image.url)
            logger.info(f"URL de imagen de perfil: {image_url}")
        else:
            image_url = None
            logger.info("No hay imagen de perfil")
        
        # Serializar el perfil
        serializer = UserSerializer(user, context={'request': request})
        logger.info("Perfil serializado exitosamente")
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



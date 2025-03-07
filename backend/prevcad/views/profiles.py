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
        logger.info(f"FILES: {request.FILES}")
        
        if 'image' not in request.FILES:
            logger.error("No se encontró imagen en la solicitud")
            return Response(
                {'error': 'No se proporcionó ninguna imagen'},
                status=status.HTTP_400_BAD_REQUEST
            )

        image = request.FILES['image']
        profile = request.user.profile

        # Crear el directorio si no existe
        upload_path = f'profile_images/{request.user.id}'
        full_media_path = os.path.join(settings.MEDIA_ROOT, upload_path)
        os.makedirs(full_media_path, exist_ok=True)

        # Log para debug
        logger.info(f"Directorio creado: {full_media_path}")
        logger.info(f"Permisos del directorio: {oct(os.stat(full_media_path).st_mode)[-3:]}")

        # Guardar la imagen con un nombre único y extensión original
        filename = f"{uuid.uuid4()}{os.path.splitext(image.name)[1].lower()}"
        full_path = os.path.join(upload_path, filename)
        absolute_path = os.path.join(settings.MEDIA_ROOT, full_path)

        # Guardar la imagen anterior
        old_image = profile.profile_image
        
        # Guardar físicamente la nueva imagen primero
        with open(absolute_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        # Verificar que el archivo se guardó correctamente
        if not os.path.exists(absolute_path):
            raise Exception("La imagen no se guardó correctamente")

        logger.info(f"Imagen guardada en: {absolute_path}")
        logger.info(f"Permisos del archivo: {oct(os.stat(absolute_path).st_mode)[-3:]}")

        # Actualizar el perfil con la nueva imagen
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
        user = request.user
        profile = user.profile
        
        # Convertir la imagen a URL si existe
        profile_image_url = None
        if profile.profile_image:
            profile_image_url = request.build_absolute_uri(profile.profile_image.url)
        
        # Crear el diccionario de respuesta
        response_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile': {
                'profile_image': profile_image_url,  # Usar la URL en lugar del objeto ImageField
                'phone': profile.phone,
                'birth_date': profile.birth_date,
                'role': profile.role,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'email': profile.email,
                'username': profile.username
            }
        }
        
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error en getProfile: {str(e)}")
        return Response(
            {'error': 'Error al obtener el perfil'},
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
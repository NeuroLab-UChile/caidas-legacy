from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from prevcad.models.user_profile import UserProfile
from prevcad.serializers.user_profile_serializer import UserProfileSerializer, UserSerializer
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request):
    try:
        logger.info("="*50)
        logger.info("Iniciando getProfile")
        logger.info(f"Usuario: {request.user}")
        
        user = request.user
        serializer = UserSerializer(user)
        logger.info("Perfil serializado exitosamente")
        return Response(serializer.data)
            
    except Exception as e:
        logger.error(f"Error en getProfile: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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
        
        # Guardar la imagen anterior
        old_image = profile.profile_image
        
        # Actualizar con la nueva imagen
        profile.profile_image = image
        profile.save()

        # Eliminar la imagen anterior si existe
        if old_image:
            old_image.delete(save=False)

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error en uploadProfileImage: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
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

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error en deleteProfileImage: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



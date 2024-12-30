from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from .serializers.user_profile_serializer import UserProfileSerializer
from decorators import doctor_required
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers.user_profile_serializer import UserProfileSerializer, UserSerializer
from prevcad.models import UserProfile

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request: Request) -> Response:
  user = request.user
  serializer = UserProfileSerializer(user, many=False)
  return Response(serializer.data)

class UserProfileImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            # Asegurar que existe el perfil
            if not hasattr(request.user, 'profile'):
                UserProfile.objects.create(user=request.user)
                request.user.refresh_from_db()

            profile = request.user.profile
            
            if 'profile_image' not in request.FILES:
                return Response(
                    {'error': 'No se proporcionó ninguna imagen'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            profile.profile_image = request.FILES['profile_image']
            profile.save()

            # Devolver la URL de la imagen
            serializer = UserProfileSerializer(
                profile,
                context={'request': request}
            )
            return Response(serializer.data)

        except Exception as e:
            print(f"Error uploading image: {str(e)}")
            return Response(
                {'error': 'Error al subir la imagen'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        try:
            if not hasattr(request.user, 'profile'):
                UserProfile.objects.create(user=request.user)
                request.user.refresh_from_db()

            serializer = UserSerializer(
                request.user,
                context={'request': request}
            )
            return Response(serializer.data)
        except Exception as e:
            print(f"Error getting profile: {str(e)}")
            return Response(
                {'error': 'Error obteniendo el perfil'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        try:
            if not hasattr(request.user, 'profile'):
                UserProfile.objects.create(user=request.user)
                request.user.refresh_from_db()

            serializer = UserProfileSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



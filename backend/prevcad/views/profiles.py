from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from prevcad.serializers.user_serializer import (
  UserSerializer
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request: Request) -> Response:
  user = request.user  # El usuario se obtiene automáticamente del token
  serializer = UserSerializer(user, many=False)
  return Response(serializer.data)

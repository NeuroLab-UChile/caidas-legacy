from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from prevcad.models import (
  HealthCategory,
  TextRecomendation,
  Form,
)
from prevcad.serializers import (
  HealthCategorySerializer, 
  TextRecomendationSerializer, 
  UserSerializer, 
  FormSerializer
)


class HealthCategoryView(viewsets.ModelViewSet):
  queryset = HealthCategory.objects.all()
  serializer_class = HealthCategorySerializer

  def create(self, request: Request, *args, **kwargs) -> Response:
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

  def list(self, request: Request, *args, **kwargs) -> Response:
    queryset = self.get_queryset()
    serializer = self.get_serializer(queryset, many=True)
    return Response(serializer.data)


class TextRecomendationsView(viewsets.ModelViewSet):
  queryset = TextRecomendation.objects.all()
  serializer_class = TextRecomendationSerializer

  def create(self, request: Request, *args, **kwargs) -> Response:
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

  def retrieve(self, request: Request, pk=None, *args, **kwargs) -> Response:
    try:
      instance = self.get_object()
      serializer = self.get_serializer(instance)
      return Response(serializer.data)
    except TextRecomendation.DoesNotExist:
      return Response(status=status.HTTP_404_NOT_FOUND)

  def list(self, request, *args, **kwargs) -> Response:
    queryset = self.get_queryset()
    serializer = self.get_serializer(queryset, many=True)
    return Response(serializer.data)


class FormView(viewsets.ViewSet):
  queryset = Form.objects.all()
  serializer_class = FormSerializer

  def list(self, request: Request) -> Response:
    forms = self.queryset
    serializer = self.serializer_class(forms, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  
class FormByCategoryView(APIView):
  def get(self, request, category_id, *args, **kwargs):
    try:
      category = HealthCategory.objects.get(id=category_id)

      if hasattr(category, 'form'):
        form = category.form
        serializer = FormSerializer(form)
        return Response(serializer.data, status=status.HTTP_200_OK)
      else:
        return Response({'error': 'Formulario no encontrado para esta categoría'}, status=status.HTTP_404_NOT_FOUND)
    except HealthCategory.DoesNotExist:
      return Response({'error': 'Categoría no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request: Request) -> Response:
  user = request.user  # El usuario se obtiene automáticamente del token
  serializer = UserSerializer(user, many=False)
  return Response(serializer.data)
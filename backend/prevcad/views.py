from rest_framework import viewsets, status
from rest_framework.response import Response
from prevcad.models import HealthCategory, TextRecomendation
from prevcad.serializers import HealthCategorySerializer, TextRecomendationSerializer

class HealthCategoryView(viewsets.ViewSet):
  queryset = HealthCategory.objects.all()

  def create(self, request):
    serializer = HealthCategorySerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def list(self, request):
    queryset = HealthCategory.objects.all()
    serializer = HealthCategorySerializer(queryset, many=True)
    return Response(serializer.data)

  # Other methods can remain unchanged if not used

class TextRecomendationsView(viewsets.ViewSet):
  queryset = TextRecomendation.objects.all()

  def create(self, request):
    serializer = TextRecomendationSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def retrieve(self, request, pk=None):
    try:
      text_recomendation = TextRecomendation.objects.get(pk=pk)
    except TextRecomendation.DoesNotExist:
      return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = TextRecomendationSerializer(text_recomendation)
    return Response(serializer.data)

  def list(self, request):
    queryset = TextRecomendation.objects.all()
    serializer = TextRecomendationSerializer(queryset, many=True)
    return Response(serializer.data)

  # Other methods can remain unchanged if not used

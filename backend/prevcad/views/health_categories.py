from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from prevcad.models import (
  HealthCategory,
)
from prevcad.serializers.health_category_serializer import (
  HealthCategorySerializer,
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

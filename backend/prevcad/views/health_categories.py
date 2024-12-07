from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import HealthCategory
from ..serializers.health_category_serializer import HealthCategorySerializer
import base64
from django.utils.encoding import smart_str

class HealthCategoryListView(APIView):
  def get(self, request):
    try:
      categories = HealthCategory.objects.filter(user=request.user)
      serialized_categories = HealthCategorySerializer(categories, many=True)
      return Response(
        serialized_categories.data,
        status=status.HTTP_200_OK
      )
    except Exception as e:
      return Response(
        {'error': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

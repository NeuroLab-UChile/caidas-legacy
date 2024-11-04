from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import PhysicalActivity
import base64
from django.utils.encoding import smart_str

class HealthCategoryListView(APIView):
  def get(self, request):
    try:
      activities = PhysicalActivity.objects.all()
      serialized_data = []

      for activity in activities:
        image_data = None
        if activity.image and hasattr(activity.image, 'path'):
          with open(activity.image.path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        serialized_data.append({
          'id': activity.id,
          'name': smart_str(activity.name),
          'image': image_data
        })

      return Response(serialized_data, status=status.HTTP_200_OK)
    except Exception as e:
      return Response(
        {'error': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from prevcad.models import PhysicalActivity
from prevcad.serializers.physical_activity_serializer import PhysicalActivitySerializer


class PhysicalActivityView(APIView):
  def get(self, request: Request) -> Response:

    try:
      physical_activity = PhysicalActivity.objects.get(user=request.user)
      serializer = PhysicalActivitySerializer(physical_activity, many=False)
      return Response(serializer.data)
    except PhysicalActivity.DoesNotExist:
      return Response(
        {"error": "Physical activity not found"},
        status=status.HTTP_404_NOT_FOUND
      )

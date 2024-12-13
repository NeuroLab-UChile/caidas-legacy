from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import HealthCategory
from ..serializers import HealthCategorySerializer

class HealthCategoryListView(APIView):
    def get(self, request):
        try:
            # Get user categories
            categories = HealthCategory.objects.filter(user=request.user)

            # Serialize categories with their evaluation forms
            serialized_categories = HealthCategorySerializer(categories, many=True).data

            return Response(
               serialized_categories,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(f"Error in HealthCategoryListView: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

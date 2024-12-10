from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import HealthCategory, ActivityNodeDescription, ActivityNodeQuestion
from ..serializers import ActivityNodeSerializer, HealthCategorySerializer

class HealthCategoryListView(APIView):
    print("HealthCategoryListView")
    def get(self, request):
        try:
            # Obtener categorías del usuario
            categories = HealthCategory.objects.filter(user=request.user)
            serialized_categories = HealthCategorySerializer(categories, many=True).data
            print(serialized_categories)

            # Obtener todos los nodos de actividad relacionados
            nodes = []
            for category in categories:
                if category.root_node:
                    nodes.append(category.root_node)

            # Serializar todos los nodos de actividad
            serialized_nodes = ActivityNodeSerializer(nodes, many=True).data

            response = {"categories": serialized_categories, "nodes": serialized_nodes}
            print(response)

            return Response(
                {"categories": serialized_categories, "nodes": serialized_nodes},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

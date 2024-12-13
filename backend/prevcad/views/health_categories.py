from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import HealthCategory, CategoryTemplate
from ..serializers import HealthCategorySerializer
from rest_framework.decorators import api_view
from django.utils import timezone

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

@api_view(['POST'])
def save_evaluation_responses(request, category_id):
    try:
        category = HealthCategory.objects.get(id=category_id, user=request.user)
        responses = request.data.get('responses', {})
        
        # Guardar respuestas
        category.responses = responses
        
        # Calcular score (ejemplo simple)
        total_questions = len(category.evaluation_form.get("question_nodes", []))
        answered_questions = len(responses.keys())
        score = int((answered_questions / total_questions) * 100) if total_questions > 0 else 0
        
        # Actualizar categoría
        category.score = score
        category.completion_date = timezone.now()
        category.save()
        
        return Response({
            'status': 'success',
            'score': score,
            'recommendations': category.evaluation_form.get("question_nodes", [])[-1].get("recommendations", [])
        })
    except HealthCategory.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def update_category_template(request, template_id):
    try:
        template = CategoryTemplate.objects.get(id=template_id)
        template.name = request.data.get('name', template.name)
        template.description = request.data.get('description', template.description)
        template.evaluation_form = request.data.get('evaluation_form', template.evaluation_form)
        template.save()
        return Response({'status': 'success'})
    except CategoryTemplate.DoesNotExist:
        return Response({'error': 'Template not found'}, status=404)

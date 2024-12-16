from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import HealthCategory, CategoryTemplate
from ..serializers import HealthCategorySerializer
from rest_framework.decorators import api_view
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from datetime import datetime
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class HealthCategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            print("\n=== Debug HealthCategoryListView ===")
            print(f"Usuario autenticado: {request.user}")
            
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Usuario no autenticado"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Get user categories
            categories = HealthCategory.objects.filter(user=request.user)
            print(f"Categorías encontradas: {categories.count()}")
            
            # Debug cada categoría
            for category in categories:
                print(f"\nCategoría ID: {category.id}")
                print(f"Template: {category.template.name if category.template else 'No template'}")
                print(f"Evaluation Form: {category.template.evaluation_form if category.template else None}")
                print(f"Responses: {category.responses}")

            # Filtrar categorías sin template
            categories = categories.filter(template__isnull=False)
            
            serialized_categories = HealthCategorySerializer(categories, many=True).data
            return Response(serialized_categories, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"❌ Error in HealthCategoryListView: {e}")
            import traceback
            print(traceback.format_exc())
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
        category.completion_date = timezone.now()
        category.save()
        
        return Response({
            'status': 'success',
            'message': 'Respuestas guardadas correctamente'
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

@require_POST
@csrf_exempt
def submit_responses(request, category_id):
    try:
        category = get_object_or_404(HealthCategory, id=category_id)
        
        # Obtener las respuestas del request
        data = json.loads(request.body)
        responses = data.get('responses')
        
        if not responses:
            return JsonResponse({
                'status': 'error',
                'message': 'No se recibieron respuestas'
            }, status=400)

        # Validar las respuestas contra el formulario de evaluación
        if not category.template or not category.template.evaluation_form:
            return JsonResponse({
                'status': 'error',
                'message': 'No existe un formulario de evaluación para esta categoría'
            }, status=400)

        # Actualizar el modelo con las respuestas
        category.responses = responses
        category.completion_date = datetime.now()
        category.save(update_fields=['responses', 'completion_date'])

        return JsonResponse({
            'status': 'success',
            'message': 'Respuestas guardadas correctamente'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Formato de datos inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def calculate_score(responses):
    """
    Calcula el score basado en las respuestas.
    Implementa tu lógica de puntuación aquí.
    """
    # Ejemplo básico
    score = 0
    # ... implementa tu lógica de puntuación
    return score

@api_view(['POST'])
def create_health_category(request):
    try:
        print("Recibiendo request para crear health category:", request.data)  # Debug
        
        # Obtener datos del request
        template_id = request.data.get('template_id')
        # Usar el usuario autenticado en lugar de recibir user_id
        user = request.user
        
        if not template_id:
            return Response({
                'status': 'error',
                'message': 'template_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Validar que existe el template
        try:
            template = CategoryTemplate.objects.get(id=template_id)
        except CategoryTemplate.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f'Template con id {template_id} no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
            
        # Verificar si ya existe una categoría para este usuario y template
        existing_category = HealthCategory.objects.filter(
            user=user,
            template=template
        ).first()
        
        if existing_category:
            serializer = HealthCategorySerializer(existing_category)
            return Response({
                'status': 'success',
                'message': 'Ya existe una evaluación para este usuario y template',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        # Crear nueva categoría
        health_category = HealthCategory.objects.create(
            user=user,
            template=template,
            evaluation_form=template.evaluation_form
        )
        
        # Serializar y retornar la respuesta
        serializer = HealthCategorySerializer(health_category)
        
        print("Health category creada exitosamente:", health_category.id)  # Debug
        
        return Response({
            'status': 'success',
            'message': 'Categoría creada exitosamente',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"Error al crear health category: {str(e)}")  # Debug
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

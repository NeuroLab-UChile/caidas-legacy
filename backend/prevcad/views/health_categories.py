from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import HealthCategory, CategoryTemplate, ActivityNode
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
            
            # Obtener solo las categorías del usuario actual
            categories = HealthCategory.objects.filter(
                user=request.user,
                template__is_active=True  # Solo templates activos
            ).select_related('template')  # Optimizar consultas

            for category in categories:
                print(f"\nCategoría: {category.id}")
                print(f"Template: {category.template}")
                print(f"Evaluation Form: {category.template.evaluation_form if category.template else None}")
            
            serialized = HealthCategorySerializer(categories, many=True).data
            print(f"\nDatos serializados: {serialized}")
            
            return Response(serialized)
        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def save_evaluation_responses(request, category_id):
    print("\n=== Debug save_evaluation_responses ===")
    print(f"Request data: {request.data}")
    try:
        category = HealthCategory.objects.get(id=category_id, user=request.user)
        responses = request.data.get('responses', {})

        print(f"Received responses: {responses}")
        
        # Actualizar estado y respuestas
        category.responses = responses
        category.completion_date = timezone.now()
        category.status = 'completed'
        category.save(update_fields=['responses', 'completion_date'])
        
        # Recargar la categoría
        category.refresh_from_db()
        
        return Response({
            'status': 'success',
            'message': 'Respuestas guardadas correctamente',
            'data': HealthCategorySerializer(category).data
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
        
        # Log de inicio
        print(f"\n=== Processing submission for category {category_id} ===")
        
        # Validar y parsear el JSON
        try:
            data = json.loads(request.body)
            responses = data.get('responses', {})
            print(f"Received responses: {responses}")
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Formato JSON inválido'
            }, status=400)

        # Validaciones básicas
        if not responses:
            return JsonResponse({
                'status': 'error',
                'message': 'No se recibieron respuestas'
            }, status=400)

        if not category.template or not category.template.evaluation_form:
            return JsonResponse({
                'status': 'error',
                'message': 'No existe un formulario de evaluación para esta categoría'
            }, status=400)

        # Validar formato de respuestas
        validated_responses = {}
        for node_id, response in responses.items():
            try:
                node = ActivityNode.objects.get(id=node_id)
                print(f"\nValidating node {node_id} of type {node.type}")
                print(f"Response: {response}")

                # Validar según el tipo de nodo
                if node.type == 'SINGLE_CHOICE_QUESTION':
                    if not isinstance(response.get('selectedOption'), int):
                        print(f"Warning: Invalid single choice response for node {node_id}")
                        continue
                    validated_responses[node_id] = {'selectedOption': response['selectedOption']}
                
                elif node.type == 'MULTIPLE_CHOICE_QUESTION':
                    if not isinstance(response.get('selectedOptions'), list):
                        print(f"Warning: Invalid multiple choice response for node {node_id}")
                        continue
                    validated_responses[node_id] = {'selectedOptions': response['selectedOptions']}
                
                elif node.type == 'TEXT_QUESTION':
                    if not isinstance(response.get('answer'), str):
                        print(f"Warning: Invalid text response for node {node_id}")
                        continue
                    validated_responses[node_id] = {'answer': response['answer']}

            except ActivityNode.DoesNotExist:
                print(f"Warning: Node {node_id} does not exist")
                continue

        # Guardar solo si hay respuestas válidas
        if validated_responses:
            print(f"\nSaving validated responses: {validated_responses}")
            category.responses = validated_responses
            category.completion_date = datetime.now()
            category.save(update_fields=['responses', 'completion_date'])

            return JsonResponse({
                'status': 'success',
                'message': 'Respuestas guardadas correctamente',
                'validated_responses': validated_responses
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'No se encontraron respuestas válidas'
            }, status=400)

    except Exception as e:
        print(f"Error processing submission: {str(e)}")
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

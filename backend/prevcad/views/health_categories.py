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
        
        validated_responses = {}
        
        for node_id, response_data in responses.items():
            print(f"\nProcessing node_id: {node_id}")
            print(f"Response data: {response_data}")
            
            if not isinstance(response_data, dict):
                print(f"Skipping invalid response format for node {node_id}")
                continue
            
            response_type = response_data.get('type')
            validated_response = {
                'id': response_data.get('id'),
                'type': response_type,
                'question': response_data.get('question')
            }
            
            # Validar respuesta según el tipo
            is_valid = False
            answer = response_data.get('answer', {})
            
            if response_type == 'SINGLE_CHOICE_QUESTION':
                if isinstance(answer, dict):
                    selected_option = answer.get('selectedOption')
                    options = answer.get('options', [])
                    if selected_option is not None and options and selected_option < len(options):
                        validated_response['answer'] = {
                            'selectedOption': selected_option,
                            'options': options
                        }
                        is_valid = True
            
            elif response_type == 'MULTIPLE_CHOICE_QUESTION':
                if isinstance(answer, dict):
                    selected_options = answer.get('selectedOptions', [])
                    options = answer.get('options', [])
                    if isinstance(selected_options, list) and options:
                        if all(isinstance(i, int) and i < len(options) for i in selected_options):
                            validated_response['answer'] = {
                                'selectedOptions': selected_options,
                                'options': options
                            }
                            is_valid = True
            
            elif response_type == 'SCALE_QUESTION':
                if isinstance(answer, dict) and 'value' in answer:
                    try:
                        value = int(answer['value'])
                        if 1 <= value <= 10:
                            validated_response['answer'] = {'value': value}
                            is_valid = True
                    except (ValueError, TypeError):
                        print(f"Invalid scale value for node {node_id}")
            
            elif response_type == 'TEXT_QUESTION':
                if isinstance(answer, dict) and isinstance(answer.get('value'), str):
                    validated_response['answer'] = {'value': answer['value']}
                    is_valid = True
            
            if is_valid:
                if 'metadata' in response_data:
                    validated_response['metadata'] = response_data['metadata']
                validated_responses[str(node_id)] = validated_response
            else:
                print(f"Response validation failed for node {node_id}")
        
        if validated_responses:
            category.responses = validated_responses
            category.completion_date = timezone.now()
            category.status = 'completed'
            category.save()
            
            print(f"Saved responses: {validated_responses}")
            
            return Response({
                'status': 'success',
                'message': 'Respuestas guardadas correctamente',
                'data': HealthCategorySerializer(category).data
            })
        else:
            return Response({
                'status': 'error',
                'message': 'No se encontraron respuestas válidas'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except HealthCategory.DoesNotExist:
        return Response({
            'error': 'Category not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error processing submission: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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


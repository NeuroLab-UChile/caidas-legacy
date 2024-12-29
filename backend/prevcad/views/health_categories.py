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
        validated_responses = {}
        
        for node_id, response_data in responses.items():
            print(f"\nProcessing node_id: {node_id}")
            response_type = response_data.get('type')
            
            if response_type == 'IMAGE_QUESTION':
                # Obtener el array de imágenes del formato correcto
                answer_data = response_data.get('answer', {})
                images = answer_data.get('images', []) if isinstance(answer_data, dict) else []
                processed_images = []
                
                if isinstance(images, list):
                    for image_data in images:
                        if image_data and image_data.startswith('file://'):
                            try:
                                # Extraer el nombre del archivo
                                file_name = image_data.split('/')[-1]
                                # Crear una URL pública para la imagen
                                public_url = f"/media/evaluation_images/{category_id}/{file_name}"
                                
                                # Guardar la imagen en el servidor
                                import base64
                                from django.core.files.base import ContentFile
                                from django.conf import settings
                                import os
                                
                                # Crear el directorio si no existe
                                save_path = os.path.join(settings.MEDIA_ROOT, 'evaluation_images', str(category_id))
                                os.makedirs(save_path, exist_ok=True)
                                
                                # Guardar la imagen
                                with open(image_data.replace('file://', ''), 'rb') as image_file:
                                    image_content = image_file.read()
                                    file_path = os.path.join(save_path, file_name)
                                    with open(file_path, 'wb') as f:
                                        f.write(image_content)
                                
                                processed_images.append(public_url)
                            except Exception as e:
                                print(f"Error processing image: {e}")
                                processed_images.append("Error processing image")
                
                # Mantener el formato de respuesta consistente
                response_data['answer'] = {
                    'images': processed_images
                }
            
            validated_responses[str(node_id)] = response_data
        
        # Guardar las respuestas actualizadas
        category.responses = validated_responses
        category.completion_date = timezone.now()
        category.status = 'completed'
        
        # Limpiar las recomendaciones del doctor cuando se envían nuevas respuestas
        category.doctor_recommendations = None
        category.doctor_recommendations_updated_at = None
        category.doctor_recommendations_updated_by = None
        category.status_color = None
        
        category.save()
        
        return Response({
            'status': 'success',
            'message': 'Respuestas guardadas correctamente',
            'data': HealthCategorySerializer(category).data
        })
        
    except Exception as e:
        print(f"Error saving responses: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_health_category(request, category_id):
    try:
        category = HealthCategory.objects.get(id=category_id, user=request.user)
        
        # Actualizar los campos específicos
        if 'doctor_recommendations' in request.data:
            category.doctor_recommendations = request.data['doctor_recommendations']
            category.doctor_recommendations_updated_at = None
            category.doctor_recommendations_updated_by = None
        
        if 'status_color' in request.data:
            category.status_color = request.data['status_color']
        
        category.save()
        
        return Response({
            'status': 'success',
            'message': 'Categoría actualizada correctamente',
            'data': HealthCategorySerializer(category).data
        })
        
    except HealthCategory.DoesNotExist:
        return Response({
            'error': 'Category not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
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


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import HealthCategory, CategoryTemplate, ActivityNode, UserProfile
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
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from prevcad.models import UserProfile

class HealthCategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        print("=== Debug HealthCategoryListView ===")
        print(f"Usuario autenticado: {request.user.username}")
        
        categories = HealthCategory.objects.filter(user__user=request.user)
        serialized_categories = []
        
        for category in categories:
            template = category.template
            if template:
                category_data = {
                    'id': category.id,
                    'name': template.name,
                    'description': template.description,
                    'icon': template.get_icon_base64(),
                    'evaluation_type': template.evaluation_type,
                    'evaluation_form': template.evaluation_form,
                    'professional_evaluation_results': category.professional_evaluation_results,
                    'training_form': template.training_form,

                    # ... otros campos ...
                }
                serialized_categories.append(category_data)
        
        return Response(serialized_categories)

@api_view(['POST'])
def save_evaluation_responses(request, category_id):
    print("\n=== Debug save_evaluation_responses ===")
    print(f"Request data: {request.data}")
    
    try:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        category = get_object_or_404(
            HealthCategory, 
            id=category_id, 
            user=user_profile
        )
        
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
        
        # Actualizar la categoría con la información del usuario
        category.responses = validated_responses
        category.completion_date = timezone.now()
        category.status = 'completed'
        
        # Limpiar las recomendaciones previas
        category.professional_recommendations = None
        category.professional_recommendations_updated_at = None
        category.professional_recommendations_updated_by = None
        category.status_color = None  
        
        category.save()
        
        # Serializar con información detallada
        serializer = HealthCategorySerializer(category)
        
        return Response({
            'status': 'success',
            'message': 'Respuestas guardadas correctamente',
            'data': serializer.data
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
        user_profile = get_object_or_404(UserProfile, user=request.user)
        category = get_object_or_404(
            HealthCategory, 
            id=category_id, 
            user=user_profile
        )
        
        # Actualizar los campos específicos
        if 'professional_recommendations' in request.data:
            category.professional_recommendations = request.data['professional_recommendations']
            category.professional_recommendations_updated_at = None
            category.professional_recommendations_updated_by = None
        
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




@api_view(['POST'])
def create_health_category(request):
    try:
        print("Recibiendo request para crear health category:", request.data)
        
        template_id = request.data.get('template_id')
        if not template_id:
            return Response({
                'status': 'error',
                'message': 'template_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener o crear el perfil del usuario
        user_profile = get_object_or_404(UserProfile, user=request.user)
        template = get_object_or_404(CategoryTemplate, id=template_id)
            
        # Verificar si ya existe una categoría
        existing_category = HealthCategory.objects.filter(
            user=user_profile,
            template=template
        ).first()
        
        if existing_category:
            serializer = HealthCategorySerializer(existing_category)
            return Response({
                'status': 'success',
                'message': 'Ya existe una evaluación para este usuario y template',
                'data': serializer.data
            })
            
        # Crear nueva categoría con el perfil del usuario
        health_category = HealthCategory.objects.create(
            user=user_profile,
            template=template,
            evaluation_form=template.evaluation_form
        )
        
        serializer = HealthCategorySerializer(health_category)
        return Response({
            'status': 'success',
            'message': 'Categoría creada exitosamente',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"Error al crear health category: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_health_category_detail(request, category_id):
    try:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        category = get_object_or_404(
            HealthCategory, 
            id=category_id, 
            user=user_profile
        )
        
        serializer = HealthCategorySerializer(category)
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


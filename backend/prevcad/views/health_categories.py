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

from django.core.files.storage import default_storage
from django.conf import settings
import os

from prevcad.utils import build_media_url

from prevcad.models import UserProfile

class HealthCategoryListView(APIView):

    
    def get(self, request):
        print("=== Debug HealthCategoryListView ===")
        print(f"Usuario autenticado: {request.user.username}")
        
        user_profile = get_object_or_404(UserProfile, user=request.user)
        categories = HealthCategory.objects.filter(user__user=request.user)
        
        serialized_categories = []
        
        for category in categories:
            template = category.template
            if template:
                # Usar el serializer en lugar de construir el diccionario manualmente
                serializer = HealthCategorySerializer(category)
                print(f"serializer.data: {serializer.data}")
           

                serialized_categories.append(serializer.data)
        
        return Response(serialized_categories)

@api_view(['POST'])
def save_evaluation_responses(request, category_id):
    try:
        # Verificar autenticación
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Usuario no autenticado'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        # Obtener el perfil y la categoría
        user_profile = get_object_or_404(UserProfile, user=request.user)
        health_category = get_object_or_404(
            HealthCategory, 
            id=category_id,
            user=user_profile
        )
        
        # Obtener y parsear las respuestas
        responses = request.data.get('responses', {})
        if isinstance(responses, str):
            responses = json.loads(responses)
            
        # Procesar imágenes y actualizar respuestas
        for node_id, response in responses.items():
            if isinstance(response, dict) and response.get('type') == 'IMAGE_QUESTION':
                # Obtener todas las imágenes para este nodo específico
                image_files = sorted([
                    (k, f) for k, f in request.FILES.items()
                    if k.startswith(f'image_{node_id}')
                ], key=lambda x: x[0])
                
                if image_files:
                    processed_images = []
                    for key, image_file in image_files:
                        try:
                            print(f"\nProcesando archivo: {image_file.name}")
                            print(f"Tipo de contenido: {image_file.content_type}")
                            print(f"Tamaño: {image_file.size} bytes")
                            
                            # Validar que es una imagen
                            if not image_file.content_type.startswith('image/'):
                                print(f"Archivo no válido: {image_file.name}")
                                continue
                            
                            # Crear nombre único para la imagen
                            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S_%f')
                            extension = os.path.splitext(image_file.name)[1].lower() or '.jpg'
                            filename = f'question_{node_id}_{timestamp}{extension}'
                            
                            # Definir la ruta relativa
                            relative_path = os.path.join(
                                'evaluation_images',
                                f'category_{category_id}',
                                filename
                            )
                            
                            print(f"Ruta relativa: {relative_path}")
                            
                            # Asegurar que el directorio existe
                            full_path = os.path.join(settings.MEDIA_ROOT, 'evaluation_images', f'category_{category_id}')
                            os.makedirs(full_path, exist_ok=True)
                            
                            # Guardar la imagen
                            saved_path = default_storage.save(relative_path, image_file)
                            print(f"Archivo guardado en: {saved_path}")
                            
                            # Construir la URL
                            image_url = build_media_url(saved_path, request, is_backend=False)
                            print(f"URL generada: {image_url}")
                            
                            processed_images.append({
                                'url': image_url,
                                'filename': filename,
                                'timestamp': timezone.now().isoformat()
                            })
                            
                        except Exception as e:
                            print(f"Error procesando imagen: {str(e)}")
                            continue
                    
                    if processed_images:
                        # Actualizar la respuesta con todas las imágenes procesadas
                        responses[node_id] = {
                            'type': 'IMAGE_QUESTION',
                            'answer': {
                                'images': processed_images
                            }
                        }
                    else:
                        print(f"No se procesaron imágenes para node {node_id}")
                else:
                    print(f"No se encontraron archivos de imagen para node {node_id}")
        
        # Guardar las respuestas en el formulario de evaluación
        evaluation_form = health_category.get_or_create_evaluation_form()
        if evaluation_form.responses is None:
            evaluation_form.responses = {}
            
        evaluation_form.completed_date = timezone.now()
        evaluation_form.responses.update(responses)
        evaluation_form.save()
        
        return Response({
            'status': 'success',
            'message': 'Respuestas guardadas correctamente'
        })
        
    except Exception as e:
        print(f"Error guardando respuestas: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_health_category(request, category_id):
    try:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        category = get_object_or_404(HealthCategory, id=category_id)
        
        # Verificar permisos de edición
        if not category.can_user_edit(user_profile):
            return Response({
                'status': 'error',
                'message': 'No tienes permisos para editar esta categoría'
            }, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['user_profile'] = user_profile  # Agregar el perfil de usuario
        data['updated_by'] = request.user.get_full_name()
        
        try:
            category.update(data)
            return Response({
                'status': 'success',
                'message': 'Categoría actualizada correctamente',
                'data': HealthCategorySerializer(category).data
            })
        except ValidationError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
            
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

@api_view(['POST'])
def save_professional_evaluation(request, category_id):
    """
    Vista de admin para guardar la evaluación profesional
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        # Obtener la categoría de salud
        health_category = HealthCategory.objects.get(id=category_id)
        
        # Obtener los datos del request
        data = json.loads(request.body)
        evaluation_form = health_category.get_or_create_evaluation_form()
        
        # Debug
        print("Estado inicial:", {
            'is_draft': evaluation_form.is_draft,
            'completed_date': evaluation_form.completed_date
        })
        
        # Obtener y actualizar las respuestas profesionales
        professional_responses = data.get('professional_responses', {})
        if evaluation_form.professional_responses is None:
            evaluation_form.professional_responses = {}
        evaluation_form.professional_responses.update(professional_responses)
        
        # Manejar el estado de completado
        if data.get('complete', False):
            print("Marcando como completado...")  # Debug
            now = timezone.now()
            
            # Actualizar el formulario
            evaluation_form.is_draft = False
            evaluation_form.completed_date = now
            
            # Actualizar la recomendación
            try:
                recommendation = health_category.get_or_create_recommendation()
                if recommendation:
                    recommendation.is_draft = False
                    recommendation.updated_by = request.user.username
                    recommendation.updated_at = now
                    recommendation.save()
                    print("Recomendación actualizada")  # Debug
            except Exception as e:
                print(f"Error actualizando recomendación: {e}")
        
        # Guardar y verificar
        evaluation_form.save()
        evaluation_form.refresh_from_db()
        
        # Debug final
        print("Estado final:", {
            'is_draft': evaluation_form.is_draft,
            'completed_date': evaluation_form.completed_date,
            'professional_responses': evaluation_form.professional_responses
        })

        return JsonResponse({
            'success': True,
            'message': 'Evaluación guardada correctamente',
            'is_draft': evaluation_form.is_draft,
            'completed_date': evaluation_form.completed_date.isoformat() if evaluation_form.completed_date else None,
            'professional_responses': evaluation_form.professional_responses
        })

    except HealthCategory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Categoría de salud no encontrada'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        import traceback
        print("Error completo:")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 
    


@api_view(['POST'])
def update_recommendation(request, category_id):
    """
    Vista de admin para actualizar la recomendación
    """

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try: 
        print("=== Debug update_recommendation ===")
        print('request.POST:', request.POST)

        # Recuperar la categoría de salud y su recomendación
        health_category = get_object_or_404(HealthCategory, id=category_id)
        recommendation = health_category.recommendation

        # Manejar el video si está presente en request.POST
        video_file = request.FILES.get('video')
        if video_file:
            recommendation.video = video_file
            recommendation.save()
            print(f"Video guardado: {recommendation.video.url}")

       
        # Actualizar otros campos de la recomendación
        recommendation.use_default = request.POST.get('use_default') == 'true'

  

 
        recommendation.text = request.POST.get('text', '')
        recommendation.status_color = request.POST.get('status_color', 'gris')
        recommendation.is_draft = request.POST.get('is_draft') == 'true'
        recommendation.updated_by = request.user.username
        recommendation.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Recomendación actualizada correctamente',
            'video_url': recommendation.video.url if recommendation.video else None
        })

    except Exception as e:
        import traceback
        print("Error completo:")
        print(traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

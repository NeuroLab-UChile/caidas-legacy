import json
import uuid
import os
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.conf import settings
from prevcad.models import CategoryTemplate
import logging
import time
from prevcad.decorators import doctor_required
from django.contrib.auth.decorators import user_passes_test


from django.utils import timezone

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.urls import path
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from ..models import VideoNode
from rest_framework import serializers
from rest_framework.reverse import reverse
from prevcad.utils import build_media_url




logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def update_evaluation_form(request, template_id):
    """
    Actualiza el formulario de evaluación de una plantilla de categoría.
    """
    try:
        obj = get_object_or_404(CategoryTemplate, id=template_id)
        new_form_data = request.POST.get('evaluation_form')
        
        if not new_form_data:
            return JsonResponse({
                'status': 'error', 
                'message': 'No se recibieron datos del formulario',
                'details': None
            }, status=400, json_dumps_params={'indent': 2, 'ensure_ascii': False})
        
        new_form = json.loads(new_form_data)
        if "question_nodes" not in new_form or not isinstance(new_form["question_nodes"], list):
            return JsonResponse({
                'status': 'error', 
                'message': 'Estructura de datos inválida',
                'details': {
                    'required_fields': ['question_nodes'],
                    'received_fields': list(new_form.keys())
                }
            }, status=400, json_dumps_params={'indent': 2, 'ensure_ascii': False})

        # Obtener nodos actuales
        current_form = obj.evaluation_form or {'question_nodes': []}
        current_nodes = {node['id']: node for node in current_form.get('question_nodes', [])}
        
        # Procesar cada nodo nuevo/actualizado
        updated_nodes = []
        for node in new_form['question_nodes']:
            node_id = node.get('id')
            if node_id in current_nodes:
                # Actualizar nodo existente manteniendo datos previos
                current_node = current_nodes[node_id].copy()
                current_node.update(node)
                updated_nodes.append(current_node)
                logger.debug(f"Actualizando nodo existente: {node_id}")
            else:
                # Agregar nuevo nodo
                updated_nodes.append(node)
                logger.debug(f"Agregando nuevo nodo: {node_id}")

        # Actualizar el formulario con los nodos procesados
        new_form['question_nodes'] = updated_nodes
        obj.evaluation_form = new_form
        obj.save(update_fields=["evaluation_form"])
        
        return JsonResponse({
            'status': 'success',
            'message': 'Formulario de evaluación actualizado correctamente',
            'data': {
                'template_id': template_id,
                'updated_at': obj.updated_at.isoformat() if hasattr(obj, 'updated_at') else None,
                'nodes_count': len(updated_nodes)
            }
        }, json_dumps_params={'indent': 2, 'ensure_ascii': False})

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al decodificar JSON',
            'details': {
                'received_data': new_form_data[:100] + '...' if new_form_data else None
            }
        }, status=400, json_dumps_params={'indent': 2, 'ensure_ascii': False})

    except Exception as e:
        logger.error(f"Error updating evaluation form: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'Error interno del servidor',
            'details': {
                'error_type': type(e).__name__,
                'error_message': str(e)
            }
        }, status=500, json_dumps_params={'indent': 2, 'ensure_ascii': False})

@require_POST
@csrf_exempt
@user_passes_test(lambda u: u.is_staff)
def update_training_form(request, template_id):
    """
    Actualiza el formulario de entrenamiento de una plantilla de categoría.
    """
    try:
        obj = get_object_or_404(CategoryTemplate, id=template_id)
        
        # Manejar archivo de media si existe
        media_file = None
        if 'video' in request.FILES:
            media_file = request.FILES['video']
            file_type = 'VIDEO'
        elif 'media_file' in request.FILES:
            media_file = request.FILES['media_file']
            file_type = 'IMAGE'
            
        if media_file:
            # Crear directorio si no existe
            print("-----> media_file", media_file)
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Guardar archivo
            file_path = os.path.join('videos' if file_type == 'VIDEO' else 'images', media_file.name)
            saved_path = handle_uploaded_file(media_file, request)
            
            # Obtener y actualizar el nodo actual
            training_form_data = json.loads(request.POST.get('training_form', '{}'))
            nodes = training_form_data.get('training_nodes', [])
            print("-----> nodes", nodes)
            
            for node in nodes:
                if node.get('media_pending'):
                    node['media_url'] = saved_path
                    node['media_pending'] = False
                    break
            
            # Actualizar el formulario
            obj.training_form = {'training_nodes': nodes}
            obj.save(update_fields=['training_form'])

            print("-----> nodes", nodes)
            return JsonResponse({
                'status': 'success',
                'message': 'Formulario de entrenamiento actualizado correctamente',
                'data': {
                    'nodes': nodes,
                    'template_id': template_id,
                    'nodes_count': len(nodes)
                }
            }, json_dumps_params={'indent': 2, 'ensure_ascii': False})
            
        # Si no hay archivo, procesar el resto del formulario normalmente
        new_form_data = request.POST.get('training_form')
        if not new_form_data:
            return JsonResponse({
                'status': 'error',
                'message': 'No se recibieron datos del formulario'
            }, status=400)

        # Procesar el formulario como antes...
        
    except Exception as e:
        logger.error(f"Error updating training form: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def handle_uploaded_file(file, request):
    """
    Maneja la subida de archivos y retorna la URL relativa.
    """
    import os
    import uuid
    from django.conf import settings

    # Crear directorio si no existe
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generar nombre único para el archivo
    file_name = f"{uuid.uuid4()}_{file.name}"
    file_path = build_media_url(file_name, request, is_backend=True)
    
    # Guardar el archivo
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    # Retornar la ruta relativa con el formato correcto
    return build_media_url(file_name, request, is_backend=False)





# def update_recommendation(request, object_id):
#     try:
#         # Debug de los datos recibidos
#         print("Files:", request.FILES)
#         print("POST data:", request.POST)
        
#         health_category = get_object_or_404(HealthCategory, id=object_id)
#         recommendation = health_category.recommendation

#         # Manejar el video si está presente
#         if 'video' in request.FILES:
#             try:
#                 video_file = request.FILES['video']
#                 print(f"Procesando video: {video_file.name} ({video_file.size} bytes)")
                
#                 # Validar el archivo
#                 if video_file.size > 100 * 1024 * 1024:  # 100MB limit
#                     return JsonResponse({
#                         'status': 'error',
#                         'message': 'El archivo es demasiado grande'
#                     }, status=400)

#                 # Guardar el video
#                 recommendation.video = video_file
#                 recommendation.save()
#                 print(f"Video guardado: {recommendation.video.url}")

#             except Exception as e:
#                 print(f"Error procesando video: {str(e)}")
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': f'Error al procesar el video: {str(e)}'
#                 }, status=500)

#         # Actualizar otros campos
#         recommendation.use_default = request.POST.get('use_default') == 'true'
#         recommendation.text = request.POST.get('text', '')
#         recommendation.status_color = request.POST.get('status_color', 'gris')
#         recommendation.is_draft = request.POST.get('is_draft') == 'true'
#         recommendation.updated_by = request.user.username
#         recommendation.save()

#         return JsonResponse({
#             'status': 'success',
#             'message': 'Recomendación actualizada correctamente',
#             'video_url': recommendation.video.url if recommendation.video else None
#         })

#     except Exception as e:
#         import traceback
#         print("Error completo:")
#         print(traceback.format_exc())
#         return JsonResponse({
#             'status': 'error',
#             'message': str(e)
#         }, status=500)



# def save_professional_evaluation(request, category_id):
#     """
#     Vista de admin para guardar la evaluación profesional
#     """
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Método no permitido'}, status=405)

#     try:
#         # Obtener la categoría de salud
#         health_category = HealthCategory.objects.get(id=category_id)
        
#         # Obtener los datos del request
#         data = json.loads(request.body)
#         evaluation_form = health_category.get_or_create_evaluation_form()
        
#         # Debug
#         print("Estado inicial:", {
#             'is_draft': evaluation_form.is_draft,
#             'completed_date': evaluation_form.completed_date
#         })
        
#         # Obtener y actualizar las respuestas profesionales
#         professional_responses = data.get('professional_responses', {})
#         if evaluation_form.professional_responses is None:
#             evaluation_form.professional_responses = {}
#         evaluation_form.professional_responses.update(professional_responses)
        
#         # Manejar el estado de completado
#         if data.get('complete', False):
#             print("Marcando como completado...")  # Debug
#             now = timezone.now()
            
#             # Actualizar el formulario
#             evaluation_form.is_draft = False
#             evaluation_form.completed_date = now
            
#             # Actualizar la recomendación
#             try:
#                 recommendation = health_category.get_or_create_recommendation()
#                 if recommendation:
#                     recommendation.is_draft = False
#                     recommendation.updated_by = request.user.username
#                     recommendation.updated_at = now
#                     recommendation.save()
#                     print("Recomendación actualizada")  # Debug
#             except Exception as e:
#                 print(f"Error actualizando recomendación: {e}")
        
#         # Guardar y verificar
#         evaluation_form.save()
#         evaluation_form.refresh_from_db()
        
#         # Debug final
#         print("Estado final:", {
#             'is_draft': evaluation_form.is_draft,
#             'completed_date': evaluation_form.completed_date,
#             'professional_responses': evaluation_form.professional_responses
#         })

#         return JsonResponse({
#             'success': True,
#             'message': 'Evaluación guardada correctamente',
#             'is_draft': evaluation_form.is_draft,
#             'completed_date': evaluation_form.completed_date.isoformat() if evaluation_form.completed_date else None,
#             'professional_responses': evaluation_form.professional_responses
#         })

#     except HealthCategory.DoesNotExist:
#         return JsonResponse({
#             'success': False,
#             'error': 'Categoría de salud no encontrada'
#         }, status=404)
#     except json.JSONDecodeError:
#         return JsonResponse({
#             'success': False,
#             'error': 'Datos JSON inválidos'
#         }, status=400)
#     except Exception as e:
#         import traceback
#         print("Error completo:")
#         print(traceback.format_exc())
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         }, status=500) 
    

import json
import uuid
import os
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.conf import settings
from prevcad.models import CategoryTemplate
import logging
import time
from prevcad.decorators import doctor_required
logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
@doctor_required
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

        obj.evaluation_form = new_form
        obj.save(update_fields=["evaluation_form"])
        
        return JsonResponse({
            'status': 'success',
            'message': 'Formulario de evaluación actualizado correctamente',
            'data': {
                'template_id': template_id,
                'updated_at': obj.updated_at.isoformat() if hasattr(obj, 'updated_at') else None,
                'nodes_count': len(new_form.get('question_nodes', []))
            }
        }, json_dumps_params={'indent': 2, 'ensure_ascii': False})

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al decodificar JSON',
            'details': {
                'received_data': new_form_data[:100] + '...' if len(new_form_data) > 100 else new_form_data
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
def update_training_form(request, template_id):
    """
    Actualiza el formulario de entrenamiento de una plantilla de categoría.
    """
    try:
        obj = get_object_or_404(CategoryTemplate, id=template_id)
        new_form_data = request.POST.get('training_form')
        media_file = request.FILES.get('media_file')
        
        if not new_form_data:
            return JsonResponse({
                'status': 'error', 
                'message': 'No se recibieron datos del formulario'
            }, status=400)
        
        new_form = json.loads(new_form_data)
        if "training_nodes" not in new_form or not isinstance(new_form["training_nodes"], list):
            return JsonResponse({
                'status': 'error', 
                'message': 'Estructura de datos inválida'
            }, status=400)

        # Manejar archivo multimedia si existe
        if media_file:
            file_name = handle_uploaded_file(media_file)
            
            # Actualizar el nodo correspondiente con la URL del archivo
            for node in new_form["training_nodes"]:
                if node.get('media_pending'):
                    node['media_url'] = file_name
                    del node['media_pending']

        # Actualizar o agregar los nodos de entrenamiento
        if not obj.training_form:
            obj.training_form = {}
        
        existing_nodes = obj.training_form.get('training_nodes', [])
        
        # Actualizar nodos existentes o agregar nuevos
        updated_nodes = []
        new_node_ids = {node['id'] for node in new_form['training_nodes']}
        
        # Mantener nodos existentes que no están siendo actualizados
        for node in existing_nodes:
            if node['id'] not in new_node_ids:
                updated_nodes.append(node)
        
        # Agregar los nuevos nodos
        updated_nodes.extend(new_form['training_nodes'])
        
        # Actualizar el formulario
        obj.training_form = {
            'training_nodes': updated_nodes
        }
        
        obj.save(update_fields=["training_form"])
        
        return JsonResponse({
            'status': 'success',
            'message': 'Formulario de entrenamiento actualizado correctamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al decodificar JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error updating training form: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def handle_uploaded_file(file):
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
    file_path = os.path.join(upload_dir, file_name)
    
    # Guardar el archivo
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    # Retornar la ruta relativa con el formato correcto
    return f'/media/uploads/{file_name}'  # Añadimos /media/ al inicio 
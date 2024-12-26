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

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
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
                'message': 'No se recibieron datos del formulario'
            }, status=400)
        
        new_form = json.loads(new_form_data)
        if "question_nodes" not in new_form or not isinstance(new_form["question_nodes"], list):
            return JsonResponse({
                'status': 'error', 
                'message': 'Estructura de datos inválida'
            }, status=400)

        obj.evaluation_form = new_form
        obj.save(update_fields=["evaluation_form"])
        
        return JsonResponse({
            'status': 'success',
            'message': 'Formulario de evaluación actualizado correctamente'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Error al decodificar JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error updating evaluation form: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_POST
@csrf_exempt
def update_training_form(request, template_id):
    """
    Actualiza el formulario de entrenamiento de una plantilla de categoría.
    Maneja la subida de archivos multimedia para nodos de tipo video.
    """
    try:
        print("Request data:", request.POST)
        print("Files:", request.FILES)
        
        obj = get_object_or_404(CategoryTemplate, id=template_id)
        
        # Inicializar o obtener el training_form
        if not obj.training_form:
            obj.training_form = {'training_nodes': []}
        
        nodes = obj.training_form['training_nodes']
        
        # Obtener el ID del nodo si estamos editando
        node_id = request.POST.get('node_id')
        content = request.POST.get('content')
        node_type = request.POST.get('type', 'TEXT_NODE')  # Tipo por defecto
        
        # Buscar el nodo existente o crear uno nuevo
        if node_id:
            node_id = int(node_id)
            node_index = next((i for i, node in enumerate(nodes) 
                             if node.get('id') == node_id), None)
            if node_index is not None:
                node = nodes[node_index]
            else:
                node = {'id': node_id}
                nodes.append(node)
        else:
            node = {'id': int(time.time() * 1000)}
            nodes.append(node)
        
        # Actualizar el contenido del nodo
        node.update({
            'type': node_type,
            'content': content
        })
        
        # Guardar los cambios
        obj.save(update_fields=['training_form'])
        
        return JsonResponse({
            'status': 'success',
            'message': 'Contenido actualizado correctamente',
            'node': node
        })
        
    except Exception as e:
        print(f"Error in update_training_form: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500) 
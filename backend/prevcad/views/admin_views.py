from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from prevcad.models import CategoryTemplate
import json

@require_POST
@csrf_exempt  # Only if you are sure this is safe and necessary
def update_evaluation_form(request, template_id):
    try:
        obj = get_object_or_404(CategoryTemplate, id=template_id)
        new_form_data = request.POST.get('evaluation_form')
        if not new_form_data:
            return JsonResponse({'status': 'error', 'message': 'No se recibieron datos del formulario'}, status=400)
        
        new_form = json.loads(new_form_data)
        if "question_nodes" not in new_form or not isinstance(new_form["question_nodes"], list):
            return JsonResponse({'status': 'error', 'message': 'Estructura de datos inválida'}, status=400)

        obj.evaluation_form = new_form
        obj.save(update_fields=["evaluation_form"])
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500) 
    
def update_training_form(request, template_id):
    try:
        obj = get_object_or_404(CategoryTemplate, id=template_id)
        new_form_data = request.POST.get('training_form')

        print(new_form_data)
        if not new_form_data:
            return JsonResponse({'status': 'error', 'message': 'No se recibieron datos del formulario'}, status=400)
        
        new_form = json.loads(new_form_data)
        if "training_nodes" not in new_form or not isinstance(new_form["training_nodes"], list):
            return JsonResponse({'status': 'error', 'message': 'Estructura de datos inválida'}, status=400)

        obj.training_form = new_form
        obj.save(update_fields=["training_form"])
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500) 
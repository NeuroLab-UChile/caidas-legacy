from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import path
import json
from ..models import HealthCategory, Recommendation
from .filters import HealthStatusFilter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.template.loader import TemplateDoesNotExist
from urllib.parse import unquote



@admin.register(HealthCategory)
class HealthCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'get_user_info',
        'get_template_name',
        'get_completion_status',
        'get_completion_date',
        'get_recommendation_status'
    ]

    # Definir los campos base del modelo
    base_fields = ['user', 'template']

    # Definir los campos de solo lectura
    readonly_fields = (
        'user',
        'template',
        'get_user_info',
        'get_template_name',
        'get_completion_status',
        'get_completion_date',
        'get_detailed_responses',
        'get_recommendation_editor',
        'get_professional_evaluation'
        
    )

    fieldsets = [
        ('Información Base', {
            'fields': (
                'user',
                'template',
            )
        }),
     
        ('Estado de Completación', {
            'fields': (
                'get_professional_evaluation',
                'get_completion_status',
                'get_completion_date',
                'get_detailed_responses',
            )
        }),
        ('Recomendación', {
            'fields': (
                'get_recommendation_editor',
            ),
            'classes': ('wide',)
        }),
   
    ]

    def get_professional_evaluation(self, obj):
        """Renderiza el formulario de evaluación profesional"""
        if not hasattr(obj, 'template') or obj.template.evaluation_type != 'PROFESSIONAL':
            return None
            
        try:
            evaluation_form = obj.get_or_create_evaluation_form()
            professional_responses = evaluation_form.professional_responses or {}
            
            context = {
                'health_category': obj,
                'evaluation_form': evaluation_form,
                'professional_responses': professional_responses,
                'completed_date': evaluation_form.completed_date,
                'is_completed': bool(evaluation_form.completed_date),
            }
            
            # Especificar la ruta completa
            template_path = 'admin/healthcategory/professional_evaluation.html'
            try:
                return mark_safe(render_to_string(template_path, context))
            except TemplateDoesNotExist:
                return format_html(
                    '<div class="text-red-500">Template no encontrado: {}</div>',
                    template_path
                )
        except Exception as e:
            return format_html(
                '<div class="text-red-500">Error al cargar evaluación profesional: {}</div>',
                str(e)
            )
    get_professional_evaluation.short_description = "Evaluación Profesional"

    def get_user_info(self, obj):
        if obj.user and obj.user.user:
            return f"{obj.user.user.get_full_name()} ({obj.user.user.username})"
        return "-"
    get_user_info.short_description = "Información de Usuario"

    def get_template_name(self, obj):
        return obj.template.name
    get_template_name.short_description = "Plantilla"

    def get_completion_status(self, obj):
        status = obj.get_status()
        return "Completado" if status['is_completed'] else "Pendiente"
    get_completion_status.short_description = "Estado"

    def get_completion_date(self, obj):
        try:
            return obj.evaluation_form.completed_date
        except:
            return None
    get_completion_date.short_description = "Fecha de Completado"

    def get_recommendation_status(self, obj):
        try:
            recommendation = obj.recommendation
            status_colors = {
                'verde': ('bg-green-100 text-green-800', '●'),
                'amarillo': ('bg-yellow-100 text-yellow-800', '●'),
                'rojo': ('bg-red-100 text-red-800', '●'),
                'gris': ('bg-gray-100 text-gray-600', '●')
            }
            color_class, dot = status_colors.get(recommendation.status_color, status_colors['gris'])
            
            # Mostrar estado de publicación y firma
            status_text = []
            if recommendation.is_draft:
                status_text.append("Borrador")
            else:
                status_text.append("Publicado")
                if recommendation.is_signed:
                    status_text.append("Firmado")
            
            return format_html(
                '<div class="flex flex-col gap-2">'
                '<span class="{} px-2 py-1 rounded-full text-xs font-medium">'
                '{} {}</span>'
                '<span class="text-xs text-gray-500">{}</span>'
                '</div>',
                color_class,
                dot,
                recommendation.status_color.capitalize(),
                ' • '.join(status_text)
            )
        except:
            return format_html(
                '<span class="text-xs text-gray-500">Sin recomendación</span>'
            )
    get_recommendation_status.short_description = "Estado de Recomendación"

    def get_detailed_responses(self, obj):
        responses = obj.evaluation_form.responses or {}
        processed_responses = {}

        for node_id, response in responses.items():
            processed_response = response.copy()
            if response.get('type') == 'SINGLE_CHOICE_QUESTION':
                options = response['answer'].get('options', [])
                selected = response['answer'].get('selectedOption')
                if selected is not None and selected < len(options):
                    processed_response['answer']['selected_text'] = options[selected]
            elif response.get('type') == 'MULTIPLE_CHOICE_QUESTION':
                options = response['answer'].get('options', [])
                selected = response['answer'].get('selectedOptions', [])
                processed_response['answer']['selected_texts'] = [
                    options[idx] for idx in selected if idx < len(options)
                ]
            processed_responses[node_id] = processed_response

        context = {'responses': processed_responses}
        return mark_safe(render_to_string('admin/healthcategory/detailed_responses.html', context))
    get_detailed_responses.short_description = "Detalle de Respuestas"



    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Recommendation):
                instance.updated_by = request.user.username
                if not instance.is_draft and instance.is_signed:
                    instance.signed_by = request.user.username
                    instance.signed_at = timezone.now()
            instance.save()
        formset.save_m2m() 

    def get_recommendation_editor(self, obj):
        """Renderiza el editor de recomendaciones"""
        recommendation = obj.get_or_create_recommendation()
        context = {
            'recommendation': recommendation,
            'health_category': obj,
            'default_recommendations': obj.template.default_recommendations or {},
        }
        return mark_safe(render_to_string(
            'admin/healthcategory/recommendation_editor.html',
            context
        ))
    get_recommendation_editor.short_description = "Editor de Recomendación"

    def save_model(self, request, obj, form, change):
        """Guarda el modelo y actualiza los campos relacionados con la evaluación profesional"""
        super().save_model(request, obj, form, change)
        
        if obj.template.evaluation_type == 'PROFESSIONAL':
            try:
                evaluation_form = obj.get_or_create_evaluation_form()
                
                # Debug: Imprimir estado inicial
                print(f"Estado inicial - is_draft: {evaluation_form.is_draft}, completed_date: {evaluation_form.completed_date}")
                
                if 'professional_responses' in request.POST:
                    # Obtener las respuestas actuales o inicializar
                    responses = evaluation_form.professional_responses or {}
                    
                    # Actualizar observaciones y diagnóstico
                    observations = request.POST.get('professional_responses[observations]', '').strip()
                    diagnosis = request.POST.get('professional_responses[diagnosis]', '').strip()
                    
                    if observations:
                        responses['observations'] = observations
                    if diagnosis:
                        responses['diagnosis'] = diagnosis
                    
                    # Actualizar el formulario
                    evaluation_form.professional_responses = responses
                    
                    # Manejar el estado de completado
                    if 'complete_evaluation' in request.POST:
                        print("Completando evaluación...")  # Debug
                        evaluation_form.completed_date = timezone.now()
                        evaluation_form.is_draft = False
                        
                        # Actualizar la recomendación
                        recommendation = obj.get_or_create_recommendation()
                        if recommendation:
                            recommendation.is_draft = False
                            recommendation.updated_by = request.user.username
                            recommendation.updated_at = timezone.now()
                            recommendation.save()
                            print(f"Recomendación actualizada - is_draft: {recommendation.is_draft}")  # Debug
                    
                    # Forzar el guardado y verificar que se guardó correctamente
                    evaluation_form.save()
                    evaluation_form.refresh_from_db()
                    
                    # Debug: Imprimir estado final
                    print(f"Estado final - is_draft: {evaluation_form.is_draft}, completed_date: {evaluation_form.completed_date}")
                    
            except Exception as e:
                print(f"Error al guardar la evaluación: {str(e)}")
                raise

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/save-professional-evaluation/',
                self.admin_site.admin_view(self.save_professional_evaluation),
                name='healthcategory_save_evaluation',
            ),
            path(
                '<int:category_id>/update-recommendation/',
                self.admin_site.admin_view(self.update_recommendation_view),
                name='update-recommendation',
            ),
        ]
        return custom_urls + urls

    def save_professional_evaluation(self, request, object_id):
        """Vista para guardar la evaluación profesional"""
        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'}, status=405)

        try:
            # Debug
            print(f"Buscando objeto con ID: {object_id}")
            
            # Obtener el objeto
            obj = self.get_object(request, unquote(object_id))
            if not obj:
                print(f"No se encontró el objeto con ID: {object_id}")
                return JsonResponse({'error': 'Objeto no encontrado'}, status=404)

            print(f"Objeto encontrado: {obj}")  # Debug
            
            data = json.loads(request.body)
            evaluation_form = obj.get_or_create_evaluation_form()
            
            # Obtener las respuestas profesionales
            professional_responses = data.get('professional_responses', {})
            
            # Actualizar las respuestas
            if evaluation_form.professional_responses is None:
                evaluation_form.professional_responses = {}
            evaluation_form.professional_responses.update(professional_responses)
            
            # Manejar el estado de completado
            if data.get('complete', False):
                now = timezone.now()
                evaluation_form.is_draft = False
                evaluation_form.completed_date = now
                
                # Actualizar la recomendación
                recommendation = obj.get_or_create_recommendation()
                if recommendation:
                    recommendation.is_draft = False
                    recommendation.updated_by = request.user.username
                    recommendation.updated_at = now
                    recommendation.save()
            
            evaluation_form.save()

            return JsonResponse({
                'success': True,
                'message': 'Evaluación guardada correctamente',
                'is_draft': evaluation_form.is_draft,
                'completed_date': evaluation_form.completed_date.isoformat() if evaluation_form.completed_date else None
            })

        except Exception as e:
            import traceback
            print("Error completo:")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=500)

    def update_recommendation_view(self, request, category_id):
        try:
            category = HealthCategory.objects.get(id=category_id)
            
            if request.method == 'POST':
                data = json.loads(request.body)
                recommendation_text = data.get('recommendation_text', '').strip()
                
                # Obtener nombre completo del profesional
                professional_name = request.user.get_full_name() or request.user.username
                
                # Obtener roles del usuario de manera más robusta
                professional_roles = []
                
                # 1. Primero intentar obtener roles de grupos
                user_groups = request.user.groups.all()
                if user_groups.exists():
                    professional_roles.extend([group.name for group in user_groups])
                
                # 2. Si no hay grupos, usar roles basados en permisos
                if not professional_roles:
                    if request.user.is_superuser:
                        professional_roles.append("Administrador")
                    if request.user.is_staff:
                        professional_roles.append("Personal Médico")
                
                # 3. Si aún no hay roles, usar rol por defecto
                if not professional_roles:
                    professional_roles.append("Profesional de la salud")
                
                # Unir roles y asegurarse de que no sea None
                professional_role = " • ".join(professional_roles)
                
                # Debug para verificar
                print(f"DEBUG - Información del profesional:")
                print(f"Nombre: {professional_name}")
                print(f"Roles encontrados: {professional_roles}")
                print(f"Rol final: {professional_role}")
                
                # Actualizar recomendación
                recommendation = category.get_or_create_recommendation()
                recommendation.text = recommendation_text
                recommendation.professional_name = professional_name
                recommendation.professional_role = professional_role
                recommendation.updated_by = request.user.username
                recommendation.updated_at = timezone.now()
                recommendation.is_draft = False
                
                # Debug antes de guardar
                print(f"DEBUG - Antes de guardar:")
                print(f"professional_role: {recommendation.professional_role}")
                
                recommendation.save()
                
                # Verificar después de guardar
                recommendation.refresh_from_db()
                print(f"DEBUG - Después de guardar:")
                print(f"professional_role: {recommendation.professional_role}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Recomendación actualizada correctamente',
                    'debug_info': {
                        'professional_name': professional_name,
                        'professional_role': professional_role
                    }
                })
                
        except HealthCategory.DoesNotExist:
            print(f"No se encontró la categoría con ID: {category_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'Categoría no encontrada'
            }, status=404)
            
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            import traceback
            print("Traceback completo:")
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'message': f'Error: {str(e)}'
            }, status=500)
            
        print("=== Fin de la Actualización ===\n")
        return HttpResponseRedirect("../../")

    class Media:
        css = {
            'all': (
                'https://cdn.tailwindcss.com',
                'admin/css/forms.css',
            )
        }
        js = (
            'admin/js/recommendation_editor.js',
            'admin/js/professional_evaluation.js',
        ) 
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
from django.utils.formats import date_format
from django.utils.timezone import localtime
from django.utils.timesince import timesince



@admin.register(HealthCategory)
class HealthCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'get_user_info',
        'get_template_name',
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

    def format_datetime(self, date):
        """Función auxiliar para formatear fechas de manera consistente"""
        if not date:
            return None
            
        # Asegurar que la fecha está en UTC
        if timezone.is_naive(date):
            date = timezone.make_aware(date)
            
        # Convertir a hora local
        local_date = timezone.localtime(date)
        
        return {
            'iso': date.isoformat(),
            'formatted': date_format(local_date, "j \d\e F \d\e Y, H:i"),
            'timesince': timesince(local_date),
        }

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
        if status['is_completed']:
            return "Completado"
        elif status['is_draft']:
            return "Pendiente"
        else:
            return "Pendiente"
    get_completion_status.short_description = "Estado"

    def get_completion_date(self, obj):
        """Muestra la fecha de completado con formato mejorado"""
        try:
            date_info = self.format_datetime(obj.evaluation_form.completed_date)
            if not date_info:
                return format_html(
                    '<span style="color: #6B7280; font-style: italic;">No completado</span>'
                )

            return format_html(
                '<div style="display: flex; flex-direction: column; gap: 4px;">'
                '<div style="color: #059669; font-weight: 500;">'
                '<span style="display: inline-block; width: 8px; height: 8px; '
                'background-color: #059669; border-radius: 50%; margin-right: 6px;'
                '"></span>Completado'
                '</div>'
                '<div style="color: #374151;">{}</div>'
                '<div style="color: #6B7280; font-style: italic;">hace {}</div>'
                '</div>',
                date_info['formatted'],
                date_info['timesince']
            )
        except Exception as e:
            return format_html(
                '<span style="color: #6B7280; font-style: italic;">'
                'Error al mostrar fecha: {}</span>', str(e)
            )

    get_completion_date.short_description = "Fecha de Completado"

    def get_recommendation_status(self, obj):
        """Muestra el estado de la recomendación con estilos mejorados"""
        try:
            recommendation = obj.recommendation
            
            # Configuración de estados con estilos y símbolos
            status_config = {
                'verde': {
                    'color': '#059669',  # Verde esmeralda
                    'bg': '#ECFDF5',
                    'border': '#A7F3D0',
                    'icon': '✓',
                    'label': 'Favorable'
                },
                'amarillo': {
                    'color': '#D97706',  # Ámbar
                    'bg': '#FFFBEB',
                    'border': '#FDE68A',
                    'icon': '⚠',
                    'label': 'Precaución'
                },
                'rojo': {
                    'color': '#DC2626',  # Rojo
                    'bg': '#FEF2F2',
                    'border': '#FECACA',
                    'icon': '!',
                    'label': 'Atención'
                },
                'gris': {
                    'color': '#6B7280',  # Gris
                    'bg': '#F9FAFB',
                    'border': '#E5E7EB',
                    'icon': '○',
                    'label': 'Pendiente'
                }
            }
            
            # Obtener configuración del estado actual
            status = status_config.get(recommendation.status_color, status_config['gris'])
            
            # Determinar estado de publicación
            publication_status = []
            if recommendation.is_draft:
                publication_status.append(("Borrador", "#6B7280"))  # Gris
            else:
                publication_status.append(("Publicado", "#059669"))  # Verde
                if recommendation.is_signed:
                    publication_status.append(("Firmado", "#2563EB"))  # Azul
            
            # Construir el HTML con estilos inline (para no depender de Tailwind)
            status_html = f'''
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <div style="
                        display: inline-flex;
                        align-items: center;
                        background-color: {status['bg']};
                        color: {status['color']};
                        border: 1px solid {status['border']};
                        padding: 4px 12px;
                        border-radius: 9999px;
                        font-size: 0.75rem;
                        font-weight: 500;
                        line-height: 1rem;
                    ">
                        <span style="margin-right: 4px;">{status['icon']}</span>
                        {status['label']}
                    </div>
                    <div style="
                        display: flex;
                        gap: 8px;
                        font-size: 0.75rem;
                    ">
            '''
            
            # Agregar pills de estado
            for label, color in publication_status:
                status_html += f'''
                    <span style="
                        color: {color};
                        background-color: {color}15;
                        padding: 2px 8px;
                        border-radius: 4px;
                        font-weight: 500;
                    ">{label}</span>
                '''
            
            status_html += '</div></div>'
            
            return format_html(status_html)
            
        except Exception as e:
            return format_html(
                '<span style="'
                'color: #6B7280;'
                'font-size: 0.75rem;'
                'font-style: italic;'
                '">Sin recomendación</span>'
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

            date_info = self.format_datetime(evaluation_form.completed_date)
            return JsonResponse({
                'success': True,
                'message': 'Evaluación guardada correctamente',
                'is_draft': evaluation_form.is_draft,
                'completed_date': date_info['iso'] if date_info else None,
                'formatted_date': date_info['formatted'] if date_info else None,
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
                now = timezone.now()
                
                recommendation = category.get_or_create_recommendation()
                recommendation.text = data.get('recommendation_text', '').strip()
                recommendation.status_color = data.get('status_color', '').strip()
                recommendation.is_draft = data.get('is_draft', False)
                recommendation.updated_by = request.user.username
                recommendation.updated_at = now
                recommendation.professional_name = request.user.get_full_name() or request.user.username
                recommendation.professional_role = " • ".join(
                    [group.name for group in request.user.groups.all()] or ["Profesional de la salud"]
                )

                if not recommendation.is_draft and data.get('is_signed'):
                    recommendation.signed_by = request.user.username
                    recommendation.signed_at = now

                recommendation.save()

                date_info = self.format_datetime(now)
                return JsonResponse({
                    'status': 'success',
                    'message': 'Recomendación actualizada correctamente',
                    'recommendation': {
                        'updated_at': date_info['iso'],
                        'formatted_date': date_info['formatted'],
                        'timesince': date_info['timesince'],
                        'professional': {
                            'name': recommendation.professional_name,
                            'role': recommendation.professional_role
                        }
                    }
                })
                
        except HealthCategory.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Categoría no encontrada'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error: {str(e)}'
            }, status=500)

    class Media:
        css = {
            'all': (
                'admin/css/custom_admin.css',
            )
        }
        js = (
            'admin/js/recommendation_editor.js',
            'admin/js/professional_evaluation.js',
        ) 
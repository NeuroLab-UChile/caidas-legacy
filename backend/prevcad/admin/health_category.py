from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import path, reverse
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
from django.core.handlers.wsgi import WSGIRequest
from threading import current_thread
from django.db import transaction
from ..models.user_types import UserTypes
from django.db.models import Q
from django.db import connection
import time



class UserProfileFilter(admin.SimpleListFilter):
    title = _('Usuario')  # Nombre que aparece en el panel
    parameter_name = 'user_filter'  # Parámetro en la URL

    def lookups(self, request, model_admin):
        """
        Retorna lista de tuplas (valor, texto) para las opciones del filtro
        """
        users = set()
        for obj in model_admin.model.objects.select_related('user__user').all():
            if obj.user and obj.user.user:
                user = obj.user.user
                # Tupla con (id, nombre completo (username))
                users.add((
                    str(obj.user.id),
                    f"{user.get_full_name()} ({user.username})"
                ))
        return sorted(users, key=lambda x: x[1].lower())

    def queryset(self, request, queryset):
        """
        Retorna el queryset filtrado basado en el valor seleccionado
        """
        if not self.value():
            return queryset
        return queryset.filter(user_id=self.value())



@admin.register(HealthCategory)
class HealthCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'get_user_info',
        'get_template_name',
        'get_completion_date',
        'get_recommendation_status',
        'get_edit_status',
        'get_evaluation_type'
    ]

    list_filter = (
        UserProfileFilter,
        'template',
    )

    search_fields = (
        'user__user__username',
        'user__user__first_name',
        'user__user__last_name',
        'template__name',
    )

    # Definir los campos base del modelo
    base_fields = ['user_profile', 'template']

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
        'get_professional_evaluation',
        'get_evaluation_type',
        
      
        
    )

    def get_evaluation_type(self, obj):
        return obj.template.evaluation_type if obj.template else 'Sin template'
    get_evaluation_type.short_description = 'Tipo de Evaluación'

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
                'evaluation_tags': obj.template.evaluation_tags if obj.template else []
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
        """Muestra la fecha de completado según el tipo de evaluación"""
        try:
            if not obj.template:
                return '-'

            evaluation_type = obj.template.evaluation_type
            
            # Intentar obtener o crear el form si no existe
            from prevcad.models import EvaluationForm
            evaluation_form, created = EvaluationForm.objects.get_or_create(
                health_category=obj,
                defaults={
                    'responses': {},
                    'professional_responses': {},
                    'question_nodes': obj.template.evaluation_form.get('question_nodes', []) if obj.template.evaluation_form else []
                }
            )
            
            def format_date(date):
                """Formatea la fecha de manera más legible"""
                if not date:
                    return None
                from django.utils import formats
                return formats.date_format(date, "d/m/Y H:i")
            
            # Para evaluaciones normales
            if evaluation_type == 'SELF':
                if evaluation_form.responses:
                    date_info = format_date(evaluation_form.completed_date)
                    return f'✅ {date_info}' if date_info else '✅ Completado'
                return '⏳ Pendiente'
            
            # Para evaluaciones profesionales
            else:
                if evaluation_form.professional_responses:
                    date_info = format_date(evaluation_form.completed_date)
                    return f'✅ {date_info}' if date_info else '✅ Completado'
                elif evaluation_form.responses:
                    date_info = format_date(evaluation_form.completed_date)
                    return f'⏳ Evaluado el {date_info}' if date_info else '⏳ Por evaluar'
                return '⏳ Pendiente'
            
        except Exception as e:
            print(f"Error en get_completion_date para HealthCategory {obj.id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return f'❌ Error: {str(e)}'

    get_completion_date.short_description = 'Estado'

    def get_recommendation_status(self, obj):
        """Muestra el estado de la recomendación con estilos mejorados"""
        try:
            recommendation = getattr(obj, 'recommendation', None)
            if not recommendation:
                return format_html(
                    '<span style="'
                    'color: #6B7280;'
                    'font-size: 0.875rem;'
                    'font-style: italic;'
                    '">Sin recomendación</span>'
                )
            
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
            
            # Construir el HTML con estilos inline
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
            print(f"Error en get_recommendation_status: {e}")
            return format_html(
                '<span style="'
                'color: #6B7280;'
                'font-size: 0.875rem;'
                'font-style: italic;'
                '">Error al cargar estado</span>'
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

    
    def get_default_recommendation(self, obj):
        """Retorna la recomendación por defecto basada en el tipo de evaluación"""
        return obj.template.get_default_recommendation()

    def get_recommendation_editor(self, obj):
        """Renderiza el editor de recomendaciones"""
        request = getattr(current_thread(), '_current_request', None)
        if not request:
            return "Error: No se pudo obtener el contexto de la solicitud"

        try:
            # Verificar permisos usando el método del modelo
            user_profile = getattr(request.user, 'profile', None)
            can_edit = obj.can_user_edit(user_profile)
            
            # Obtener el rol y su label
            user_role = getattr(user_profile, 'role', None)
            user_role_label = UserTypes(user_role).label if user_role else None

            # Obtener o crear recomendación
            try:
                recommendation = obj.recommendation
            except Recommendation.DoesNotExist:
                recommendation = Recommendation.objects.create(
                    health_category=obj,
                    status_color='gris',
                    is_draft=True,
                    use_default=True
                )

            context = {
                'recommendation': recommendation,
                'health_category': obj,
                'default_recommendations': obj.template.default_recommendations,
                'can_edit': can_edit,
                'user_role': user_role,
                'user_role_label': user_role_label,
                'is_readonly': obj.template.is_readonly if obj.template else True,
            }

            # Debug de permisos
            print(f"""
            Debug Permisos:
            - Usuario: {request.user.username}
            - Rol: {user_role}
            - Label: {user_role_label}
            - Puede editar: {can_edit}
            - Template readonly: {obj.template.is_readonly if obj.template else True}
            """)

            return render_to_string(
                'admin/healthcategory/recommendation_editor.html',
                context,
                request=request
            )

        except Exception as e:
            import traceback
            print(f"Error al renderizar el editor: {str(e)}")
            print(traceback.format_exc())
            return f"Error al cargar el editor: {str(e)}"

    get_recommendation_editor.short_description = "Editor de Recomendación"

    def response_change(self, request, obj):
        """Personaliza la respuesta después de intentar guardar"""
        if '_save' in request.POST and hasattr(request, '_permission_denied'):
            # Si hubo un error de permisos, redirigir de vuelta al formulario
            url = reverse(
                'admin:prevcad_healthcategory_change',
                args=[obj.pk],
            )
            return HttpResponseRedirect(url)
        return super().response_change(request, obj)

    def save_model(self, request, obj, form, change):
        from django.db import connection
        import time

        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            try:
                with transaction.atomic():
                    # Guardar objeto principal
                    super().save_model(request, obj, form, change)
                    
                    # Obtener o crear recomendación
                    recommendation = obj.get_or_create_recommendation()
                    
                    # Manejar archivo de video
                    if 'video' in request.FILES:
                        if recommendation.video:
                            recommendation.video.delete(save=False)
                        recommendation.video = request.FILES['video']
                    
                    # Guardar otros campos
                    recommendation.text = request.POST.get('text', '')
                    recommendation.status_color = request.POST.get('status_color', 'gris')
                    recommendation.is_draft = request.POST.get('is_draft') == 'true'
                    recommendation.updated_by = request.user.username
                    recommendation.updated_at = timezone.now()
                    
                    # Guardar cambios
                    recommendation.save()
                    
                    messages.success(request, "Recomendación guardada correctamente")
                    return JsonResponse({
                        'success': True,
                        'message': 'Cambios guardados correctamente'
                    })
                    
                break  # Si llegamos aquí, todo salió bien
                
            except OperationalError as e:
                attempt += 1
                if attempt == max_attempts:
                    messages.error(request, "Error al guardar: Base de datos ocupada")
                    return JsonResponse({
                        'success': False,
                        'error': 'Error al guardar: Base de datos ocupada'
                    }, status=503)
                time.sleep(0.5)  # Esperar antes de reintentar
                
            except Exception as e:
                print("Error al guardar:", str(e))
                messages.error(request, f"Error al guardar: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)

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

    def get_readonly_fields(self, request, obj=None):
        """Define campos de solo lectura basados en permisos"""
        readonly = list(self.readonly_fields)
        
        if obj:  # Solo para objetos existentes
            user_profile = getattr(request.user, 'profile', None)
            
            # Si el usuario no puede editar o el template está en readonly
            if not obj.can_user_edit(user_profile) or obj.template.is_readonly:
                # Hacer todos los campos readonly excepto los que ya lo son
                all_fields = [f.name for f in self.model._meta.fields]
                readonly.extend([f for f in all_fields if f not in readonly])
                
                # Mantener campos base siempre readonly
                readonly.extend(self.base_fields)
            
            # Campos que siempre son readonly
            readonly.extend(obj.READONLY_FIELDS)
        
        return list(set(readonly))  # Eliminar duplicados

    def get_edit_status(self, obj):
        """Muestra el estado de edición del objeto"""
        try:
            # Obtener el request del thread local actual
            from django.core.handlers.wsgi import WSGIRequest
            from threading import current_thread
            request = getattr(current_thread(), '_current_request', None)
            
            if not request or not isinstance(request, WSGIRequest):
                return format_html(
                    '<span style="color: #6B7280; padding: 4px 8px; '
                    'background: #F3F4F6; border-radius: 4px; font-size: 0.875rem;">'
                    '⚠️ Estado desconocido</span>'
                )

            user_profile = getattr(request.user, 'profile', None)
            can_edit = obj.can_user_edit(user_profile)
            is_readonly = obj.template.is_readonly

            if is_readonly:
                return format_html(
                    '<span style="color: #DC2626; padding: 4px 8px; '
                    'background: #FEF2F2; border-radius: 4px; font-size: 0.875rem;">'
                    '�� Solo lectura</span>'
                )
            elif can_edit:
                return format_html(
                    '<span style="color: #059669; padding: 4px 8px; '
                    'background: #ECFDF5; border-radius: 4px; font-size: 0.875rem;">'
                    '✏️ Editable</span>'
                )
            else:
                return format_html(
                    '<span style="color: #6B7280; padding: 4px 8px; '
                    'background: #F3F4F6; border-radius: 4px; font-size: 0.875rem;">'
                    '🚫 Sin permisos</span>'
                )
        except Exception as e:
            return format_html(
                '<span style="color: #DC2626;">Error: {}</span>', str(e)
            )
    get_edit_status.short_description = "Estado de Edición"

    def changelist_view(self, request, extra_context=None):
        """Guarda el request en el thread local para acceso posterior"""
        from threading import current_thread
        setattr(current_thread(), '_current_request', request)
        extra_context = extra_context or {}
        extra_context['can_edit'] = self.has_change_permission(request, self.get_object(request, object_id))
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Guarda el request en el thread local para acceso posterior"""
        from threading import current_thread
        setattr(current_thread(), '_current_request', request)
        extra_context = extra_context or {}
        extra_context['can_edit'] = self.has_change_permission(request, self.get_object(request, object_id))
        return super().change_view(request, object_id, form_url, extra_context)
    

    def has_change_permission(self, request, obj=None):
        """Controla el permiso de edición"""
        if obj is None:
            return True  # Permitir acceso a la lista
            
        user_profile = getattr(request.user, 'profile', None)
        if request.user.is_superuser:
            return True
            
        return obj.can_user_edit(user_profile)

    def get_fieldsets(self, request, obj=None):
        """Define los fieldsets incluyendo el editor de recomendaciones"""
        fieldsets = [
            ('Información Base', {
                'fields': (
                    'user',
                    'template',
                )
            }),
            ('Recomendación', {
                'fields': ('get_recommendation_editor',),
                'classes': ('wide',)
            }),
            ('Estado de Completación', {
                'fields': (
                    'get_professional_evaluation',
                    'get_completion_status',
                    'get_completion_date',
                    'get_detailed_responses',
                   
                )
            }),
        ]
        return fieldsets
    

    def get_edit_status_message(self, obj, can_edit, is_readonly):
        """Genera un mensaje detallado sobre el estado de edición"""
        if not obj:
            return ''

        styles = {
            'container': 'padding: 15px; border-radius: 8px; margin: 10px 0;',
            'title': 'font-size: 1.1em; font-weight: bold; margin-bottom: 10px;',
            'message': 'margin: 5px 0;',
            'info': 'margin-top: 10px; font-size: 0.9em; color: #666;',
            'readonly': 'background: #FEF2F2; border: 1px solid #FCA5A5;',
            'editable': 'background: #ECFDF5; border: 1px solid #6EE7B7;',
            'no_permission': 'background: #F3F4F6; border: 1px solid #D1D5DB;'
        }

        if is_readonly:
            return f"""
            <div style="{styles['container']} {styles['readonly']}">
                <div style="{styles['title']}">🔒 Modo Solo Lectura</div>
                <div style="{styles['message']}">
                    Esta categoría está configurada como solo lectura y no puede ser modificada.
                </div>
                <div style="{styles['info']}">
                    • El template está configurado como solo lectura<br>
                    • Solo los administradores pueden modificar este estado
                </div>
            </div>
            """
        elif can_edit:
            role_info = f"como {getattr(obj.user.user.profile, 'role', 'Usuario')}"
            return f"""
            <div style="{styles['container']} {styles['editable']}">
                <div style="{styles['title']}">✏️ Edición Permitida</div>
                <div style="{styles['message']}">
                    Tienes permisos para editar esta categoría {role_info}.
                </div>
                <div style="{styles['info']}">
                    • Puedes modificar los campos no marcados como "solo lectura"<br>
                    • Los cambios quedarán registrados con tu usuario
                </div>
            </div>
            """
        else:
            return f"""
            <div style="{styles['container']} {styles['no_permission']}">
                <div style="{styles['title']}">🚫 Sin Permisos de Edición</div>
                <div style="{styles['message']}">
                    No tienes los permisos necesarios para editar esta categoría.
                </div>
                <div style="{styles['info']}">
                    • Tu rol actual no está en la lista de roles permitidos<br>
                    • Contacta a un administrador si necesitas acceso
                </div>
            </div>
            """

  
        

    def can_user_edit(self, obj, user_profile):
        """Verifica si un usuario puede editar la categoría"""
        if not user_profile:
            return False
            
        user_role = getattr(user_profile, 'role', None)
        template_roles = obj.template.allowed_editor_roles if obj.template else []
        
        return user_role in template_roles

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/recommendation_editor.js',) 
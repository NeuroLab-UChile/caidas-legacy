from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django.utils.text import Truncator
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.urls import path, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.template.loader import TemplateDoesNotExist
from django.utils.formats import date_format
from django.utils.timesince import timesince
from django.db import transaction
import json
from ..models import CategoryTemplate, UserTypes, AccessLevel
from .filters import CategoryTypeFilter
from django.utils.timezone import localtime
from django.template.response import TemplateResponse

class RoleSelectWidget(forms.SelectMultiple):
    template_name = 'admin/widgets/role_select.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        
        # Agrupar roles por tipo usando las tuplas directamente
        grouped_choices = {
            'Roles Principales': UserTypes.get_professional_types(),
            'Personal Administrativo': [
                ('ADMIN', 'Administrador')
            ],
        }
        
        context['widget']['grouped_choices'] = grouped_choices
        context['widget']['value'] = value or []
        return context

class CategoryTemplateForm(forms.ModelForm):
    allowed_editor_roles = forms.MultipleChoiceField(
        choices=[(role.value, role.label) for role in UserTypes],
        widget=RoleSelectWidget,
        required=False,
        help_text="Selecciona los roles que pueden editar instancias de este template"
    )

    class Meta:
        model = CategoryTemplate
        fields = '__all__'


class CategoryTemplateAdmin(admin.ModelAdmin):
    form = CategoryTemplateForm
    list_filter = ('is_active', 'evaluation_type')
    search_fields = ('name', 'description')
    change_form_template = 'admin/categorytemplate/change_activity_form.html'

    EVALUATION_TYPE_CHOICES = [
        ('SELF', 'Auto-evaluación'),
        ('PROFESSIONAL', 'Evaluación Profesional'),
    ]
    
    fields = (
        'name',
        'description',
        'icon',
        'is_active',
        'evaluation_type',
        'evaluation_tags',
        'get_user_permissions',
    )

    list_display = [
        'name',
        'is_active',
        'preview_icon',
        'description_preview',
        'evaluation_type',
        'get_user_permissions',
        'get_actions_display'
    ]
    

    list_filter = (
        CategoryTypeFilter,
        'is_active',
    )

    search_fields = (
        'name',
        'description',
    )



    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'evaluation_type':
            kwargs['choices'] = self.EVALUATION_TYPE_CHOICES
        return super().formfield_for_choice_field(db_field, request, **kwargs)




    def _check_permission(self, user, perm_type):
        """Verifica permisos incluyendo grupos y permisos directos"""
        if not user.is_authenticated:
            return False
            
        if user.is_superuser:
            return True

        # Verificar si es doctor (igual que en HealthCategory)
        if user.groups.filter(name='DOCTOR').exists():
            return True

        # Verificar permisos directos y de grupo
        perm_name = f'prevcad.{perm_type}_categorytemplate'
        return (
            user.has_perm(perm_name) or
            any(group.permissions.filter(codename=f'{perm_type}_categorytemplate').exists() 
                for group in user.groups.all())
        )

    def has_view_permission(self, request, obj=None):
        return self._check_permission(request.user, 'view')

    def has_change_permission(self, request, obj=None):
        return self._check_permission(request.user, 'change')

    def has_add_permission(self, request):
        return self._check_permission(request.user, 'add')

    def has_delete_permission(self, request, obj=None):
        return self._check_permission(request.user, 'delete')

    def has_module_permission(self, request):
        return any([
            self._check_permission(request.user, perm)
            for perm in ['view', 'change', 'add', 'delete']
        ])

    def save_model(self, request, obj, form, change):
        """Guarda el modelo con manejo de permisos"""
        if not self._check_permission(request.user, 'change'):
            messages.error(request, "No tienes permisos para realizar esta acción.")
            return

        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
                messages.success(request, "Cambios guardados correctamente.")
        except Exception as e:
            messages.error(request, f"Error al guardar: {str(e)}")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/change_activity_form/',
                self.admin_site.admin_view(self.change_activity_form_view),
                name='categorytemplate_change_activity_form',
            ),
            path(
                '<path:object_id>/update_training_form/',
                self.admin_site.admin_view(self.update_training_form),
                name='update_training_form',
            ),
        ]
        return custom_urls + urls

    def change_activity_form_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj is None:
            raise Http404("CategoryTemplate no encontrado")

        context = {
            'title': 'Gestionar Formularios',
            'original': obj,
            'is_popup': False,
            'is_nav_sidebar_enabled': True,
            'has_permission': True,
            'site_url': '/',
            'site_header': self.admin_site.site_header,
            'site_title': self.admin_site.site_title,
            'app_label': 'prevcad',
            'opts': obj._meta,
            'is_read_only': not self._check_permission(request.user, 'change'),
            **self.admin_site.each_context(request),
        }
        
        return TemplateResponse(
            request,
            'admin/categorytemplate/change_activity_form.html',
            context
        )

    def get_actions_display(self, obj):
        """Muestra botones de acción basados en permisos"""
        try:
            request = getattr(self, 'request', None)
            if not request:
                return '-'

            # Solo mostrar botones si tiene permisos de edición
            if self._check_permission(request.user, 'change'):
                actions = []
                
                # Botón de editar template
                actions.append(
                    '<a href="{}" class="button" style="'
                    'background: #059669; color: white; padding: 4px 8px; '
                    'border-radius: 4px; text-decoration: none; font-size: 0.75rem; '
                    'margin-right: 4px; display: inline-block;">✏️ Editar Template</a>'.format(
                        reverse('admin:prevcad_categorytemplate_change', args=[obj.id])
                    )
                )

                # Botón de editar formulario de evaluación
                if obj.evaluation_type == 'PROFESSIONAL':
                    actions.append(
                        '<a href="{}#evaluation-form" class="button" style="'
                        'background: #2563eb; color: white; padding: 4px 8px; '
                        'border-radius: 4px; text-decoration: none; font-size: 0.75rem; '
                        'margin-right: 4px; display: inline-block;">📝 Editar Evaluación</a>'.format(
                            reverse('admin:prevcad_categorytemplate_change', args=[obj.id])
                        )
                    )

                # Botón de editar formulario de entrenamiento
                actions.append(
                    '<a href="{}#training-form" class="button" style="'
                    'background: #2563eb; color: white; padding: 4px 8px; '
                    'border-radius: 4px; text-decoration: none; font-size: 0.75rem; '
                    'margin-right: 4px; display: inline-block;">📚 Editar Entrenamiento</a>'.format(
                        reverse('admin:prevcad_categorytemplate_change', args=[obj.id])
                    )
                )

                return format_html(
                    '<div style="display: flex; gap: 4px; flex-wrap: wrap;">{}</div>',
                    mark_safe(''.join(actions))
                )

            # Si solo tiene permisos de lectura
            return format_html(
                '<span style="color: #6B7280; background: #F3F4F6; padding: 2px 8px; '
                'border-radius: 4px; font-size: 0.75rem;">👁️ Solo lectura</span>'
            )

        except Exception as e:
            return format_html(
                '<span style="color: #DC2626;">Error: {}</span>', str(e)
            )

    get_actions_display.short_description = 'Acciones'
    get_actions_display.allow_tags = True

    def preview_icon(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" style="height: 30px; width: auto;" alt="{}"/>',
                obj.icon.url,
                obj.name
            )
        return format_html(
            '<span style="color: #6B7280;">Sin ícono</span>'
        )
    preview_icon.short_description = 'Ícono'

    def description_preview(self, obj):
        return format_html(
            '<span style="color: #374151;">{}</span>',
            Truncator(obj.description).chars(50)
        )
    description_preview.short_description = 'Descripción'

    def get_user_permissions(self, obj):
        """Muestra los permisos del usuario actual"""
        try:
            request = getattr(self, 'request', None)
            if not request or not request.user.is_authenticated:
                return format_html(
                    '<span style="color: #DC2626; background: #FEF2F2; padding: 2px 8px; '
                    'border-radius: 4px; font-size: 0.75rem;">🚫 Sin acceso</span>'
                )

            user = request.user
            
            # Superusuario
            if user.is_superuser:
                return format_html(
                    '<div style="display: flex; gap: 4px; flex-direction: column;">'
                    '<span style="color: #059669; background: #ECFDF5; padding: 2px 8px; '
                    'border-radius: 4px; font-size: 0.75rem;">✏️ Acceso completo</span>'
                    '<span style="color: #4F46E5; background: #EEF2FF; padding: 2px 8px; '
                    'border-radius: 4px; font-size: 0.75rem;">👑 Superusuario</span>'
                    '</div>'
                )

            # Verificar permisos
            perms = []
            if self._check_permission(user, 'view'):
                perms.append('Ver')
            if self._check_permission(user, 'change'):
                perms.append('Editar')
            if self._check_permission(user, 'add'):
                perms.append('Añadir')
            if self._check_permission(user, 'delete'):
                perms.append('Eliminar')

            if perms:
                groups = [g.name for g in user.groups.all()]
                role = "Staff" if user.is_staff else "Usuario"
                
                return format_html(
                    '<div style="display: flex; gap: 4px; flex-direction: column;">'
                    '<span style="color: #0891b2; background: #CFFAFE; padding: 2px 8px; '
                    'border-radius: 4px; font-size: 0.75rem;">⚙️ {} ({})</span>'
                    '<span style="color: #4F46E5; background: #EEF2FF; padding: 2px 8px; '
                    'border-radius: 4px; font-size: 0.75rem;">🔑 {}</span>'
                    '</div>',
                    role,
                    ' • '.join(groups) if groups else 'Sin grupos',
                    ', '.join(perms)
                )

            return format_html(
                '<span style="color: #DC2626; background: #FEF2F2; padding: 2px 8px; '
                'border-radius: 4px; font-size: 0.75rem;">🚫 Sin acceso</span>'
            )

        except Exception as e:
            return format_html(
                '<span style="color: #DC2626;">Error: {}</span>', str(e)
            )

    get_user_permissions.short_description = "Permisos"
    get_user_permissions.allow_tags = True


    def get_readonly_fields(self, request, obj=None):
        """Si no es admin, todos los campos son de solo lectura"""
    
        if not self._check_permission(request.user, 'change'):
            return [field.name for field in self.model._meta.fields]
        return ['training_form_button', 'evaluation_form_button', 'training_form']

    def get_fieldsets(self, request, obj=None):
        """Define los fieldsets con estilos apropiados para Django Admin"""
        fieldsets = [
            ('Información Básica', {
                'fields': ('name', 'description', 'icon', 'is_active'),
                'classes': ('wide',)
            }),
            ('Tipo de Evaluación', {
                'fields': ('evaluation_type',),
                'classes': ('wide',)
            }),
        ]
        
        if obj and obj.evaluation_type == 'PROFESSIONAL':
            fieldsets.extend([
                ('Formulario de Evaluación', {
                    'fields': ('evaluation_form_button',),
                    
                }),
            ])

        if obj and obj.evaluation_type == 'PROFESSIONAL':
            fieldsets.extend([
                ('Formulario de Evaluación', {
                    'fields': ('evaluation_tags',),
                }),
            ])

        fieldsets.append(('Formulario de Entrenamiento', {
            'fields': ('training_form_button',),
        }))

        return fieldsets

    def display_tags(self, obj):
        """Muestra los tags en formato legible"""
        if obj.evaluation_tags:
            return ", ".join(obj.evaluation_tags)
        return "-"
    display_tags.short_description = "Tags de Evaluación"

    def evaluation_form_button(self, obj):
        return mark_safe(f"""
        <div class="form-row field-evaluation_form">
            <label for="id_evaluation_form">Formulario de Evaluación</label>
            <button type="button" class="btn btn-primary" onclick="openFormModal('EVALUATION')">
            Ver Formulario
            </button>
        </div>
        """)
    evaluation_form_button.short_description = "Formulario de Evaluación"

    def training_form_button(self, obj):
        return mark_safe(f"""
        <div class="form-row field-training_form">
            <label for="id_training_form">Formulario de Entrenamiento</label>
            <button type="button" class="btn btn-primary" onclick="openFormModal('TRAINING')">
            Ver Formulario
            </button>
        </div>
        """)

    training_form_button.short_description = "Formulario de Entrenamiento"



    def get_professional_roles(self, obj):
        """Muestra los roles profesionales asignados"""
        roles = UserTypes.get_professional_types()
        role_badges = []
        
        for role_value, role_label in roles:
            if hasattr(obj, f'is_{role_value.lower()}_template') and \
               getattr(obj, f'is_{role_value.lower()}_template'):
                role_badges.append(
                    f'<span class="role-badge role-{role_value.lower()}">{role_label}</span>'
                )
        
        return format_html('&nbsp;'.join(role_badges)) if role_badges else '-'
    
    get_professional_roles.short_description = 'Roles Profesionales'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Obtener roles profesionales
        professional_roles = UserTypes.get_professional_types()
        
        # Agregar ayuda contextual solo si el campo existe
        if 'name' in form.base_fields:
            form.base_fields['name'].help_text = 'Nombre de la plantilla de categoría'
        
        # Mostrar roles disponibles
        role_help = "Roles profesionales disponibles:<br>"
        for role_value, role_label in professional_roles:
            role_help += f"• {role_label}<br>"
        
        # Agregar help_text a is_active solo si existe
        if 'is_active' in form.base_fields:
            form.base_fields['is_active'].help_text = role_help
        
        return form

    class Media:
        css = {
            'all': ('admin/css/category_template.css',)
        }

    def update_training_form(self, request, object_id):
        try:
            # Obtener el objeto CategoryTemplate
            obj = self.get_object(request, object_id)
            if not obj:
                return JsonResponse({'status': 'error', 'message': 'Objeto no encontrado'}, status=404)

            # Verificar permisos
            if not self._check_permission(request.user, 'change'):
                return JsonResponse({'status': 'error', 'message': 'No tienes permisos'}, status=403)

            # Parsear los datos del formulario
            form_data = json.loads(request.POST.get('training_form', '{}'))
            training_nodes = form_data.get('training_nodes', [])

            # Manejar la subida de archivos
            image = request.FILES.get('image')
            video = request.FILES.get('video')

            # Directorio de almacenamiento
            import os
            from django.conf import settings

            training_images_dir = os.path.join(settings.MEDIA_ROOT, 'training_images')
            os.makedirs(training_images_dir, exist_ok=True)

            # Procesar la imagen si existe
            if image:
                # Generar un nombre de archivo único
                from django.utils.crypto import get_random_string
                filename = f"{get_random_string(10)}_{image.name}"
                filepath = os.path.join(training_images_dir, filename)

                # Guardar la imagen
                with open(filepath, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

                # Actualizar la URL de la imagen en los nodos
                for node in training_nodes:
                    if node.get('media_pending') and node.get('media_url') == image.name:
                        node['media_url'] = f'training_images/{filename}'
                        node.pop('media_pending', None)

            # Procesar el video si existe (similar a la imagen)
            if video:
                training_videos_dir = os.path.join(settings.MEDIA_ROOT, 'training_videos')
                os.makedirs(training_videos_dir, exist_ok=True)
                
                filename = f"{get_random_string(10)}_{video.name}"
                filepath = os.path.join(training_videos_dir, filename)

                with open(filepath, 'wb+') as destination:
                    for chunk in video.chunks():
                        destination.write(chunk)

                for node in training_nodes:
                    if node.get('media_pending') and node.get('media_url') == video.name:
                        node['media_url'] = f'training_videos/{filename}'
                        node.pop('media_pending', None)

            # Actualizar el formulario de entrenamiento
            obj.training_form = json.dumps(form_data)
            obj.save()

            return JsonResponse({
                'status': 'success', 
                'message': 'Formulario de entrenamiento actualizado correctamente',
                'training_nodes': training_nodes
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'status': 'error', 
                'message': f'Error al actualizar: {str(e)}'
            }, status=500)

admin.site.register(CategoryTemplate, CategoryTemplateAdmin)


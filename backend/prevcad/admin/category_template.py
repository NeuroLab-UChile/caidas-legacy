from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from django.utils.safestring import mark_safe
from ..models import CategoryTemplate, UserTypes, AccessLevel

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
    list_display = (
        'name', 
        'is_active', 
        'preview_icon', 
        'description_preview', 
        'evaluation_type',
        'is_readonly',
        'get_professional_roles',
    )
    

    def is_admin_user(self, request):
        """
        Verifica si el usuario tiene perfil de administrador
        """
        return hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'

    def has_change_permission(self, request, obj=None):
        """Solo usuarios admin pueden editar"""
        return self.is_admin_user(request)

    def has_add_permission(self, request):
        """Solo usuarios admin pueden crear"""
        return self.is_admin_user(request)

    def has_delete_permission(self, request, obj=None):
        """Solo usuarios admin pueden eliminar"""
        return self.is_admin_user(request)

    def get_readonly_fields(self, request, obj=None):
        """Si no es admin, todos los campos son de solo lectura"""
    
        if not self.is_admin_user(request):
            return [field.name for field in self.model._meta.fields]
        return ['training_form_button', 'evaluation_form_button', 'training_form']

    def get_fieldsets(self, request, obj=None):
        # Fieldsets base para todos los usuarios
        fieldsets = [
            ('Información Básica', {
                'fields': ('name', 'description', 'icon', 'is_active')
            }),
            ('Tipo de Evaluación', {
                'fields': ('evaluation_type',),
            }),
        ]
        
        # Agregar configuración de permisos para superusuarios y admins
        if self.is_admin_user(request):
            fieldsets.insert(1, ('Configuración de Permisos', {
                'fields': ('allowed_editor_roles', 'is_readonly'),
                'description': 'Define quién puede editar las instancias y si son de solo lectura',
            }))
        
        # Agregar campos de formularios según el tipo de evaluación
        if obj and obj.evaluation_type == 'SELF':
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

    def preview_icon(self, obj):
        if obj.icon:
            return format_html('<img src="{}" style="height: 30px; width: auto;"/>', obj.icon.url)
        return "Sin ícono"
    preview_icon.short_description = 'Ícono'

    def description_preview(self, obj):
        return Truncator(obj.description).chars(50)
    description_preview.short_description = 'Descripción'

    def get_editor_roles(self, obj):
        """Muestra los roles con permiso"""
        if not obj.allowed_editor_roles:
            return "Sin roles asignados"
            
        roles = [role for role in UserTypes if role.value in obj.allowed_editor_roles]
        role_badges = []
        
        for role in roles:
            color = {
                'ADMIN': 'red',
                'DOCTOR': 'green',
                'NURSE': 'blue',
                'PATIENT': 'gray',
                'MANAGER': 'orange',
                'COORDINATOR': 'purple'
            }.get(role.value, 'gray')
            
            badge = format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; '
                'border-radius: 10px; font-size: 11px; margin: 0 2px;">{}</span>',
                color, role.label
            )
            role_badges.append(badge)
            
        return format_html(''.join(str(badge) for badge in role_badges))
        
    get_editor_roles.short_description = "Roles con permiso"

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
        
        # Agregar ayuda contextual
        form.base_fields['name'].help_text = 'Nombre de la plantilla de categoría'
        
        # Mostrar roles disponibles
        role_help = "Roles profesionales disponibles:<br>"
        for role_value, role_label in professional_roles:
            role_help += f"• {role_label}<br>"
        
        if 'is_active' in form.base_fields:
            form.base_fields['is_active'].help_text = role_help
        
        return form

    class Media:
        css = {
            'all': ('admin/css/category_template.css',)
        }

admin.site.register(CategoryTemplate, CategoryTemplateAdmin)


from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from django.utils.safestring import mark_safe
from ..models import CategoryTemplate

@admin.register(CategoryTemplate)
class CategoryTemplateAdmin(admin.ModelAdmin):
    list_filter = ('is_active', 'evaluation_type')
    search_fields = ('name', 'description')
    change_form_template = 'admin/categorytemplate/change_activity_form.html'
    list_display = ('name', 'is_active', 'preview_icon', 'description_preview', 'evaluation_type')

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Información Básica', {
                'fields': ('name', 'description', 'icon', 'is_active')
            }),
            ('Permisos de Edición', {
                'fields': ('editable_fields_by_user_type',),
                'description': "Defina qué campos son editables para cada tipo de usuario.",
            }),
            ('Tipo de Evaluación', {
                'fields': ('evaluation_type',),
            }),
        ]
        
        if obj.evaluation_type == 'SELF':
            fieldsets.extend([
                ('Formulario de Evaluación', {
                    'fields': ('evaluation_form_button',),
                }),
            ])

        fieldsets.append(('Formulario de Entrenamiento', {
            'fields': ('training_form_button',),
        }))
        return fieldsets

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

    def get_readonly_fields(self, request, obj=None):
        readonly = ['training_form_button', 'evaluation_form_button']
        
        if not request.user.is_superuser:
            readonly.append('evaluation_type')
        
        if obj and obj.evaluation_type == 'SELF':
            if not hasattr(request.user, 'profile') or request.user.profile.role != 'doctor':
                readonly.append('self_evaluation_form')
        
        return readonly

    def preview_icon(self, obj):
        if obj.icon:
            return format_html('<img src="{}" style="height: 30px; width: auto;"/>', obj.icon.url)
        return "Sin ícono"
    preview_icon.short_description = 'Ícono'

    def description_preview(self, obj):
        return Truncator(obj.description).chars(50)
    description_preview.short_description = 'Descripción'


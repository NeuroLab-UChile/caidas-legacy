import re
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.text import Truncator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
import json
from django.urls import reverse
from django.contrib.admin import SimpleListFilter
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import models
from django import forms
import os
from django.conf import settings
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder

from .models import (
  TextRecomendation,

  CategoryTemplate,
  HealthCategory,
  ActivityNode,
  ActivityNodeDescription,
  TextQuestion,
  SingleChoiceQuestion,
  MultipleChoiceQuestion,
  ScaleQuestion,
  ImageQuestion,
  ResultNode,
  WeeklyRecipeNode,
  Appointment,
  UserProfile
)

# Define an inline admin descriptor for Profile model
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'

# Add HealthCategory inline to show categories in user admin
class HealthCategoryInline(admin.TabularInline):
  model = HealthCategory
  fk_name = 'user'
  extra = 0
  readonly_fields = ['template']  # Make them read-only
  can_delete = True
  verbose_name_plural = 'Health Categories'

# Extend the existing UserAdmin
class UserAdmin(BaseUserAdmin):
  inlines = [UserProfileInline]  # Add HealthCategoryInline
  list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'get_role')
  list_filter = ('is_staff', 'is_superuser', 'is_active')

  def get_inline_instances(self, request, obj=None):
    if not obj:
      return list()
    return super(UserAdmin, self).get_inline_instances(request, obj)

  def get_role(self, obj):
    try:
      return obj.profile.get_role_display()  # Usando el related_name 'profile'
    except (UserProfile.DoesNotExist, AttributeError):
      return 'Sin perfil'  # Valor por defecto si no existe perfil
  get_role.short_description = 'Rol'

  def save_model(self, request, obj, form, change):
    super().save_model(request, obj, form, change)
    # Asegurarse de que el usuario tenga un perfil
    UserProfile.objects.get_or_create(user=obj)

class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if obj is None:
            return null
        return super().default(obj)

@admin.register(CategoryTemplate)
class CategoryTemplateAdmin(admin.ModelAdmin):
    change_form_template = 'admin/categorytemplate/change_activity_form.html'
    list_display = ('name', 'is_active', 'preview_icon', 'description_preview', 'get_evaluation_type_display')
    list_filter = ('is_active', 'evaluation_type')
    search_fields = ('name', 'description')

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Información Básica', {
                'fields': ('name', 'description', 'icon', 'is_active')
            })
        ]
        
        # Solo los superusuarios pueden ver y editar el tipo de evaluación
        if request.user.is_superuser:
            fieldsets.append(
                ('Tipo de Evaluación', {
                    'fields': ('evaluation_type',),
                    'description': 'Solo administradores pueden modificar el tipo de evaluación.'
                })
            )

        # Siempre mostrar el training form y el botón de gestión
        fieldsets.append(
            ('Nodos de Entrenamiento', {
                'fields': ('training_form', 'training_form_button'),
                'description': 'Configure los nodos de entrenamiento.',
            })
        )

        # Mostrar el formulario de evaluación según el tipo
        if obj and obj.evaluation_type:
            if obj.evaluation_type == 'SELF':
                if hasattr(request.user, 'profile') and request.user.profile.role == 'doctor':
                    fieldsets.append(
                        ('Formulario de Autoevaluación', {
                            'fields': ('self_evaluation_form', 'evaluation_form_button'),
                            'description': 'Configure las preguntas para la autoevaluación.'
                        })
                    )
            else:  # PROFESSIONAL
                fieldsets.append(
                    ('Formulario de Evaluación Profesional', {
                            'fields': ('professional_evaluation_form', 'evaluation_form_button'),
                        'description': 'Configure el formulario de evaluación profesional.'
                    })
                )

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly = ['training_form_button', 'evaluation_form_button']  # Botones siempre readonly
        
        if not request.user.is_superuser:
            readonly.append('evaluation_type')
        
        if obj and obj.evaluation_type == 'SELF':
            if not hasattr(request.user, 'profile') or request.user.profile.role != 'doctor':
                readonly.append('self_evaluation_form')
        
        return readonly





    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            # Personalizar widgets para los campos de formulario
            if 'training_form' in form.base_fields:
                form.base_fields['training_form'].widget = forms.Textarea(attrs={
                    'rows': 10,
                    'class': 'vLargeTextField',
                    'placeholder': 'Configure aquí los nodos de entrenamiento'
                })
            if 'self_evaluation_form' in form.base_fields:
                form.base_fields['self_evaluation_form'].widget = forms.Textarea(attrs={
                    'rows': 10,
                    'class': 'vLargeTextField',
                    'placeholder': 'Configure aquí las preguntas de autoevaluación'
                })
            if 'professional_evaluation_form' in form.base_fields:
                form.base_fields['professional_evaluation_form'].widget = forms.Textarea(attrs={
                    'rows': 10,
                    'class': 'vLargeTextField',
                    'placeholder': 'Configure aquí el formulario de evaluación profesional'
                })
        return form

    class Media:
        js = [
            'admin/js/vendor/jquery/jquery.min.js',
            'admin/js/jquery.init.js',
            'admin/js/categorytemplate/change_activity_form.js',
        ]

    def get_evaluation_type_display(self, obj):
        evaluation_types = {
            'SELF': 'Autoevaluación',
            'PROFESSIONAL': 'Evaluación Profesional'
        }
        return evaluation_types.get(obj.evaluation_type, 'Desconocido')
    get_evaluation_type_display.short_description = 'Tipo de Evaluación'

    def save_model(self, request, obj, form, change):
        if 'evaluation_type' in form.changed_data:
            if not request.user.is_superuser:
                messages.error(request, "Solo los administradores pueden cambiar el tipo de evaluación")
                return
            
            # Limpiar el formulario anterior al cambiar el tipo
            if obj.evaluation_type == 'SELF':
                obj.professional_evaluation_form = {}
                messages.info(request, "Se ha configurado como autoevaluación y se ha limpiado el formulario profesional")
            else:
                obj.self_evaluation_form = {}
                messages.info(request, "Se ha configurado como evaluación profesional y se ha limpiado el formulario de autoevaluación")
            
        if obj.evaluation_type == 'SELF' and 'self_evaluation_form' in form.changed_data:
            if not hasattr(request.user, 'profile') or request.user.profile.role != 'doctor':
                messages.error(request, "Solo los doctores pueden modificar el formulario de autoevaluación")
                return
        
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        # Verificar permisos básicos primero
        if not super().has_change_permission(request, obj):
            return False

        # Si es superusuario, tiene todos los permisos
        if request.user.is_superuser:
            return True

        # Si no es superusuario, no puede cambiar el tipo de evaluación
        if obj and 'evaluation_type' in request.POST:
            return False

        return True

    def preview_icon(self, obj):
        if obj.icon:
            return format_html('<img src="{}" style="height: 30px; width: auto;"/>', obj.icon.url)
        return "Sin ícono"
    preview_icon.short_description = 'Ícono'

    def description_preview(self, obj):
        return Truncator(obj.description).chars(50)
    description_preview.short_description = 'Descripción'

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

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        
        if "_continue" in request.POST and 'evaluation_type' in request.POST:
            # Redirigir a la misma página para mostrar los campos actualizados
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(request.path)
            
        return response

    def formatted_description(self, obj):
        truncated_text = Truncator(obj.description).chars(50, truncate='...')
        return format_html(
            f'<span title="{obj.description}">{truncated_text}</span>'
        )

    formatted_description.short_description = "Descripción"
  

# Unregister the original User admin and register the new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models

class HealthStatusFilter(SimpleListFilter):
    title = 'Estado'
    parameter_name = 'status_color'

    def lookups(self, request, model_admin):
        return HealthCategory.COLOR_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status_color=self.value())

@admin.register(HealthCategory)
class HealthCategoryAdmin(admin.ModelAdmin):
    # Display and ordering
    list_display = [
        'get_user_info',
        'get_template_name',
        'get_completion_status',
        'completion_date',
        'is_draft',
        'get_status_color',
    ]
    
    list_filter = [
        ('completion_date', admin.DateFieldListFilter),
        ('template', admin.RelatedFieldListFilter),
        ('user__user__username', admin.AllValuesFieldListFilter),
    ]
    
    search_fields = [
        'user__user__username',
        'user__user__email',
        'user__user__first_name',
        'user__user__last_name',
        'template__name',
        'professional_recommendations'
    ]
    
    ordering = ['-completion_date']
    list_per_page = 20

    # Fields and fieldsets configuration
    readonly_fields = [
        'completion_date',
        'get_user_info',
        'get_template_name',
        'get_status_color',
        'get_completion_status',
        'is_draft',
        'professional_recommendations_updated_at',
        'professional_recommendations_updated_by',
        'get_detailed_responses'
    ]

    fieldsets = (
        ('Información del Paciente', {
            'fields': (
                'get_user_info',
                'get_template_name',
                'template',
            ),
            'classes': ('wide',)
        }),
        ('Estado y Fechas', {
            'fields': (
                'get_completion_status',
                'completion_date',
            ),
        }),
        ('Recomendaciones Médicas', {
            'fields': (
                'professional_recommendations',
                ('status_color'),
                ('professional_recommendations_updated_at', 'professional_recommendations_updated_by')
            ),
            'description': 'Estado y color de las recomendaciones médicas.',
            'classes': ('wide',)
        }),
    )

    # Templates and Media
    change_form_template = 'admin/healthcategory/change_form.html'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

    # Helper methods for display
    def get_detailed_responses(self, obj):
        from django.template.loader import render_to_string
        
        if not obj.responses:
            responses = {}
        else:
            responses = {}
            for node_id, response in obj.responses.items():
                processed_response = response.copy()
                
                # Procesar respuestas de opción única
                if response.get('type') == 'SINGLE_CHOICE_QUESTION':
                    answer = response.get('answer', {})
                    options = answer.get('options', [])
                    selected = answer.get('selectedOption')
                    if selected is not None and selected < len(options):
                        processed_response['answer']['selected_text'] = options[selected]
                        
                # Procesar respuestas de opción múltiple
                elif response.get('type') == 'MULTIPLE_CHOICE_QUESTION':
                    answer = response.get('answer', {})
                    options = answer.get('options', [])
                    selected = answer.get('selectedOptions', [])
                    selected_texts = []
                    for idx in selected:
                        if idx < len(options):
                            selected_texts.append(options[idx])
                    processed_response['answer']['selected_texts'] = selected_texts
                    
                responses[node_id] = processed_response
        
        context = {'responses': responses}
        return mark_safe(render_to_string('admin/healthcategory/detailed_responses.html', context))

    get_detailed_responses.short_description = "Detalle de Respuestas"

    def get_user_info(self, obj):
        if obj.user and obj.user.user:
            user = obj.user.user
            return format_html(
                '<div style="min-width: 200px;">'
                '<strong style="font-size: 14px;">{username}</strong><br>'
                '<small style="color: #666;">{nombre} {apellido}</small><br>'
                '<small style="color: #888;">{email}</small>'
                '</div>',
                username=user.username,
                nombre=user.first_name or '',
                apellido=user.last_name or '',
                email=user.email or ''
            )
        return "Usuario no disponible"
    get_user_info.short_description = 'Usuario'

    def get_template_name(self, obj):
        return obj.template.name if obj.template else "Sin plantilla"
    get_template_name.short_description = 'Plantilla'

    def get_completion_status(self, obj):
        if obj.completion_date:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">●</span> '
                '<span style="color: #28a745;">Completado</span>'
            )
        return format_html(
            '<span style="color: #ffc107; font-weight: bold;">●</span> '
            '<span style="color: #ffc107;">Pendiente</span>'
        )
    get_completion_status.short_description = 'Estado'


    def get_status_color(self, obj):
        color_map = {
            'verde': '#28a745',
            'amarillo': '#ffc107',
            'rojo': '#dc3545',
            'gris': '#6c757d'
        }
        if obj.status_color:
            return format_html(
                '<span style="color: {}; font-weight: bold;">●</span> {}',
                color_map.get(obj.status_color, '#6c757d'),
                obj.get_status_color_display()
            )
        return "Sin asignar"
    get_status_color.short_description = 'Color de riesgo'

    def response_change(self, request, obj):
        if "_save_draft" in request.POST:
            obj.is_draft = True
            obj.save()
            
            self.message_user(
                request, 
                "Las recomendaciones se han guardado como borrador y NO son visibles para el paciente.",
                level=messages.WARNING
            )
            return self.response_post_save_change(request, obj)
        
        # Si no es borrador, se guarda como firmado
        obj.is_draft = False
        obj.professional_recommendations_updated_by = request.user.get_full_name() or request.user.username
        obj.professional_recommendations_updated_at = timezone.now()
        obj.save()
        
        self.message_user(
            request, 
            "✓ Las recomendaciones han sido firmadas y son visibles para el paciente.",
            level=messages.SUCCESS
        )
        return super().response_change(request, obj)

    def save_model(self, request, obj, form, change):
        if 'doctor_recommendations' in form.changed_data or 'status_color' in form.changed_data:
            if not obj.is_draft:
                obj.professional_recommendations_updated_by = request.user.get_full_name() or request.user.username
                obj.professional_recommendations_updated_at = timezone.now()
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['professional_recommendations'].help_text = (
            "Las recomendaciones serán visibles para el paciente cuando se guarden sin marcar como borrador."
        )
        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(self.fieldsets)  # Convertir a lista para poder modificar

        # Si es evaluación profesional, agregar el campo de resultado
        if obj and obj.template and obj.template.evaluation_type == 'PROFESSIONAL':
            fieldsets.insert(2, (
                'Evaluación Profesional', {
                    'fields': ('professional_evaluation_result',),
                    'description': 'Resultado de la evaluación profesional.',
                    'classes': ('wide',)
                }
            ))

        # Agregar el fieldset de respuestas al final
        fieldsets.append(
            ('Respuestas del Paciente', {
                'fields': ('get_detailed_responses',),
                'classes': ('collapse',),
                'description': 'Historial completo de respuestas del paciente.'
            })
        )

        return fieldsets

    def save_model(self, request, obj, form, change):
        if 'professional_evaluation_result' in form.changed_data:
            if not obj.is_draft:
                obj.professional_recommendations_updated_by = request.user.get_full_name() or request.user.username
                obj.professional_recommendations_updated_at = timezone.now()
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.template and obj.template.evaluation_type == 'PROFESSIONAL':
            form.base_fields['professional_evaluation_result'].widget = forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'vLargeTextField',
                    'placeholder': 'Ingrese el resultado de la evaluación profesional'
                }
            )
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        
        try:
            # Asegurarse de que los datos son diccionarios válidos
            training_form = obj.training_form if isinstance(obj.training_form, dict) else {}
            evaluation_form = (
                obj.self_evaluation_form if obj.evaluation_type == 'SELF' 
                else obj.professional_evaluation_form
            )
            evaluation_form = evaluation_form if isinstance(evaluation_form, dict) else {}

            # Serializar los datos
            extra_context['training_form'] = training_form
            extra_context['evaluation_form'] = evaluation_form

        except Exception as e:
            print(f"Error preparing data: {e}")
            extra_context['training_form'] = {'training_nodes': []}
            extra_context['evaluation_form'] = {'question_nodes': []}

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

class AppointmentForm(forms.ModelForm):
    date = forms.DateField(
        widget=admin.widgets.AdminDateWidget(),
        help_text="Seleccione la fecha de la cita"
    )
    time = forms.TimeField(
        widget=admin.widgets.AdminTimeWidget(),
        required=False
    )

    class Meta:
        model = Appointment
        fields = ['title', 'date', 'description', 'user']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class AppointmentInline(admin.TabularInline):
    model = Appointment
    form = AppointmentForm
    extra = 1
    template = 'admin/appointment/edit_inline/tabular.html'
    fields = ('title', 'date', 'description')
    
    class Media:
        css = {
            'all': ('admin/css/forms.css', 'admin/css/widgets.css')
        }
        js = ('admin/js/calendar.js', 'admin/js/admin/DateTimeShortcuts.js')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    form = AppointmentForm
    list_display = ('title', 'user', 'date', 'created_at')
    list_filter = ('date', 'created_at', 'user')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'date'
    ordering = ('-date',)
    
    # Especifica los templates personalizados
    change_form_template = 'admin/appointment/change_form.html'
    change_list_template = 'admin/appointment/change_list.html'

    class Media:
        css = {
            'all': ('admin/css/forms.css', 'admin/css/widgets.css')
        }
        js = ('admin/js/calendar.js', 'admin/js/admin/DateTimeShortcuts.js')

class CustomUserAdmin(UserAdmin):
    inlines = [AppointmentInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# 1. Primero, registra UserProfile directamente
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')





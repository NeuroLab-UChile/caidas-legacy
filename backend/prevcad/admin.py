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

@admin.register(CategoryTemplate)
class CategoryTemplateAdmin(admin.ModelAdmin):
  change_form_template = 'admin/categorytemplate/change_activity_form.html'
  list_display = ('name', 'is_active', 'preview_icon', 'description_preview')
  list_filter = ('is_active',)
  search_fields = ('name', 'description')

  
  
  fieldsets = (
    ('Información Básica', {
      'fields': ('name', 'description', 'icon', 'is_active')
    }),
    ('Formulario de Evaluación', {
      'classes': ('wide',),
      'fields': ('evaluation_form_button',),
      'description': 'Configure las preguntas del formulario de evaluación.'
    }),
    ('Nodos de Entrenamiento', {
      'classes': ('collapse',),
      'fields': ('training_nodes_button',),
    }),
  )
  readonly_fields = ('evaluation_form_button', 'training_nodes_button')

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

  def training_nodes_button(self, obj):
    return mark_safe(f"""
     <div class="form-row field-training_form">
    <label for="id_training_form">Formulario de Entrenamiento</label>
    <button type="button" class="btn btn-primary" onclick="openFormModal('TRAINING')">
      Ver Formulario
    </button>
  </div>
    """)
  training_nodes_button.short_description = "Nodos de Entrenamiento"

  def response_change(self, request, obj):
      if "_add_node" in request.POST:
          node_data = self._get_node_data_from_request(request)
          obj.add_activity_node(node_data)
          self.message_user(request, "Pregunta agregada exitosamente")
      elif "_edit_node" in request.POST:
          node_id = request.POST.get('node_id')
          node_data = self._get_node_data_from_request(request)
          self._edit_node(obj, node_id, node_data)
          self.message_user(request, "Pregunta actualizada exitosamente")
      elif "_delete_node" in request.POST:
          node_id = request.POST.get('node_id')
          self._delete_node(obj, node_id)
          self.message_user(request, "Pregunta eliminada exitosamente")
      return super().response_change(request, obj)

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
        ('Respuestas del Paciente', {
            'fields': ('get_detailed_responses',),
            'classes': ('collapse',),
            'description': 'Historial completo de respuestas del paciente.'
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





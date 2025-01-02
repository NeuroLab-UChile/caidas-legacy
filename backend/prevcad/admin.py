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
from django.urls import path

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
  UserProfile,
 
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
            return None
        return super().default(obj)



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
        readonly = ['training_form_button', 'evaluation_form_button']  # Botones siempre readonly
        
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

    def evaluation_form_button(self, obj):
        return mark_safe(f"""
    <div class="form-row field-evaluation_form">
        <label for="id_evaluation_form">Formulario de Evaluación</label>
        <button type="button" class="btn btn-primary" onclick="openFormModal('EVALUATION')">
        Ver Formulario
        </button>
    </div>
        """)


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
    list_display = [
        'get_user_info',
        'get_template_name',
        'get_completion_status',
        'get_completion_date',
        'get_is_draft',
        'get_status_color'
    ]
    
    list_filter = [
        ('evaluation_form__completed_date', admin.DateFieldListFilter),
        ('template', admin.RelatedFieldListFilter),
        ('user__user__username', admin.AllValuesFieldListFilter),
    ]
    
    search_fields = [
        'user__user__username',
        'user__user__email',
        'user__user__first_name',
        'user__user__last_name',
        'template__name',
    ]
    
    readonly_fields = [
        'get_user_info',
        'get_template_name',
        'get_completion_status',
        'get_completion_date',
        'get_is_draft',
        'get_status_color',
        'get_evaluation_data',
        'get_recommendation_data'
    ]

    fieldsets = (
        ('Información del Usuario', {
            'fields': (
                'user',
                'get_user_info',
                'template',
                'get_template_name',
            )
        }),
        ('Estado', {
            'fields': (
                'get_completion_status',
                'get_completion_date',
                'get_is_draft',
                'get_status_color'
            )
        }),
        ('Datos de Evaluación', {
            'fields': (
                'get_evaluation_data',
                'get_recommendation_data'
            )
        })
    )

    def get_user_info(self, obj):
        return f"{obj.user.user.get_full_name()} ({obj.user.user.username})"
    get_user_info.short_description = "Usuario"

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

    def get_status_color(self, obj):
        status = obj.get_status()
        colors = {
            'verde': '#28a745',
            'amarillo': '#ffc107',
            'rojo': '#dc3545',
            'gris': '#6c757d'
        }
        return format_html(
            '<span style="color: {};">●</span> {}',
            colors.get(status['recommendation_status'], '#6c757d'),
            status['recommendation_status'].capitalize()
        )
    get_status_color.short_description = "Estado de Recomendación"

    change_form_template = 'admin/healthcategory/change_form.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/update-recommendation/',
                self.admin_site.admin_view(self.update_recommendation_view),
                name='update-recommendation',
            ),
        ]
        return custom_urls + urls

    def update_recommendation_view(self, request, object_id):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                health_category = self.get_object(request, object_id)
                
                health_category.update({
                    'professional_recommendations': data.get('text'),
                    'status_color': data.get('status_color', 'gris'),
                    'is_draft': data.get('is_draft', True),
                    'updated_by': request.user.username
                })
                
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:
            extra_context['evaluation_data'] = obj.get_evaluation_data()
            extra_context['recommendation_data'] = obj.get_recommendation_data()
        return super().change_view(request, object_id, form_url, extra_context)

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





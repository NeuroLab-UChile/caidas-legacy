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

from .models import (
  TextRecomendation,
  Profile,
  CategoryTemplate,
  HealthCategory
)

# Define an inline admin descriptor for Profile model
class ProfileInline(admin.StackedInline):
  model = Profile
  can_delete = False
  verbose_name_plural = 'Profiles'
  fk_name = 'user'

# Add HealthCategory inline to show categories in user admin
class HealthCategoryInline(admin.TabularInline):
  model = HealthCategory
  extra = 0  # Don't show empty forms
  readonly_fields = ['template']  # Make them read-only
  can_delete = True
  verbose_name_plural = 'Health Categories'

# Extend the existing UserAdmin
class UserAdmin(BaseUserAdmin):
  inlines = [ProfileInline, HealthCategoryInline]  # Add HealthCategoryInline
  list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')
  list_filter = ('is_staff', 'is_superuser', 'is_active')

  def get_inline_instances(self, request, obj=None):
    if not obj:
      return list()
    return super(UserAdmin, self).get_inline_instances(request, obj)


@admin.register(CategoryTemplate)
class CategoryTemplateAdmin(admin.ModelAdmin):
  list_display = ('name', 'formatted_description', 'is_active')
  search_fields = ('name', 'description')
  list_filter = ('is_active',)
  readonly_fields = ('formatted_evaluation_form',)
  ordering = ('name',)
  change_form_template = "admin/categorytemplate/change_activity_form.html"
  
  class Media:
    css = {
      'all': ('css/output.css',)
    }
    js = ('js/tailwind.config.js',)

  def formatted_evaluation_form(self, obj):
    """Muestra el evaluation_form formateado"""
    if obj.evaluation_form:
      return format_html('<pre>{}</pre>', json.dumps(obj.evaluation_form, indent=2))
    return '-'
  formatted_evaluation_form.short_description = 'Formulario de Evaluación'

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

@admin.register(HealthCategory)
class HealthCategoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'template', 'completion_date', 'get_responses_status', 'status_color')
    list_filter = ('template', 'user', 'completion_date', 'status_color')
    search_fields = ('user__username', 'user__email', 'template__name')
    readonly_fields = ('completion_date', 'get_formatted_responses')
    raw_id_fields = ('user',)
    
    COLOR_CHOICES = [
        ('green', '🟢 Verde - Saludable'),
        ('yellow', '🟡 Amarillo - Precaución'),
        ('red', '🔴 Rojo - Atención Requerida'),
    ]
    
    def get_responses_status(self, obj):
        if obj.responses:
            return '✅ Completado'
        return '❌ Pendiente'
    get_responses_status.short_description = 'Estado'

    def get_formatted_responses(self, obj):
        if obj.responses:
            return format_html('<pre>{}</pre>', json.dumps(obj.responses, indent=2))
        return '-'
    get_formatted_responses.short_description = 'Respuestas'

    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'template')
        }),
        ('Evaluación', {
            'fields': ('completion_date', 'get_formatted_responses'),
            'classes': ('collapse',),
            'description': 'Detalles de la evaluación completada'
        }),
        ('Diagnóstico y Recomendaciones', {
            'fields': ('status_color', 'doctor_recommendations'),
            'description': 'Evaluación del doctor y recomendaciones'
        }),
    )

    class Media:
        css = {
            'all': ('css/output.css',)
        }

admin.site.register(TextRecomendation)


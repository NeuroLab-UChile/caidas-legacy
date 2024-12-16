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

  def formatted_evaluation_form(self, obj):
    """Muestra el evaluation_form formateado"""
    if obj.evaluation_form:
      return format_html('<pre>{}</pre>', json.dumps(obj.evaluation_form, indent=2))
    return '-'
  formatted_evaluation_form.short_description = 'Formulario de Evaluación'

  def response_change(self, request, obj):
    if "_add_node" in request.POST:
      try:
        node_data = {
          'type': request.POST.get('questionType'),
          'question': request.POST.get('questionText'),
        }

        # Add options for choice questions
        if node_data['type'] in ['SINGLE_CHOICE_QUESTION', 'MULTIPLE_CHOICE_QUESTION']:
          options = json.loads(request.POST.get('options', '[]'))
          if not options:
            self.message_user(request, "Debe agregar al menos una opción", level='ERROR')
            return self.response_post_save_change(request, obj)
          node_data['options'] = options

        # Add scale parameters
        if node_data['type'] == 'SCALE_QUESTION':
          min_value = request.POST.get('minValue')
          max_value = request.POST.get('maxValue')
          step = request.POST.get('stepValue')
          
          if not all([min_value, max_value, step]):
            self.message_user(request, "Todos los campos de escala son requeridos", level='ERROR')
            return self.response_post_save_change(request, obj)
            
          node_data.update({
            'min_value': int(min_value),
            'max_value': int(max_value),
            'step': int(step)
          })

        obj.add_activity_node(node_data)
        self.message_user(request, "Pregunta agregada exitosamente")
        
      except Exception as e:
        self.message_user(request, f"Error al guardar la pregunta: {str(e)}", level='ERROR')
        
      return self.response_post_save_change(request, obj)
    
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

admin.site.register(HealthCategory)
admin.site.register(TextRecomendation)


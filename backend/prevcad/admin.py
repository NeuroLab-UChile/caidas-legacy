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

from .models import (
  TextRecomendation,
  Profile,
  CategoryTemplate,
  HealthCategory,
  ActivityNode,
  ActivityNodeDescription
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
      'fields': ('evaluation_form_display', 'evaluation_form'),
      'description': 'Configure las preguntas del formulario de evaluación.'
    }),
    ('Configuración Avanzada', {
      'classes': ('collapse',),
      'fields': ('training_nodes', 'root_node'),
    }),
  )
  readonly_fields = ('evaluation_form_display',)

  def preview_icon(self, obj):
    if obj.icon:
      return format_html('<img src="{}" style="height: 30px; width: auto;"/>', obj.icon.url)
    return "Sin ícono"
  preview_icon.short_description = 'Ícono'

  def description_preview(self, obj):
    return Truncator(obj.description).chars(50)
  description_preview.short_description = 'Descripción'

  def evaluation_form_display(self, obj):
    if not obj.evaluation_form:
      return "No hay formulario configurado"
    
    try:
      questions = obj.evaluation_form.get('question_nodes', [])
      html = ['<div class="evaluation-form-preview">']
      
      for i, q in enumerate(questions, 1):
        q_type = q.get('type', '')
        question = q.get('data', {}).get('question', '')
        options = q.get('data', {}).get('options', [])
        
        html.append(f'<div class="question-item">')
        html.append(f'<div class="question-number">Pregunta {i}</div>')
        html.append(f'<div class="question-type">{q_type}</div>')
        html.append(f'<div class="question-text">{question}</div>')
        
        if options:
          html.append('<div class="question-options">')
          for opt in options:
            html.append(f'<div class="option-item">• {opt}</div>')
          html.append('</div>')
        
        html.append('</div>')
      
      html.append('</div>')
      return mark_safe(''.join(html))
      
    except Exception as e:
      return f"Error al mostrar el formulario: {str(e)}"
  
  evaluation_form_display.short_description = 'Vista Previa del Formulario'

  class Media:
    css = {
      'all': ('admin/css/custom_admin.css',)
    }
    js = ('admin/js/custom_admin.js',)

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

class HealthCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'user_info', 
        'template_info', 
        'status_badge', 
        'completion_status',
        'date_display'
    )
    list_filter = (
        HealthStatusFilter, 
        'template',
        ('user', admin.RelatedOnlyFieldListFilter),
        'completion_date'
    )
    search_fields = ('user__username', 'template__name')
    
    fieldsets = (
        ('Principal', {
            'fields': (
                'user',
                'template',
                'status_color',
            )
        }),
        ('Detalles', {
            'classes': ('collapse',),
            'fields': (
                'doctor_recommendations',
                'responses',
                'completion_date',
            )
        }),
    )

    def user_info(self, obj):
        return format_html(
            '<div class="flex-cell" style="min-width:100px; flex: 1;">'
            '<strong>{}</strong>'
            '</div>',
            obj.user.username
        )
    user_info.short_description = 'Usuario'

    def template_info(self, obj):
        if obj.template:
            return format_html(
                '<div class="flex-cell" style="min-width:120px; flex: 1.5;">'
                '<strong>{}</strong><br/>'
                '<small style="color: #666">{}</small>'
                '</div>',
                obj.template.name,
                Truncator(obj.template.description).chars(25)
            )
    template_info.short_description = 'Categoría'

    def status_badge(self, obj):
        colors = {
            'green': ('#28a745', '✓'),
            'yellow': ('#ffc107', '!'),
            'red': ('#dc3545', '×'),
        }
        if obj.status_color:
            color, symbol = colors.get(obj.status_color, ('#6c757d', '-'))
            return format_html(
                '<div class="flex-cell" style="flex: 0.5; text-align: center;">'
                '<span style="'
                'background-color: {};'
                'color: white;'
                'padding: 1px 6px;'
                'border-radius: 10px;'
                'display: inline-block;'
                '">{}</span>'
                '</div>',
                color, symbol
            )
        return '-'
    status_badge.short_description = 'Estado'

    def completion_status(self, obj):
        return format_html(
            '<div class="flex-cell" style="flex: 0.5; text-align: center;">'
            '<span style="color: {}">{}</span>'
            '</div>',
            '#28a745' if obj.completion_date else '#dc3545',
            '✓' if obj.completion_date else '×'
        )
    completion_status.short_description = 'Completado'

    def date_display(self, obj):
        if obj.completion_date:
            return format_html(
                '<div class="flex-cell" style="flex: 1; text-align: right;">'
                '<small style="color: #666">{}</small>'
                '</div>',
                obj.completion_date.strftime('%d/%m/%Y')
            )
        return ''
    date_display.short_description = 'Fecha'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

admin.site.register(HealthCategory, HealthCategoryAdmin)
admin.site.register(TextRecomendation)


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
    list_display = ('name', 'evaluation_type', 'is_active')
    list_filter = ('is_active', 'evaluation_type')
    search_fields = ('name', 'description')

    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'icon', 'is_active')
        }),
        ('Configuración de Evaluación', {
            'fields': ('evaluation_type', 'evaluation_form', 'default_recommendations')
        }),
        ('Configuración de Entrenamiento', {
            'fields': ('training_form', 'root_node')
        }),
    )


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
        'recommendations',
    ]
    ordering = ['-completion_date']
    list_per_page = 20
    readonly_fields = [
        'template',
        'completion_date',
        'get_user_info',
        'get_template_name',
        'get_status_color',
        'get_completion_status',
        'is_draft',
        'recommendations_field_group',
        'get_detailed_responses',
    ]
    fieldsets = (
        ('Información del Paciente', {
            'fields': ('get_user_info', 'get_template_name'),
            'classes': ('wide',),
        }),
        ('Estado y Fechas', {
            'fields': ('get_completion_status', 'completion_date'),
        }),
        ('Recomendaciones Médicas', {
            'fields': (
                'use_default_recommendations',
                'recommendations_field_group',
            ),
            'description': 'Estado y color de las recomendaciones médicas.',
            'classes': ('wide',),
        }),
        ('Respuestas del Paciente', {
            'fields': ('get_detailed_responses',),
            'classes': ('collapse',),
            'description': 'Historial completo de respuestas del paciente.',
        })
    )
    change_form_template = 'admin/healthcategory/change_form.html'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = (
            'admin/js/jquery.init.js',
            'admin/js/healthcategory.js',
        )

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
            'gris': '#6c757d',
        }
        if obj.status_color:
            return format_html(
                '<span style="color: {}; font-weight: bold;">●</span> {}',
                color_map.get(obj.status_color, '#6c757d'),
                obj.get_status_color_display()
            )
        return "Sin asignar"
    get_status_color.short_description = 'Color de riesgo'

    def get_detailed_responses(self, obj):
        from django.template.loader import render_to_string

        responses = obj.responses or {}
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

    def save_model(self, request, obj, form, change):
        if 'use_default_recommendations' in form.changed_data:
            if obj.use_default_recommendations:
                if obj.template and obj.template.default_recommendations:
                    obj.recommendations = obj.template.default_recommendations
                    messages.info(request, "Se han restaurado las recomendaciones por defecto del template")
            else:
                messages.info(request, "Ahora puede personalizar las recomendaciones")

        if not obj.use_default_recommendations:
            if 'recommendations' in request.POST:
                obj.recommendations = request.POST['recommendations']
            if 'status_color' in request.POST:
                obj.status_color = request.POST['status_color']

        super().save_model(request, obj, form, change)

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

        obj.is_draft = False
        obj.recommendations_updated_by = request.user.get_full_name() or request.user.username
        obj.recommendations_updated_at = timezone.now()
        obj.save()

        self.message_user(
            request,
            "✓ Las recomendaciones han sido firmadas y son visibles para el paciente.",
            level=messages.SUCCESS
        )
        return super().response_change(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if 'recommendations' in form.base_fields:
            form.base_fields['recommendations'].help_text = (
                "Las recomendaciones serán visibles para el paciente cuando se guarden sin marcar como borrador."
            )
            form.base_fields['recommendations'].widget = forms.Textarea(attrs={
                'rows': 4,
                'class': 'vLargeTextField',
                'placeholder': 'Ingrese las recomendaciones personalizadas'
            })

        if 'use_default_recommendations' in form.base_fields:
            form.base_fields['use_default_recommendations'].help_text = (
                "Marque esta casilla para usar las recomendaciones predeterminadas del template"
            )

        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Información del Paciente', {
                'fields': ('get_user_info', 'get_template_name'),
                'classes': ('wide',),
            }),
            ('Estado y Fechas', {
                'fields': ('get_completion_status', 'completion_date'),
            }),
            ('Recomendaciones Médicas', {
                'fields': (
                    'use_default_recommendations',
                    'recommendations_field_group',
                ),
                'description': 'Estado y color de las recomendaciones médicas.',
                'classes': ('wide',),
            }),
        ]

        # Add response fields based on evaluation type
        if obj and obj.template:
            if obj.template.evaluation_type == 'SELF':
                fieldsets.append(
                    ('Respuestas de Autoevaluación', {
                        'fields': ('get_detailed_responses',),
                        'classes': ('collapse',),
                        'description': 'Historial completo de respuestas de autoevaluación.',
                    })
                )
            elif obj.template.evaluation_type == 'PROFESSIONAL':
                fieldsets.append(
                    ('Evaluación Profesional', {
                        'fields': ('professional_evaluation_results',),
                        'classes': ('collapse',),
                        'description': 'Respuestas de la evaluación profesional.',
                    })
                )
            elif obj.template.evaluation_type == 'BOTH':
                fieldsets.extend([
                    ('Respuestas de Autoevaluación', {
                        'fields': ('get_detailed_responses',),
                        'classes': ('collapse',),
                        'description': 'Historial completo de respuestas de autoevaluación.',
                    }),
                    ('Evaluación Profesional', {
                        'fields': ('professional_evaluation_results',),
                        'classes': ('collapse',),
                        'description': 'Respuestas de la evaluación profesional.',
                    })
                ])

        return fieldsets

    def recommendations_field_group(self, obj):
        """Muestra las recomendaciones según el tipo seleccionado."""
        if obj and obj.use_default_recommendations:
            # Mostrar las recomendaciones por defecto del template
            default_recs = obj.template.default_recommendations if obj.template else {}
            field_html = """
            <div style="margin: 10px 0;">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold; margin-bottom: 5px;">
                        Recomendaciones por defecto del template:
                    </label>
                    <div style="padding: 10px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;">
                        <pre style="margin: 0; white-space: pre-wrap;">{default_recs}</pre>
                    </div>
                </div>
                <button type="submit" name="_save_default_recs" style="padding: 6px 12px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Guardar
                </button>
            </div>
            """
            return mark_safe(field_html.format(
                default_recs=json.dumps(default_recs, indent=2) if default_recs else "No hay recomendaciones por defecto"
            ))
        else:
            # Mostrar el formulario para recomendaciones personalizadas
            field_html = """
            <div style="margin: 10px 0;">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold; margin-bottom: 5px;">Recomendaciones:</label>
                    <textarea 
                        name="recommendations" 
                        rows="4" 
                        style="width: 90%; padding: 8px; border: 1px solid #ccc; border-radius: 4px;"
                    >{recommendations}</textarea>
                </div>
                <div>
                    <label style="display: block; font-weight: bold; margin-bottom: 5px;">Color de estado:</label>
                    <select 
                        name="status_color" 
                        style="width: 200px; padding: 6px; border: 1px solid #ccc; border-radius: 4px;"
                    >
                        <option value="">---------</option>
                        <option value="verde" {verde_selected}>Verde</option>
                        <option value="amarillo" {amarillo_selected}>Amarillo</option>
                        <option value="rojo" {rojo_selected}>Rojo</option>
                        <option value="gris" {gris_selected}>Gris</option>
                    </select>
                </div>
            </div>
            """
            recommendations = obj.recommendations if obj and obj.recommendations else ""
            status_color = obj.status_color if obj and obj.status_color else ""
            
            return mark_safe(field_html.format(
                recommendations=recommendations,
                verde_selected="selected" if status_color == "verde" else "",
                amarillo_selected="selected" if status_color == "amarillo" else "",
                rojo_selected="selected" if status_color == "rojo" else "",
                gris_selected="selected" if status_color == "gris" else "",
            ))

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





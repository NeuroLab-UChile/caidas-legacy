from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.urls import path
import json
from ..models import HealthCategory, Recommendation
from .filters import HealthStatusFilter
from django.utils import timezone

class RecommendationInline(admin.StackedInline):
    model = Recommendation
    can_delete = False
    max_num = 1
    min_num = 1
    verbose_name = "Recomendación"
    verbose_name_plural = "Recomendación"

    fields = ('text', 'status_color', 'is_draft', 'is_signed')
    readonly_fields = ('updated_by', 'updated_at', 'signed_by', 'signed_at')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            # Obtener los valores por defecto del template
            default_recommendations = obj.template.default_recommendations or {}
            formset.form.base_fields['text'].initial = default_recommendations.get('text', '')
            formset.form.base_fields['status_color'].initial = default_recommendations.get('status_color', 'gris')
        return formset

@admin.register(HealthCategory)
class HealthCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'get_user_info',
        'get_template_name',
        'get_completion_status',
        'get_completion_date',
        'get_recommendation_status'
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
        'get_detailed_responses',
        'get_recommendation_editor'
    ]

    fieldsets = (
        ('Información del Usuario', {
            'fields': (
                'get_user_info',
                'get_template_name',
            )
        }),
        ('Estado', {
            'fields': (
                'get_completion_status',
                'get_completion_date',
            )
        }),
        ('Recomendación', {
            'fields': (
                'get_recommendation_editor',
            ),
            'classes': ('wide',)
        }),
        ('Datos de Evaluación', {
            'fields': (
                'get_detailed_responses',
            )
        })
    )

    change_form_template = 'admin/healthcategory/change_form.html'

    inlines = [RecommendationInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.editors.filter(user=request.user).exists():
            return []
        return self.readonly_fields

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
                recommendation = health_category.get_or_create_recommendation()
                
                recommendation.use_default = data.get('use_default', False)
                recommendation.status_color = data.get('status_color', 'gris')
                
                if not recommendation.use_default:
                    recommendation.text = data.get('text', '')
                else:
                    # Usar el texto por defecto según el estado
                    status_map = {
                        'verde': 'no_risk',
                        'amarillo': 'prev_risk',
                        'rojo': 'risk'
                    }
                    default_recommendations = health_category.template.default_recommendations or {}
                    status_key = status_map.get(recommendation.status_color)
                    recommendation.text = default_recommendations.get(status_key, '')

                recommendation.is_draft = data.get('is_draft', True)
                if data.get('is_signed'):
                    recommendation.is_signed = True
                    recommendation.signed_by = request.user.username
                    recommendation.signed_at = timezone.now()
                
                recommendation.updated_by = request.user.username
                recommendation.save()
                
                return JsonResponse({
                    'status': 'success',
                    'recommendation': {
                        'text': recommendation.text,
                        'status_color': recommendation.status_color,
                        'use_default': recommendation.use_default,
                        'is_draft': recommendation.is_draft,
                        'is_signed': recommendation.is_signed,
                        'signed_by': recommendation.signed_by,
                        'signed_at': recommendation.signed_at.isoformat() if recommendation.signed_at else None,
                        'updated_by': recommendation.updated_by,
                        'updated_at': recommendation.updated_at.isoformat()
                    }
                })
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    def get_user_info(self, obj):
        return f"{obj.user.user.get_full_name()} {obj.user.user.username}"
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

    def get_recommendation_status(self, obj):
        try:
            recommendation = obj.recommendation
            status_colors = {
                'verde': ('bg-green-100 text-green-800', '●'),
                'amarillo': ('bg-yellow-100 text-yellow-800', '●'),
                'rojo': ('bg-red-100 text-red-800', '●'),
                'gris': ('bg-gray-100 text-gray-600', '●')
            }
            color_class, dot = status_colors.get(recommendation.status_color, status_colors['gris'])
            
            # Mostrar estado de publicación y firma
            status_text = []
            if recommendation.is_draft:
                status_text.append("Borrador")
            else:
                status_text.append("Publicado")
                if recommendation.is_signed:
                    status_text.append("Firmado")
            
            return format_html(
                '<div class="flex flex-col gap-2">'
                '<span class="{} px-2 py-1 rounded-full text-xs font-medium">'
                '{} {}</span>'
                '<span class="text-xs text-gray-500">{}</span>'
                '</div>',
                color_class,
                dot,
                recommendation.status_color.capitalize(),
                ' • '.join(status_text)
            )
        except:
            return format_html(
                '<span class="text-xs text-gray-500">Sin recomendación</span>'
            )
    get_recommendation_status.short_description = "Estado de Recomendación"

    def get_detailed_responses(self, obj):
        responses = obj.evaluation_form.responses or {}
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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:
            recommendation = obj.get_or_create_recommendation()
            extra_context['recommendation_data'] = {
                'text': recommendation.text,
                'status_color': recommendation.status_color,
                'is_draft': recommendation.is_draft,
                'is_signed': recommendation.is_signed,
                'signed_by': recommendation.signed_by,
                'signed_at': recommendation.signed_at,
                'updated_by': recommendation.updated_by,
                'updated_at': recommendation.updated_at,
                'default_text': recommendation.default_text,
                'default_status_color': recommendation.default_status_color
            }
        return super().change_view(request, object_id, form_url, extra_context)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Recommendation):
                instance.updated_by = request.user.username
                if not instance.is_draft and instance.is_signed:
                    instance.signed_by = request.user.username
                    instance.signed_at = timezone.now()
            instance.save()
        formset.save_m2m() 

    def get_recommendation_editor(self, obj):
        recommendation = obj.get_or_create_recommendation()
        context = {
            'recommendation': recommendation,
            'health_category': obj,
            'default_recommendations': obj.template.default_recommendations or {},
        }
        return mark_safe(render_to_string(
            'admin/healthcategory/recommendation_editor.html',
            context
        ))
    get_recommendation_editor.short_description = "Editor de Recomendación"

    class Media:
        css = {
            'all': (
                'https://cdn.tailwindcss.com',
                'admin/css/forms.css',
            )
        }
        js = (
            'admin/js/recommendation_editor.js',
        ) 
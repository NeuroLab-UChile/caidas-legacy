from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.urls import path
import json
from ..models import HealthCategory
from .filters import HealthStatusFilter

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
        'get_detailed_responses',
        'get_recommendation_data'
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
                'get_is_draft',
                'get_status_color'
            )
        }),
        ('Datos de Evaluación', {
            'fields': (
                'get_detailed_responses',
                'get_recommendation_data'
            )
        })
    )

    change_form_template = 'admin/healthcategory/change_form.html'

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
            extra_context['recommendation_data'] = obj.get_recommendation_data()
        return super().change_view(request, object_id, form_url, extra_context) 
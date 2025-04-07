from django.contrib import admin
from django.utils.html import format_html
from ..models import TextRecomendation

@admin.register(TextRecomendation)
class TextRecomendationAdmin(admin.ModelAdmin):
    list_display = [
        'theme',
        'category',
        'sub_category',
        'preview_learn',
        'preview_remember',
        'preview_data',
    ]
    
    list_filter = ['theme', 'category', 'sub_category']
    search_fields = ['theme', 'category', 'sub_category', 'keywords']
    
    fieldsets = [
        ('Clasificación', {
            'fields': ['theme', 'category', 'sub_category']
        }),
        ('Contenido Principal', {
            'fields': ['learn', 'remember']
        }),
        ('Datos Adicionales', {
            'fields': ['data', 'practic_data', 'context_explanation']
        }),
        ('Referencias', {
            'fields': ['quote_link', 'keywords']
        }),
    ]

    def preview_learn(self, obj):
        return self._get_preview(obj.learn, "¿Sabía qué?")
    preview_learn.short_description = '¿Sabía qué?'

    def preview_remember(self, obj):
        return self._get_preview(obj.remember, "¡Recuerda!")
    preview_remember.short_description = '¡Recuerda!'

    def preview_data(self, obj):
        return self._get_preview(obj.data, "Datos")
    preview_data.short_description = 'Datos'

    def _get_preview(self, text, field_name):
        if not text:
            return format_html(
                '<span style="color: #666; font-style: italic;">Sin {}</span>',
                field_name
            )
        preview = text[:100] + ('...' if len(text) > 100 else '')
        return format_html(
            '<div style="max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'
            '{}</div>',
            preview
        )

    class Media:
        css = {
            'all': ('admin/css/text_recommendation.css',)
        } 
from django import template

register = template.Library()

@register.filter
def get_recommendation(default_recommendations, status_color):
    status_map = {
        'verde': 'no_risk',
        'amarillo': 'prev_risk',
        'rojo': 'risk',
        'gris': 'pending'
    }
    status = status_map.get(status_color)
    if status and isinstance(default_recommendations, dict):
        return default_recommendations.get(status, '')
    return ''

@register.simple_tag
def get_recommendation_video(recommendation):
    """Retorna la URL del video de la recomendación si existe"""
    if recommendation and recommendation.video_url:
        return recommendation.video_url
    return None 
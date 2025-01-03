from django import template

register = template.Library()

@register.filter
def get_recommendation(default_recommendations, status_color):
    status_map = {
        'verde': 'no_risk',
        'amarillo': 'prev_risk',
        'rojo': 'risk'
    }
    status = status_map.get(status_color)
    if status and isinstance(default_recommendations, dict):
        return default_recommendations.get(status, '')
    return '' 
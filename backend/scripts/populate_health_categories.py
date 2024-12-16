import os
import django
import json

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from prevcad.models import CategoryTemplate

def populate_category_templates(data):
    for template_info in data:
        template, created = CategoryTemplate.objects.update_or_create(
            name=template_info['name'],
            defaults={
                'description': template_info['description'],
                'is_active': True,
                'evaluation_form': template_info['evaluation_form'],
                'training_nodes': template_info['training_nodes']
            }
        )
        
        if created:
            print(f"Creado template: {template.name}")
        else:
            print(f"Actualizado template: {template.name}")

# Datos de ejemplo con descripciones mejoradas
template_data = [
    {
        "name": "Riesgo Domiciliario",
        "description": "Identifique y prevenga los riesgos más comunes en el hogar, como caídas o problemas estructurales, a través de preguntas sobre su entorno y recomendaciones personalizadas.",
        "evaluation_form": {
            "question_nodes": [
                {"id": 1, "type": "SINGLE_CHOICE_QUESTION", "data": {"question": "¿En qué tipo de vivienda reside actualmente?", "options": ["Casa", "Departamento", "Otro"]}},
                {"id": 2, "type": "TEXT_QUESTION", "data": {"question": "Describa brevemente cualquier problema de seguridad que haya notado en su hogar."}},
                {"id": 3, "type": "SCALE_QUESTION", "data": {"question": "¿Qué tan seguro considera su hogar en una escala del 1 al 10?", "min_value": 1, "max_value": 10, "step": 1}}
            ]
        },
        "training_nodes": [
            {"id": 1, "type": "DESCRIPTION_NODE", "title": "Introducción a la Seguridad", "description": "Aprenda cómo identificar y minimizar los riesgos más comunes en el hogar.", "media_url": "/assets/training/home-safety.jpg"},
            {"id": 2, "type": "VIDEO_NODE", "title": "Prevención de Caídas", "description": "Consejos visuales para evitar caídas y accidentes frecuentes en el hogar.", "media_url": "/assets/training/fall-prevention.mp4"}
        ]
    },
    {
        "name": "Controles de Salud",
        "description": "La salud preventiva es clave para el bienestar. Aquí podrá analizar la frecuencia de sus chequeos médicos y conocer mejores prácticas de prevención.",
        "evaluation_form": {
            "question_nodes": [
                {"id": 1, "type": "SINGLE_CHOICE_QUESTION", "data": {"question": "¿Cuándo fue su último chequeo médico general?", "options": ["Último mes", "Hace 6 meses", "Hace más de 1 año"]}},
                {"id": 2, "type": "TEXT_QUESTION", "data": {"question": "Describa algún síntoma reciente que haya experimentado."}},
                {"id": 3, "type": "SCALE_QUESTION", "data": {"question": "¿Qué tan saludable se siente actualmente en una escala del 1 al 10?", "min_value": 1, "max_value": 10, "step": 1}}
            ]
        },
        "training_nodes": [
            {"id": 1, "type": "VIDEO_NODE", "title": "Importancia de los Chequeos Médicos", "description": "Por qué los controles periódicos son esenciales para su salud.", "media_url": "/assets/training/health-check.mp4"},
            {"id": 2, "type": "DESCRIPTION_NODE", "title": "Síntomas Comunes a Vigilar", "description": "Identifique los síntomas comunes y cuándo buscar ayuda profesional.", "media_url": "/assets/training/symptoms.jpg"}
        ]
    },
    {
        "name": "Actividad Física",
        "description": "Descubra la importancia de mantenerse activo y cómo adaptar rutinas de ejercicio a su estilo de vida para mejorar su salud y bienestar.",
        "evaluation_form": {
            "question_nodes": [
                {"id": 1, "type": "SINGLE_CHOICE_QUESTION", "data": {"question": "¿Realiza actividad física regularmente?", "options": ["Diario", "3-5 veces a la semana", "1-2 veces a la semana", "No realizo"]}},
                {"id": 2, "type": "TEXT_QUESTION", "data": {"question": "¿Qué actividad física le gustaría realizar si tuviera más tiempo?"}},
                {"id": 3, "type": "SCALE_QUESTION", "data": {"question": "En una escala del 1 al 5, ¿qué tan difícil le resulta realizar actividad física?", "min_value": 1, "max_value": 5, "step": 1}}
            ]
        },
        "training_nodes": [
            {"id": 1, "type": "VIDEO_NODE", "title": "Rutinas Básicas de Ejercicio", "description": "Videos con ejercicios simples que puede realizar en casa.", "media_url": "/assets/training/exercise-routine.mp4"},
            {"id": 2, "type": "IMAGE_NODE", "title": "Ejemplos de Actividades", "description": "Imágenes ilustrativas de ejercicios seguros y efectivos.", "media_url": "/assets/training/exercise-example.jpg"}
        ]
    }
]

if __name__ == '__main__':
    populate_category_templates(template_data)

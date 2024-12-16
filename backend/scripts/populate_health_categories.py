import os
import django
import json

# Configura el entorno de Django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from prevcad.models import CategoryTemplate

def crear_category_template(data):
    template, created = CategoryTemplate.objects.get_or_create(
        name=data['name'],
        defaults={
            'description': data['description'],
            'is_active': True,
            'evaluation_form': {
                'question_nodes': data['question_nodes']
            },
            'training_nodes': data.get('training_nodes', [])
        }
    )
    
    if created:
        print(f"Creado template: {template.name}")
    else:
        print(f"Template ya existe: {template.name}")
    
    return template

# Datos de ejemplo
template_data = {
    'name': 'Riesgo Domiciliario',
    'description': 'Evaluación de riesgos en el hogar para prevenir caídas y accidentes domésticos',
    'question_nodes': [
        {
            'id': 1,
            'type': 'SINGLE_CHOICE_QUESTION',
            'data': {
                'question': '¿En qué tipo de vivienda reside actualmente?',
                'options': ['Casa', 'Departamento', 'Otro']
            }
        },
        {
            'id': 2,
            'type': 'MULTIPLE_CHOICE_QUESTION',
            'data': {
                'question': 'Seleccione los espacios que más utiliza en su día a día:',
                'options': [
                    'Cocina',
                    'Living-comedor',
                    'Habitación',
                    'Baño',
                    'Escalera',
                    'Pasillo',
                    'Exterior'
                ]
            }
        },
        {
            'id': 3,
            'type': 'SINGLE_CHOICE_QUESTION',
            'data': {
                'question': '¿Tiene barandillas en las escaleras?',
                'options': ['Sí', 'No', 'No hay escaleras']
            }
        },
        {
            'id': 4,
            'type': 'MULTIPLE_CHOICE_QUESTION',
            'data': {
                'question': '¿Qué elementos de seguridad tiene en su baño?',
                'options': [
                    'Barras de apoyo en la ducha',
                    'Barras de apoyo cerca del inodoro',
                    'Alfombra antideslizante',
                    'Piso antideslizante',
                    'Ninguno'
                ]
            }
        },
        {
            'id': 5,
            'type': 'SINGLE_CHOICE_QUESTION',
            'data': {
                'question': '¿Cómo es la iluminación en los pasillos y escaleras?',
                'options': [
                    'Muy buena - Siempre bien iluminado',
                    'Regular - Algunas zonas oscuras',
                    'Mala - Poca iluminación general'
                ]
            }
        }
    ],
    'training_nodes': [
        {
            'id': 1,
            'type': 'DESCRIPTION_NODE',
            'title': 'Introducción a la Seguridad en el Hogar',
            'description': 'La seguridad en el hogar es fundamental para prevenir accidentes. En esta sección aprenderemos sobre los principales riesgos y cómo prevenirlos.',
            'media_url': '/assets/training/home-safety-intro.jpg'
        },
        {
            'id': 2,
            'type': 'VIDEO_NODE',
            'title': 'Prevención de Caídas',
            'description': 'Las caídas son uno de los accidentes más comunes en el hogar. Aprenda cómo prevenirlas con estos consejos prácticos.',
            'media_url': '/assets/training/fall-prevention.mp4'
        },
        {
            'id': 3,
            'type': 'DESCRIPTION_NODE',
            'title': 'Seguridad en el Baño',
            'description': 'El baño puede ser uno de los lugares más peligrosos de la casa. Aprenda cómo hacer este espacio más seguro.',
            'media_url': '/assets/training/bathroom-safety.jpg'
        },
        {
            'id': 4,
            'type': 'IMAGE_NODE',
            'title': 'Iluminación Adecuada',
            'description': 'Una buena iluminación es esencial para prevenir accidentes. Vea ejemplos de una iluminación correcta en diferentes áreas del hogar.',
            'media_url': '/assets/training/proper-lighting.jpg'
        },
        {
            'id': 5,
            'type': 'DESCRIPTION_NODE',
            'title': 'Organización y Orden',
            'description': 'Mantener su hogar ordenado y libre de obstáculos es fundamental para prevenir accidentes. Aprenda técnicas prácticas de organización.',
            'media_url': '/assets/training/home-organization.jpg'
        }
    ]
}

if __name__ == '__main__':
    crear_category_template(template_data)

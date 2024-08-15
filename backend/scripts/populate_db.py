import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from prevcad.models import HealthCategory, WorkRecommendation, EvaluationRecommendation, TextRecomendation

# Datos con campos adicionales inventados para cada categoría y recomendación
health_category_data = [
    {
        'health_category': {
            'name': 'Historia de caídas',
            'icon': 'fall_history.png',
            'image': 'fall_history.jpg',
            'description': 'Categoría de salud para historial de caídas'
        },
        'work_recommendation': {
            'work_specific_field': 'Supervisar las áreas donde es más probable que ocurran caídas',
            'frequency': 'Diaria'
        },
        'evaluation_recommendation': {
            'evaluation_specific_field': 'Evaluar el equilibrio y la movilidad del paciente',
            'tools': 'Test de Tinetti'
        }
    },
    {
        'health_category': {
            'name': 'Actividad física',
            'icon': 'physical_activity.png',
            'image': 'physical_activity.jpg',
            'description': 'Categoría de salud para actividad física'
        },
        'work_recommendation': {
            'work_specific_field': 'Promover la actividad física regular',
            'frequency': 'Semanal'
        },
        'evaluation_recommendation': {
            'evaluation_specific_field': 'Medir la capacidad aeróbica y la fuerza muscular',
            'tools': 'Test de resistencia'
        }
    },
    {
        'health_category': {
            'name': 'Alimentación saludable',
            'icon': 'healthy_eating.png',
            'image': 'healthy_eating.jpg',
            'description': 'Categoría de salud para alimentación saludable'
        },
        'work_recommendation': {
            'work_specific_field': 'Promover una dieta equilibrada',
            'frequency': 'Mensual'
        },
        'evaluation_recommendation': {
            'evaluation_specific_field': 'Evaluar el índice de masa corporal (IMC)',
            'tools': 'Cálculo del IMC'
        }
    },
    {
        'health_category': {
            'name': 'Vestimenta segura',
            'icon': 'safe_clothing.png',
            'image': 'safe_clothing.jpg',
            'description': 'Categoría de salud para vestimenta segura'
        },
        'work_recommendation': {
            'work_specific_field': 'Recomendar ropa adecuada para prevenir accidentes',
            'frequency': 'Cada cambio de estación'
        },
        'evaluation_recommendation': {
            'evaluation_specific_field': 'Evaluar la adecuación de la vestimenta para la seguridad',
            'tools': 'Inspección visual'
        }
    },
    {
        'health_category': {
            'name': 'Riesgo domiciliario',
            'icon': 'home_risk.png',
            'image': 'home_risk.jpg',
            'description': 'Categoría de salud para riesgo domiciliario'
        },
        'work_recommendation': {
            'work_specific_field': 'Identificar riesgos de caídas en el hogar',
            'frequency': 'Semestral'
        },
        'evaluation_recommendation': {
            'evaluation_specific_field': 'Evaluar la seguridad del entorno doméstico',
            'tools': 'Checklist de seguridad'
        }
    },
    {
        'health_category': {
            'name': 'Fármacos',
            'icon': 'medications.png',
            'image': 'medications.jpg',
            'description': 'Categoría de salud para manejo de fármacos'
        },
        'work_recommendation': {
            'work_specific_field': 'Monitorear la adherencia a la medicación',
            'frequency': 'Diaria'
        },
        'evaluation_recommendation': {
            'evaluation_specific_field': 'Evaluar los efectos secundarios de la medicación',
            'tools': 'Revisión de medicamentos'
        }
    },
    {
        'health_category': {
            'name': 'Cognición y ánimo',
            'icon': 'cognition_mood.png',
            'image': 'cognition_mood.jpg',
            'description': 'Categoría de salud para cognición y ánimo'
        },
        'work_recommendation': {
            'work_specific_field': 'Promover actividades cognitivas y sociales',
            'frequency': 'Semanal'
        },
        'evaluation_recommendation': {
            'evaluation_specific_field': 'Evaluar el estado mental y emocional',
            'tools': 'Test de depresión y ansiedad'
        }
    },
    {
        'health_category': {
            'name': 'Valoración sensorial',
            'icon': 'sensory_assessment.png',
            'image': 'sensory_assessment.jpg',
            'description': 'Categoría de salud para valoración sensorial'
        },
        'work_recommendation': {
            'work_specific_field': 'Promover chequeos regulares de los sentidos',
            'frequency': 'Anual'
        },
        'evaluation_recommendation': {
            'evaluation_specific_field': 'Evaluar la vista y la audición',
            'tools': 'Examen visual y auditivo'
        }
    },
    {
        'health_category': {
            'name': 'Estado óseo muscular',
            'icon': 'bone_muscle_health.png',
            'image': 'bone_muscle_health.jpg',
            'description': 'Categoría de salud para estado óseo y muscular'
        },
        'work_recommendation': {
            'work_specific_field': 'Promover ejercicios de fortalecimiento muscular',
            'frequency': 'Semanal'
        },
        'evaluation_recommendation': {
            'evaluation_specific_field': 'Evaluar la densidad ósea y la masa muscular',
            'tools': 'Densitometría ósea y evaluación física'
        }
    }
]

# Poblar la base de datos con las categorías y recomendaciones
for item in health_category_data:
    # Crear la categoría de salud
    health_category = HealthCategory.objects.create(
        name=item['health_category']['name'],
        icon=item['health_category']['icon'],
        image=item['health_category']['image'],
        description=item['health_category']['description']
    )

    # Crear las recomendaciones asociadas
    WorkRecommendation.objects.create(
        name=f"Recomendación laboral para {item['health_category']['name']}",
        image=item['health_category']['image'],
        description=item['health_category']['description'],
        health_category=health_category,


    )
    EvaluationRecommendation.objects.create(
        name=f"Recomendación de evaluación para {item['health_category']['name']}",
        image=item['health_category']['image'],
        description=item['health_category']['description'],
        health_category=health_category,

    )

text_recommendation_data = [
    {
		'title': 'Recomendación de texto 1',
		'inside_text': 'Texto de recomendación 1'
	},
	{
		'title': 'Recomendación de texto 2',
		'inside_text': 'Texto de recomendación 2'
	},
	{
		'title': 'Recomendación de texto 3',
		'inside_text': 'Texto de recomendación 3'
	}
]
for item in text_recommendation_data:
	TextRecomendation.objects.create(
		title=item['title'],
		inside_text=item['inside_text']
	)
      
print("Base de datos poblada correctamente con las categorías de salud y recomendaciones.")

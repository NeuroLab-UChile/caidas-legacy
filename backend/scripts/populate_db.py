import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from prevcad.models import HealthCategory

# Crear categorías de salud basadas en la imagen proporcionada
categories = [
	{'name': 'Historia de caídas', 'icon': 'fall_history.png', 'image': 'fall_history.jpg', 'description': 'Categoría de salud para historial de caídas'},
	{'name': 'Actividad física', 'icon': 'physical_activity.png', 'image': 'physical_activity.jpg', 'description': 'Categoría de salud para actividad física'},
	{'name': 'Alimentación saludable', 'icon': 'healthy_eating.png', 'image': 'healthy_eating.jpg', 'description': 'Categoría de salud para alimentación saludable'},
	{'name': 'Vestimenta segura', 'icon': 'safe_clothing.png', 'image': 'safe_clothing.jpg', 'description': 'Categoría de salud para vestimenta segura'},
	{'name': 'Riesgo domiciliario', 'icon': 'home_risk.png', 'image': 'home_risk.jpg', 'description': 'Categoría de salud para riesgo domiciliario'},
	{'name': 'Fármacos', 'icon': 'medications.png', 'image': 'medications.jpg', 'description': 'Categoría de salud para manejo de fármacos'},
	{'name': 'Cognición y ánimo', 'icon': 'cognition_mood.png', 'image': 'cognition_mood.jpg', 'description': 'Categoría de salud para cognición y ánimo'},
	{'name': 'Valoración sensorial', 'icon': 'sensory_assessment.png', 'image': 'sensory_assessment.jpg', 'description': 'Categoría de salud para valoración sensorial'},
	{'name': 'Estado óseo muscular', 'icon': 'bone_muscle_health.png', 'image': 'bone_muscle_health.jpg', 'description': 'Categoría de salud para estado óseo y muscular'}
]

# Poblar la base de datos con las categorías
for category in categories:
	HealthCategory.objects.create(
		name=category['name'],
		icon=category['icon'],
		image=category['image'],
		description=category['description']
	)

print("Base de datos poblada correctamente con las categorías de salud.")

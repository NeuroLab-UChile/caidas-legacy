# Importar el modelo
import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.contrib.contenttypes.models import ContentType

from prevcad.models import CategoryTemplate



# Importa los modelos
from prevcad.models import CategoryTemplate,ActivityNode, ActivityNodeDescription, TextQuestion, SingleChoiceQuestion, ScaleQuestion, ResultNode

def crear_category_template(template_data):
    # Crea o actualiza la plantilla
    template, created = CategoryTemplate.objects.get_or_create(
        name=template_data["name"],
        defaults={
            "description": template_data["description"],
            "icon": template_data["icon_path"],
            "evaluation_form": template_data["evaluation_form"]
        }
    )

    if not created:
        template.evaluation_form = template_data["evaluation_form"]
        template.save()

    return template


# Datos del formulario a procesar
templates_data = [
    {
        "name": "Riesgo Domiciliario",
        "description": "Entendemos que nuestras casas varían en forma, tamaño y distribución, pero es importante conocer los espacios que más utiliza para darle consejos pertinentes a su contexto.",
        "icon_path": "health_category/home.png",
        "root_node": {
            "type": "CATEGORY_DESCRIPTION",
            "description": "¡Hola! Antes de recomendarle mejoras en su vivienda, necesitamos conocer su contexto habitacional.",
            "first_button_text": "Comenzar Evaluación",
            "first_button_node_id": 1
        },
        "evaluation_form": {
            "id": 1,
            "question_nodes": [
                {
                    "id": 1,
                    "type": "SINGLE_CHOICE_QUESTION",
                    "question": "¿En qué tipo de vivienda reside actualmente?",
                    "options": ["Casa", "Departamento"],
                    "next_node_id": 2
                },
                {
                    "id": 2,
                    "type": "MULTIPLE_CHOICE_QUESTION",
                    "question": "Seleccione los espacios que más utiliza en su día a día:",
                    "options": [
                        "Cocina",
                        "Living-comedor",
                        "Habitación",
                        "Baño",
                        "Escalera",
                        "Pasillo",
                        "Exterior"
                    ],
                    "next_node_id": 3
                },
                {
                    "id": 3,
                    "type": "SINGLE_CHOICE_QUESTION",
                    "question": "Si vive en departamento, ¿cómo accede a su vivienda?",
                    "options": [
                        "Uso ascensor",
                        "Uso escaleras",
                        "Vivo en planta baja"
                    ],
                    "next_node_id": 4
                }
 
            ]
        }
    },
    {
        "name": "Actividad Física",
        "description": "Evaluación de tu nivel de actividad física",
        "icon_path": "health_category/activity.png",
        "root_node": {
            "type": "CATEGORY_DESCRIPTION",
            "description": "La actividad física es cualquier movimiento corporal producido por los músculos que consume energía. Evaluemos tu nivel actual.",
            "first_button_text": "Comenzar Evaluación",
            "first_button_node_id": 6
        },
        "evaluation_form": {
            "id": 2,
            "question_nodes": [
                # ... más nodos aquí
            ]
        }
    },
    {
        "name": "Alimentación Saludable",
        "description": "Una alimentación saludable es fundamental para mantener un buen estado de salud y prevenir enfermedades. Evaluemos tus hábitos alimenticios actuales.",
        "icon_path": "health_category/nutrition.png",
        "root_node": {
            "type": "CATEGORY_DESCRIPTION",
            "description": "¡Hola! Vamos a evaluar tus hábitos alimenticios para brindarte recomendaciones personalizadas que mejoren tu nutrición diaria.",
            "first_button_text": "Comenzar Evaluación",
            "first_button_node_id": 1
        },
        "evaluation_form": {
            "id": 3,
            "question_nodes": [
                {
                    "id": 1,
                    "type": "MULTIPLE_CHOICE_QUESTION",
                    "question": "¿Cuántas porciones de frutas y verduras consume al día?",
                    "options": [
                        "Ninguna",
                        "1-2 porciones",
                        "3-4 porciones",
                        "5 o más porciones"
                    ],
                    "next_node_id": 2
                },
                {
                    "id": 2,
                    "type": "SINGLE_CHOICE_QUESTION",
                    "question": "¿Con qué frecuencia consume comida rápida o procesada?",
                    "options": [
                        "Todos los días",
                        "3-4 veces por semana",
                        "1-2 veces por semana",
                        "Rara vez o nunca"
                    ],
                    "next_node_id": 3
                },
                {
                    "id": 3,
                    "type": "MULTIPLE_CHOICE_QUESTION",
                    "question": "¿Qué comidas realiza habitualmente?",
                    "options": [
                        "Desayuno",
                        "Colación media mañana",
                        "Almuerzo",
                        "Colación media tarde",
                        "Cena"
                    ],
                    "next_node_id": 4
                },
                {
                    "id": 4,
                    "type": "SCALE_QUESTION",
                    "question": "¿Cuántos vasos de agua consume al día?",
                    "min_value": 0,
                    "max_value": 8,
                    "step": 1,
                    "next_node_id": 5
                },
                {
                    "id": 5,
                    "type": "SINGLE_CHOICE_QUESTION",
                    "question": "¿Sigue alguna dieta específica?",
                    "options": [
                        "No",
                        "Vegetariana",
                        "Vegana",
                        "Sin gluten",
                        "Baja en sodio",
                        "Otra"
                    ],
                    "next_node_id": 6
                }

 
            ]
        }
    }
]

# Procesar la carga de datos
for template_data in templates_data:
    crear_category_template(template_data)

def create_category(name, description, icon):
    # Crear la categoría
    evaluation_form = EvaluationForm.objects.create()
    category = CategoryTemplate.objects.create(
        name=name,
        description=description,
        icon=icon,
        evaluation_form=evaluation_form
    )

    # Crear automáticamente el root node



    # Crear el formulario de evaluación


    # Vincular todo
    category.root_node = root_node
    category.evaluation_form = evaluation_form
    category.save()

    return category, evaluation_form

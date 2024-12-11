
# Importar el modelo
import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
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
    
    # Si la plantilla es nueva, se crean los nodos relacionados
    if created:
        root_node = None
        previous_node = None  # Para enlazar los nodos en secuencia

        # Iterar sobre los nodos del formulario de evaluación
        for node_data in template_data["evaluation_form"]["nodes"]:
            node_type = node_data["type"]

            # Crear el nodo dependiendo del tipo
            if node_type == "CATEGORY_DESCRIPTION":
                node = ActivityNodeDescription.objects.create(
                    type=ActivityNode.NodeType.CATEGORY_DESCRIPTION,
                    description=node_data["description"],
                    first_button_text=node_data.get("first_button_text"),
                    first_button_node_id=node_data.get("first_button_node_id")
                )

            elif node_type == "TEXT_QUESTION":
                node = TextQuestion.objects.create(
                    type=ActivityNode.NodeType.TEXT_QUESTION,
                    question=node_data["question"]
                )

            elif node_type == "SCALE_QUESTION":
                node = ScaleQuestion.objects.create(
                    type=ActivityNode.NodeType.SCALE_QUESTION,
                    question=node_data["question"],
                    min_value=node_data["min_value"],
                    max_value=node_data["max_value"],
                    step=node_data["step"]
                )

            elif node_type == "RESULT_NODE":
                node = ResultNode.objects.create(
                    type=ActivityNode.NodeType.RESULT_NODE,
                    response=node_data["response"]
                )

            # Establecer el siguiente nodo
            if previous_node:
                previous_node.next_node = node
                previous_node.save()

            previous_node = node  # Actualizar el nodo anterior

            # Si es el primer nodo, establece el root_node
            if not root_node:
                root_node = node

        # Después de crear los nodos, asociar el root_node a la plantilla
        template.root_node = root_node
        template.save()

    else:
        # Si la plantilla ya existe, solo actualiza el formulario de evaluación
        template.evaluation_form = template_data["evaluation_form"]
        template.save()
    
    return template


# Datos del formulario a procesar
templates_data = [
    {
        "name": "Physical Health",
        "description": "Monitor and improve your physical health.",
        "icon_path":'health_category/physical_health.png',
        "evaluation_form": {
            "nodes": [
                {
                    "type": "CATEGORY_DESCRIPTION",
                    "description": "Welcome to the physical health survey",
                    "first_button_text": "Start",
                    "first_button_node_id": 2
                },
                {
                    "type": "TEXT_QUESTION",
                    "question": "How do you feel after exercise?"
                },
                {
                    "type": "RESULT_NODE",
                    "response": None
                }
            ]
        }
    },
    {
        "name": "Mental Well-being",
        "description": "Track your mental health and get insights.",
        "icon_path": "health_category/mental_health.png",
        "evaluation_form": {
            "nodes": [
                {
                    "type": "CATEGORY_DESCRIPTION",
                    "description": "Welcome to the mental well-being survey",
                    "first_button_text": "Begin",
                    "first_button_node_id": 2
                },
                {
                    "type": "SCALE_QUESTION",
                    "question": "On a scale of 1 to 10, how stressed are you?",
                    "min_value": 1,
                    "max_value": 10,
                    "step": 1
                },
                {
                    "type": "RESULT_NODE",
                    "response": None
                }
            ]
        }
    }
]

# Procesar la carga de datos
for template_data in templates_data:
    crear_category_template(template_data)
